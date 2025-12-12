"""AI engine for enhanced analysis and correlation."""

from typing import Any, Dict, List, Optional


class AIEngine:
    """Advanced AI engine for vulnerability correlation and analysis."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider = None

    async def initialize(self, provider):
        """Initialize with AI provider."""
        self.provider = provider

    async def correlate_vulnerabilities(
        self,
        vulnerabilities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Correlate vulnerabilities to find attack chains."""
        # Group vulnerabilities by host
        by_host: Dict[str, List[Dict[str, Any]]] = {}

        for vuln in vulnerabilities:
            host = vuln.get("host", "unknown")
            if host not in by_host:
                by_host[host] = []
            by_host[host].append(vuln)

        # Find potential attack chains
        attack_chains = []

        for host, host_vulns in by_host.items():
            # Look for combinations that could be chained
            if len(host_vulns) >= 2:
                chains = self._identify_attack_chains(host_vulns)
                if chains:
                    attack_chains.extend(chains)

        return {
            "attack_chains": attack_chains,
            "high_risk_hosts": self._identify_high_risk_hosts(by_host),
        }

    def _identify_attack_chains(self, vulns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify potential attack chains from multiple vulnerabilities."""
        chains = []

        # Look for specific patterns
        # Example: Remote code execution + privilege escalation
        rce_vulns = [v for v in vulns if "remote" in v.get("description", "").lower() or v.get("cvss_score", 0) >= 9.0]
        privesc_vulns = [v for v in vulns if "privilege" in v.get("description", "").lower()]

        if rce_vulns and privesc_vulns:
            chains.append({
                "type": "rce_to_privesc",
                "description": "Remote Code Execution can be chained with Privilege Escalation",
                "vulnerabilities": [rce_vulns[0].get("cve_id"), privesc_vulns[0].get("cve_id")],
                "risk": "critical",
            })

        return chains

    def _identify_high_risk_hosts(self, by_host: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Identify hosts with multiple high-severity vulnerabilities."""
        high_risk = []

        for host, vulns in by_host.items():
            critical_count = len([v for v in vulns if v.get("risk_level") == "critical"])
            high_count = len([v for v in vulns if v.get("risk_level") == "high"])

            if critical_count >= 2 or (critical_count >= 1 and high_count >= 2):
                high_risk.append({
                    "host": host,
                    "critical_vulns": critical_count,
                    "high_vulns": high_count,
                    "total_vulns": len(vulns),
                    "risk_assessment": "Multiple critical vulnerabilities create high risk of compromise",
                })

        return high_risk
