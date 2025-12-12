"""EPSS (Exploit Prediction Scoring System) enricher plugin."""

import asyncio
from typing import Any, Dict, List, Optional
import aiohttp
from datetime import datetime

from nmapai.core.base_plugin import EnricherPlugin, PluginStatus


class EPSSEnricher(EnricherPlugin):
    """Enrich vulnerabilities with EPSS scores (exploit probability)."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.endpoint = "https://api.first.org/data/v1/epss"
        self.cache: Dict[str, Dict[str, Any]] = {}

    @property
    def name(self) -> str:
        return "epss_enricher"

    @property
    def version(self) -> str:
        return "2.0.0"

    async def validate(self) -> bool:
        """Validate EPSS API is accessible."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.endpoint,
                    params={"cve": "CVE-2021-44228"},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    return response.status == 200
        except Exception as e:
            self.error = f"EPSS API not accessible: {e}"
            return False

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute EPSS enrichment."""
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
                "enriched_vulns": len([v for v in enriched if v.get("epss_score")]),
            }

            return self.results

        except Exception as e:
            self.status = PluginStatus.FAILED
            self.error = str(e)
            raise

    async def enrich(self, vulnerabilities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enrich vulnerabilities with EPSS data."""
        # Extract CVE IDs
        cve_ids = [v.get("cve_id") or v.get("id") for v in vulnerabilities]
        cve_ids = [cve for cve in cve_ids if cve and cve.startswith("CVE-")]

        if not cve_ids:
            return vulnerabilities

        # Batch fetch EPSS scores (API supports multiple CVEs)
        epss_data = await self._fetch_epss_batch(cve_ids)

        # Enrich vulnerabilities
        for vuln in vulnerabilities:
            cve_id = vuln.get("cve_id") or vuln.get("id")
            if cve_id and cve_id in epss_data:
                epss_info = epss_data[cve_id]
                vuln["epss_score"] = epss_info.get("epss")
                vuln["epss_percentile"] = epss_info.get("percentile")
                vuln["epss_date"] = epss_info.get("date")

        return vulnerabilities

    async def _fetch_epss_batch(self, cve_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Fetch EPSS scores for multiple CVEs."""
        # EPSS API accepts multiple CVEs comma-separated
        batch_size = 30  # Limit batch size
        all_data = {}

        for i in range(0, len(cve_ids), batch_size):
            batch = cve_ids[i:i + batch_size]
            cves_param = ",".join(batch)

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        self.endpoint,
                        params={"cve": cves_param},
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        if response.status != 200:
                            continue

                        data = await response.json()
                        scores = data.get("data", [])

                        for score in scores:
                            cve_id = score.get("cve")
                            if cve_id:
                                all_data[cve_id] = {
                                    "epss": float(score.get("epss", 0)),
                                    "percentile": float(score.get("percentile", 0)),
                                    "date": score.get("date"),
                                }

                # Rate limiting
                await asyncio.sleep(0.5)

            except Exception as e:
                print(f"Warning: Failed to fetch EPSS for batch: {e}")
                continue

        return all_data
