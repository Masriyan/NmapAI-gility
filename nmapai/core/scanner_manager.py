"""Scanner manager for orchestrating all scanning operations."""

import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from nmapai.core.base_plugin import BasePlugin, PluginStatus
from nmapai.plugins.scanners.nmap_scanner import NmapScanner
from nmapai.plugins.scanners.nikto_scanner import NiktoScanner
from nmapai.plugins.ai_providers.openai_provider import OpenAIProvider
from nmapai.plugins.ai_providers.anthropic_provider import AnthropicProvider
from nmapai.plugins.ai_providers.ollama_provider import OllamaProvider
from nmapai.plugins.enrichers.nvd_enricher import NVDEnricher
from nmapai.plugins.enrichers.epss_enricher import EPSSEnricher
from nmapai.plugins.enrichers.exploitdb_enricher import ExploitDBEnricher
from nmapai.core.vulnerability_engine import VulnerabilityEngine


class ScannerManager:
    """Manages and orchestrates all scanning operations."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.plugins: List[BasePlugin] = []
        self.results: Dict[str, Any] = {}
        self.vuln_engine = VulnerabilityEngine(config.get("vulnerability_engine", {}))

    async def initialize(self):
        """Initialize all plugins based on configuration."""
        # Initialize scanners
        if self.config.get("nmap", {}).get("enabled", True):
            self.plugins.append(NmapScanner(self.config.get("nmap", {})))

        if self.config.get("nikto", {}).get("enabled", True):
            self.plugins.append(NiktoScanner(self.config.get("nikto", {})))

        # Initialize AI providers
        ai_config = self.config.get("ai", {})
        if ai_config.get("enabled"):
            provider_type = ai_config.get("provider", "openai")

            if provider_type == "openai":
                self.plugins.append(OpenAIProvider(ai_config))
            elif provider_type == "anthropic":
                self.plugins.append(AnthropicProvider(ai_config))
            elif provider_type == "ollama":
                self.plugins.append(OllamaProvider(ai_config))

        # Initialize enrichers
        if self.config.get("enrichers", {}).get("nvd", {}).get("enabled", True):
            self.plugins.append(NVDEnricher(self.config.get("enrichers", {}).get("nvd", {})))

        if self.config.get("enrichers", {}).get("epss", {}).get("enabled", True):
            self.plugins.append(EPSSEnricher(self.config.get("enrichers", {}).get("epss", {})))

        if self.config.get("enrichers", {}).get("exploitdb", {}).get("enabled", True):
            self.plugins.append(ExploitDBEnricher(self.config.get("enrichers", {}).get("exploitdb", {})))

        # Validate all plugins
        for plugin in self.plugins:
            is_valid = await plugin.validate()
            if not is_valid:
                print(f"Warning: Plugin {plugin.name} validation failed: {plugin.error}")

    async def run_scan(self, targets: List[str], output_dir: Path) -> Dict[str, Any]:
        """Run complete scan workflow."""
        print(f"[*] Starting scan of {len(targets)} targets...")
        print(f"[*] Output directory: {output_dir}")

        context = {
            "targets": targets,
            "output_dir": str(output_dir),
            "scan_params": self.config.get("nmap", {}),
            "start_time": datetime.now(),
        }

        # Phase 1: Nmap Scan
        nmap_results = await self._run_nmap(context)
        context["nmap_results"] = nmap_results

        # Phase 2: Nikto Scan (if enabled)
        nikto_results = await self._run_nikto(context)
        context["nikto_results"] = nikto_results

        # Phase 3: Extract vulnerabilities
        vulnerabilities = self._extract_vulnerabilities(context)
        context["vulnerabilities"] = vulnerabilities

        # Phase 4: Enrich vulnerabilities
        enriched_vulns = await self._enrich_vulnerabilities(context)
        context["vulnerabilities"] = enriched_vulns

        # Phase 5: Score and prioritize
        scored_vulns = self.vuln_engine.analyze_vulnerabilities(enriched_vulns, context)
        context["scored_vulnerabilities"] = scored_vulns

        # Phase 6: Generate recommendations
        recommendations = self.vuln_engine.generate_recommendations(scored_vulns)
        context["recommendations"] = recommendations

        # Phase 7: AI Analysis (if enabled)
        ai_analysis = await self._run_ai_analysis(context)
        context["ai_analysis"] = ai_analysis

        # Final results
        context["end_time"] = datetime.now()
        context["duration"] = (context["end_time"] - context["start_time"]).total_seconds()

        self.results = context
        return context

    async def _run_nmap(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run Nmap scanner."""
        print("\n[*] Phase 1: Nmap Scanning")

        nmap_plugin = next((p for p in self.plugins if p.name == "nmap_scanner"), None)
        if not nmap_plugin:
            print("[!] Nmap scanner not available")
            return {}

        try:
            results = await nmap_plugin.execute(context)
            print(f"[✓] Nmap scan completed - {len(results.get('hosts', []))} hosts discovered")
            return results
        except Exception as e:
            print(f"[✗] Nmap scan failed: {e}")
            return {}

    async def _run_nikto(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run Nikto scanner."""
        print("\n[*] Phase 2: Nikto Web Scanning")

        nikto_plugin = next((p for p in self.plugins if p.name == "nikto_scanner"), None)
        if not nikto_plugin:
            print("[!] Nikto scanner not available")
            return {}

        try:
            results = await nikto_plugin.execute(context)
            if results.get("scans"):
                print(f"[✓] Nikto scan completed - {results.get('total', 0)} targets scanned")
            else:
                print("[!] No web services to scan")
            return results
        except Exception as e:
            print(f"[✗] Nikto scan failed: {e}")
            return {}

    def _extract_vulnerabilities(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract vulnerabilities from scan results."""
        print("\n[*] Phase 3: Extracting Vulnerabilities")

        vulnerabilities = []

        # Extract from Nmap scripts
        hosts = context.get("nmap_results", {}).get("hosts", [])
        for host in hosts:
            for port in host.get("ports", []):
                for script in port.get("scripts", []):
                    if "cve" in script.get("id", "").lower() or "vuln" in script.get("id", "").lower():
                        # Parse CVE IDs from script output
                        import re
                        cve_pattern = r"CVE-\d{4}-\d+"
                        cves = re.findall(cve_pattern, script.get("output", ""))

                        for cve in cves:
                            vulnerabilities.append({
                                "cve_id": cve,
                                "host": host.get("ip"),
                                "port": port.get("port"),
                                "service": port.get("service", {}).get("name", ""),
                                "source": "nmap_script",
                            })

        # Extract from Nikto
        nikto_scans = context.get("nikto_results", {}).get("scans", [])
        for scan in nikto_scans:
            for finding in scan.get("findings", []):
                # Look for CVE mentions
                import re
                cve_pattern = r"CVE-\d{4}-\d+"
                cves = re.findall(cve_pattern, finding.get("description", ""))

                for cve in cves:
                    vulnerabilities.append({
                        "cve_id": cve,
                        "host": scan.get("target", {}).get("host"),
                        "port": scan.get("target", {}).get("port"),
                        "service": "http",
                        "source": "nikto",
                        "description": finding.get("description", "")[:200],
                    })

        # Deduplicate by CVE ID + host
        seen = set()
        unique_vulns = []
        for vuln in vulnerabilities:
            key = (vuln.get("cve_id"), vuln.get("host"))
            if key not in seen:
                seen.add(key)
                unique_vulns.append(vuln)

        print(f"[✓] Extracted {len(unique_vulns)} unique vulnerabilities")
        return unique_vulns

    async def _enrich_vulnerabilities(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enrich vulnerabilities with external data."""
        print("\n[*] Phase 4: Enriching Vulnerabilities")

        vulnerabilities = context.get("vulnerabilities", [])

        if not vulnerabilities:
            print("[!] No vulnerabilities to enrich")
            return []

        # Run all enrichers
        for plugin in self.plugins:
            if plugin.name.endswith("_enricher"):
                try:
                    print(f"  - Running {plugin.name}...")
                    result = await plugin.execute({"vulnerabilities": vulnerabilities})
                    vulnerabilities = result.get("vulnerabilities", vulnerabilities)
                except Exception as e:
                    print(f"  [!] {plugin.name} failed: {e}")

        print(f"[✓] Vulnerability enrichment completed")
        return vulnerabilities

    async def _run_ai_analysis(self, context: Dict[str, Any]) -> Optional[str]:
        """Run AI analysis."""
        print("\n[*] Phase 7: AI Analysis")

        ai_plugin = next((p for p in self.plugins if "provider" in p.name), None)
        if not ai_plugin:
            print("[!] AI provider not configured")
            return None

        try:
            context_for_ai = {
                "scan_data": context,
                "prompt": self.config.get("ai", {}).get("prompt"),
            }

            result = await ai_plugin.execute(context_for_ai)
            analysis = result.get("analysis", "")
            print(f"[✓] AI analysis completed ({len(analysis)} characters)")
            return analysis
        except Exception as e:
            print(f"[✗] AI analysis failed: {e}")
            return None
