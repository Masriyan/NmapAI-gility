"""NVD (National Vulnerability Database) enricher plugin."""

import asyncio
import time
from typing import Any, Dict, List, Optional
import aiohttp
from datetime import datetime, timedelta

from nmapai.core.base_plugin import EnricherPlugin, PluginStatus


class NVDEnricher(EnricherPlugin):
    """Enrich vulnerabilities with NVD data (CVSS scores, descriptions, etc)."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.api_key = config.get("api_key") if config else None
        self.endpoint = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.rate_limit_delay = 0.6 if not self.api_key else 0.1  # 6s between requests (no key) or 10/sec (with key)

    @property
    def name(self) -> str:
        return "nvd_enricher"

    @property
    def version(self) -> str:
        return "2.0.0"

    async def validate(self) -> bool:
        """Validate NVD API is accessible."""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {}
                if self.api_key:
                    headers["apiKey"] = self.api_key

                async with session.get(
                    self.endpoint,
                    params={"cveId": "CVE-2021-44228"},  # Test with Log4j
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    return response.status in [200, 404]  # 404 is OK, means API is working
        except Exception as e:
            self.error = f"NVD API not accessible: {e}"
            return False

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute vulnerability enrichment."""
        self.status = PluginStatus.RUNNING

        try:
            vulnerabilities = context.get("vulnerabilities", [])

            if not vulnerabilities:
                self.status = PluginStatus.SKIPPED
                return {"vulnerabilities": []}

            enriched = await self.enrich(vulnerabilities)

            self.status = PluginStatus.COMPLETED
            self.results = {"vulnerabilities": enriched}
            self.metrics = {
                "total_vulns": len(vulnerabilities),
                "enriched_vulns": len([v for v in enriched if v.get("nvd_data")]),
            }

            return self.results

        except Exception as e:
            self.status = PluginStatus.FAILED
            self.error = str(e)
            raise

    async def enrich(self, vulnerabilities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enrich vulnerabilities with NVD data."""
        enriched = []

        for vuln in vulnerabilities:
            cve_id = vuln.get("cve_id") or vuln.get("id")

            if not cve_id or not cve_id.startswith("CVE-"):
                enriched.append(vuln)
                continue

            # Check cache first
            if cve_id in self.cache:
                vuln["nvd_data"] = self.cache[cve_id]
                enriched.append(vuln)
                continue

            # Fetch from NVD
            try:
                nvd_data = await self._fetch_cve(cve_id)
                if nvd_data:
                    self.cache[cve_id] = nvd_data
                    vuln["nvd_data"] = nvd_data

                    # Add computed fields
                    vuln["cvss_score"] = nvd_data.get("cvss_score")
                    vuln["severity"] = nvd_data.get("severity")
                    vuln["description"] = nvd_data.get("description")

                enriched.append(vuln)

                # Rate limiting
                await asyncio.sleep(self.rate_limit_delay)

            except Exception as e:
                print(f"Warning: Failed to enrich {cve_id}: {e}")
                enriched.append(vuln)

        return enriched

    async def _fetch_cve(self, cve_id: str) -> Optional[Dict[str, Any]]:
        """Fetch CVE data from NVD."""
        headers = {}
        if self.api_key:
            headers["apiKey"] = self.api_key

        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.endpoint,
                params={"cveId": cve_id},
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status != 200:
                    return None

                data = await response.json()
                vulnerabilities = data.get("vulnerabilities", [])

                if not vulnerabilities:
                    return None

                cve_item = vulnerabilities[0].get("cve", {})

                # Extract CVSS data
                cvss_data = self._extract_cvss(cve_item)

                # Extract description
                descriptions = cve_item.get("descriptions", [])
                description = next(
                    (d.get("value") for d in descriptions if d.get("lang") == "en"),
                    descriptions[0].get("value") if descriptions else ""
                )

                # Extract references
                references = [
                    {
                        "url": ref.get("url"),
                        "source": ref.get("source"),
                    }
                    for ref in cve_item.get("references", [])[:5]
                ]

                # Extract published/modified dates
                published = cve_item.get("published", "")
                modified = cve_item.get("lastModified", "")

                return {
                    "cve_id": cve_id,
                    "description": description,
                    "cvss_score": cvss_data.get("score"),
                    "cvss_vector": cvss_data.get("vector"),
                    "severity": cvss_data.get("severity"),
                    "references": references,
                    "published": published,
                    "modified": modified,
                }

    def _extract_cvss(self, cve_item: Dict[str, Any]) -> Dict[str, Any]:
        """Extract CVSS score and severity."""
        metrics = cve_item.get("metrics", {})

        # Try CVSS v3.1 first, then v3.0, then v2
        for version in ["cvssMetricV31", "cvssMetricV30", "cvssMetricV2"]:
            metric_list = metrics.get(version, [])
            if metric_list:
                metric = metric_list[0]
                cvss_data = metric.get("cvssData", {})

                return {
                    "score": cvss_data.get("baseScore"),
                    "vector": cvss_data.get("vectorString"),
                    "severity": cvss_data.get("baseSeverity") or metric.get("baseSeverity"),
                    "version": version.replace("cvssMetricV", "v"),
                }

        return {"score": None, "vector": None, "severity": "UNKNOWN", "version": None}
