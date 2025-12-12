"""Enhanced Nikto scanner plugin with intelligent targeting."""

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import time
import re

from nmapai.core.base_plugin import ScannerPlugin, PluginStatus


class NiktoScanner(ScannerPlugin):
    """Advanced Nikto scanner for web vulnerability assessment."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.concurrency = config.get("concurrency", 2) if config else 2
        self.progress_callback = None

    @property
    def name(self) -> str:
        return "nikto_scanner"

    @property
    def version(self) -> str:
        return "2.0.0"

    async def validate(self) -> bool:
        """Validate Nikto is available."""
        try:
            proc = await asyncio.create_subprocess_exec(
                "nikto", "-Version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            return proc.returncode == 0 or b"Nikto" in stdout
        except FileNotFoundError:
            self.error = "Nikto not found in PATH"
            return False

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Nikto scans on HTTP services."""
        self.status = PluginStatus.RUNNING
        start_time = time.time()

        try:
            hosts = context.get("nmap_results", {}).get("hosts", [])
            output_dir = Path(context.get("output_dir", ".")) / "nikto"
            output_dir.mkdir(parents=True, exist_ok=True)

            # Extract HTTP/HTTPS targets
            targets = self._extract_web_targets(hosts)

            if not targets:
                self.status = PluginStatus.SKIPPED
                return {"message": "No HTTP/HTTPS services detected"}

            # Run scans
            results = await self.scan(targets, {"output_dir": str(output_dir)})

            self.status = PluginStatus.COMPLETED
            self.results = results
            self.metrics = {
                "duration": time.time() - start_time,
                "targets_scanned": len(targets),
                "vulnerabilities_found": sum(len(r.get("findings", [])) for r in results.get("scans", [])),
            }

            return results

        except Exception as e:
            self.status = PluginStatus.FAILED
            self.error = str(e)
            raise

    def _extract_web_targets(self, hosts: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Extract HTTP/HTTPS targets from host data."""
        targets = []
        web_ports = {"80", "443", "8000", "8001", "8080", "8443", "8888", "5000", "3000", "9000"}

        for host in hosts:
            ip = host.get("ip")
            for port in host.get("ports", []):
                port_num = str(port.get("port"))
                service = port.get("service", {}).get("name", "").lower()

                # Check if it's a web service
                is_web = "http" in service or port_num in web_ports

                if is_web:
                    # Determine scheme
                    is_ssl = "https" in service or "ssl" in service or port_num in {"443", "8443"}
                    scheme = "https" if is_ssl else "http"

                    targets.append({
                        "host": ip,
                        "port": port_num,
                        "scheme": scheme,
                        "url": f"{scheme}://{ip}:{port_num}",
                    })

        # Deduplicate
        seen = set()
        unique_targets = []
        for t in targets:
            key = (t["host"], t["port"], t["scheme"])
            if key not in seen:
                seen.add(key)
                unique_targets.append(t)

        return unique_targets

    async def scan(self, targets: List[Dict[str, str]], params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Nikto scans on all targets."""
        output_dir = Path(params.get("output_dir", "."))
        sem = asyncio.Semaphore(self.concurrency)

        tasks = [
            self._scan_single(sem, target, output_dir, idx, len(targets))
            for idx, target in enumerate(targets)
        ]

        scan_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        successful_scans = [r for r in scan_results if not isinstance(r, Exception)]
        failed_scans = [r for r in scan_results if isinstance(r, Exception)]

        return {
            "scans": successful_scans,
            "total": len(targets),
            "successful": len(successful_scans),
            "failed": len(failed_scans),
        }

    async def _scan_single(
        self,
        sem: asyncio.Semaphore,
        target: Dict[str, str],
        output_dir: Path,
        idx: int,
        total: int,
    ) -> Dict[str, Any]:
        """Scan a single target."""
        async with sem:
            url = target["url"]
            host = target["host"]
            port = target["port"]

            # Output files
            out_html = output_dir / f"{host}_{port}.html"
            out_json = output_dir / f"{host}_{port}.json"

            cmd = [
                "nikto",
                "-h", url,
                "-o", str(out_html),
                "-Format", "htm",
                "-nointeractive",
            ]

            try:
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

                stdout, stderr = await proc.communicate()

                # Parse output
                findings = self._parse_nikto_output(stdout.decode(errors="ignore"))

                # Save JSON
                result = {
                    "target": target,
                    "findings": findings,
                    "output_files": {
                        "html": str(out_html),
                        "json": str(out_json),
                    },
                }

                # Write JSON
                out_json.write_text(json.dumps(result, indent=2))

                # Update progress
                if self.progress_callback:
                    await self.progress_callback("nikto", (idx + 1) / total * 100)

                return result

            except Exception as e:
                return {
                    "target": target,
                    "error": str(e),
                    "findings": [],
                }

    def _parse_nikto_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse Nikto output for findings."""
        findings = []

        # Look for vulnerability patterns
        vuln_pattern = re.compile(r'\+\s+([^:]+):\s+(.+)')

        for line in output.split('\n'):
            match = vuln_pattern.search(line)
            if match:
                finding_type = match.group(1).strip()
                description = match.group(2).strip()

                # Assess severity based on keywords
                severity = "info"
                if any(keyword in description.lower() for keyword in ["critical", "dangerous", "exploit"]):
                    severity = "high"
                elif any(keyword in description.lower() for keyword in ["vulnerable", "security", "risk"]):
                    severity = "medium"
                elif any(keyword in description.lower() for keyword in ["warning", "outdated"]):
                    severity = "low"

                findings.append({
                    "type": finding_type,
                    "description": description,
                    "severity": severity,
                })

        return findings

    async def parse_results(self, raw_output: str) -> Dict[str, Any]:
        """Parse raw Nikto output."""
        return {"findings": self._parse_nikto_output(raw_output)}

    def set_progress_callback(self, callback):
        """Set callback for progress updates."""
        self.progress_callback = callback
