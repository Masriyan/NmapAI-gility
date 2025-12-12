"""Enhanced Nmap scanner plugin with adaptive capabilities."""

import asyncio
import re
import shlex
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import time

from nmapai.core.base_plugin import ScannerPlugin, PluginStatus, PluginPriority


class NmapScanner(ScannerPlugin):
    """Advanced Nmap scanner with intelligent adaptation."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.scan_id = None
        self.targets_scanned = 0
        self.total_targets = 0
        self.progress_callback = None
        self.adaptive_mode = config.get("adaptive_mode", False) if config else False

    @property
    def name(self) -> str:
        return "nmap_scanner"

    @property
    def version(self) -> str:
        return "2.0.0"

    @property
    def priority(self) -> PluginPriority:
        return PluginPriority.CRITICAL

    async def validate(self) -> bool:
        """Validate Nmap is available."""
        try:
            proc = await asyncio.create_subprocess_exec(
                "nmap", "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            return proc.returncode == 0 and b"Nmap" in stdout
        except FileNotFoundError:
            self.error = "Nmap not found in PATH"
            return False

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Nmap scan."""
        self.status = PluginStatus.RUNNING
        start_time = time.time()

        try:
            targets = context.get("targets", [])
            params = context.get("scan_params", {})
            output_dir = Path(context.get("output_dir", "."))

            results = await self.scan(targets, params)

            self.status = PluginStatus.COMPLETED
            self.results = results
            self.metrics = {
                "duration": time.time() - start_time,
                "targets_scanned": len(targets),
                "hosts_up": len(results.get("hosts", [])),
                "total_ports": sum(len(h.get("ports", [])) for h in results.get("hosts", [])),
            }

            return results

        except Exception as e:
            self.status = PluginStatus.FAILED
            self.error = str(e)
            raise

    async def scan(self, targets: List[str], params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Nmap scan with progress tracking."""
        output_dir = Path(params.get("output_dir", "."))
        nmap_params = params.get("nmap_params", "-sV")
        dursvuln_config = params.get("dursvuln", {})

        # Create output files
        out_normal = output_dir / "nmap_results.nmap"
        out_grep = output_dir / "nmap_results.gnmap"
        out_xml = output_dir / "nmap_results.xml"

        # Build command
        cmd = self._build_command(targets, nmap_params, dursvuln_config, out_normal, out_grep, out_xml)

        # Execute scan
        hosts_data = await self._execute_scan(cmd, output_dir)

        # Parse XML output for structured data
        structured_data = await self._parse_xml(out_xml)

        # Adaptive rescan if enabled
        if self.adaptive_mode:
            structured_data = await self._adaptive_rescan(structured_data, params)

        return {
            "hosts": structured_data,
            "raw_files": {
                "nmap": str(out_normal),
                "gnmap": str(out_grep),
                "xml": str(out_xml),
            },
            "scan_stats": hosts_data.get("stats", {}),
        }

    def _build_command(
        self,
        targets: List[str],
        nmap_params: str,
        dursvuln_config: Dict[str, Any],
        out_normal: Path,
        out_grep: Path,
        out_xml: Path,
    ) -> List[str]:
        """Build Nmap command with all options."""
        # Create targets temp file
        targets_file = out_normal.parent / "targets_temp.txt"
        targets_file.write_text("\n".join(targets))

        cmd = ["nmap", "-iL", str(targets_file)]
        cmd += shlex.split(nmap_params.replace("—", "--").replace("–", "--"))
        cmd += ["--stats-every", "2s", "-oN", str(out_normal), "-oG", str(out_grep), "-oX", str(out_xml), "-v"]

        # DursVuln integration
        if dursvuln_config.get("enabled"):
            if dursvuln_config.get("use_global"):
                cmd += ["--script", "dursvuln"]
            elif dursvuln_config.get("script_path"):
                cmd += ["--script", str(dursvuln_config["script_path"])]

            script_args = []
            if dursvuln_config.get("db_path"):
                script_args.append(f"db_path={dursvuln_config['db_path']}")
            if dursvuln_config.get("min_severity"):
                script_args.append(f"min_severity={dursvuln_config['min_severity']}")
            if dursvuln_config.get("output_mode"):
                script_args.append(f"dursvuln.output={dursvuln_config['output_mode']}")

            if script_args:
                cmd += ["--script-args", ",".join(script_args)]

        return cmd

    async def _execute_scan(self, cmd: List[str], output_dir: Path) -> Dict[str, Any]:
        """Execute Nmap command with progress tracking."""
        prog_re = re.compile(r"About\s+([0-9]+(?:\.[0-9]+)?)%\s+done")
        etc_re = re.compile(r"ETC:\s*([^\r\n]+)")

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        hosts_found = []
        scan_stats = {}

        async def read_stream(stream):
            while True:
                line = await stream.readline()
                if not line:
                    break
                s = line.decode(errors="ignore")

                # Extract progress
                m = prog_re.search(s)
                if m:
                    pct = float(m.group(1))
                    if self.progress_callback:
                        await self.progress_callback("nmap", pct)

                # Extract hosts
                if "Nmap scan report for" in s:
                    host = s.split("Nmap scan report for")[1].strip()
                    hosts_found.append(host)

        await asyncio.gather(read_stream(proc.stdout), read_stream(proc.stderr))
        await proc.wait()

        return {"hosts": hosts_found, "stats": scan_stats}

    async def _parse_xml(self, xml_path: Path) -> List[Dict[str, Any]]:
        """Parse Nmap XML output into structured data."""
        if not xml_path.exists():
            return []

        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            hosts = []

            for host_elem in root.findall(".//host"):
                if host_elem.find("status").get("state") != "up":
                    continue

                host_data = self._parse_host(host_elem)
                if host_data:
                    hosts.append(host_data)

            return hosts

        except Exception as e:
            print(f"Warning: Failed to parse XML: {e}")
            return []

    def _parse_host(self, host_elem) -> Optional[Dict[str, Any]]:
        """Parse single host element."""
        # Extract address
        addr_elem = host_elem.find("address[@addrtype='ipv4']")
        if addr_elem is None:
            addr_elem = host_elem.find("address[@addrtype='ipv6']")
        if addr_elem is None:
            return None

        ip = addr_elem.get("addr")

        # Extract hostname
        hostname = None
        hostnames_elem = host_elem.find("hostnames/hostname[@type='user']")
        if hostnames_elem is not None:
            hostname = hostnames_elem.get("name")

        # Extract ports
        ports = []
        for port_elem in host_elem.findall(".//port"):
            state_elem = port_elem.find("state")
            if state_elem is None or state_elem.get("state") != "open":
                continue

            port_data = {
                "port": int(port_elem.get("portid")),
                "protocol": port_elem.get("protocol"),
                "state": state_elem.get("state"),
            }

            # Service info
            service_elem = port_elem.find("service")
            if service_elem is not None:
                port_data["service"] = {
                    "name": service_elem.get("name", "unknown"),
                    "product": service_elem.get("product"),
                    "version": service_elem.get("version"),
                    "extrainfo": service_elem.get("extrainfo"),
                }

            # Script results (including DursVuln)
            scripts = []
            for script_elem in port_elem.findall("script"):
                scripts.append({
                    "id": script_elem.get("id"),
                    "output": script_elem.get("output"),
                })
            if scripts:
                port_data["scripts"] = scripts

            ports.append(port_data)

        # Extract OS detection
        os_info = None
        os_elem = host_elem.find(".//osmatch")
        if os_elem is not None:
            os_info = {
                "name": os_elem.get("name"),
                "accuracy": int(os_elem.get("accuracy", 0)),
            }

        return {
            "ip": ip,
            "hostname": hostname,
            "ports": ports,
            "os": os_info,
            "state": "up",
        }

    async def _adaptive_rescan(
        self, hosts: List[Dict[str, Any]], params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Perform adaptive rescanning based on initial results."""
        # Identify hosts with interesting services that need deeper scanning
        targets_for_deep_scan = []

        for host in hosts:
            for port in host.get("ports", []):
                service = port.get("service", {}).get("name", "")
                # Look for interesting services
                if service in ["http", "https", "ssh", "ftp", "mysql", "postgresql", "smb"]:
                    if host["ip"] not in targets_for_deep_scan:
                        targets_for_deep_scan.append(host["ip"])
                        break

        if targets_for_deep_scan:
            # Perform targeted deep scan
            deep_params = params.copy()
            deep_params["nmap_params"] = "-sV -sC --script=vuln -A"

            # Run deep scan on selected targets
            # (Implementation would recursively call scan with adjusted params)
            pass

        return hosts

    async def parse_results(self, raw_output: str) -> Dict[str, Any]:
        """Parse raw Nmap output."""
        # This is handled by _parse_xml in our implementation
        return {}

    def set_progress_callback(self, callback):
        """Set callback for progress updates."""
        self.progress_callback = callback
