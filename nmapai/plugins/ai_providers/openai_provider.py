"""OpenAI/Compatible API provider for AI analysis."""

import asyncio
import json
import os
from typing import Any, Dict, Optional, AsyncIterator
import aiohttp

from nmapai.core.base_plugin import AIProviderPlugin, PluginStatus


class OpenAIProvider(AIProviderPlugin):
    """OpenAI and compatible API provider (supports OpenAI, Azure, local APIs)."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.api_key = config.get("api_key") or os.environ.get("OPENAI_API_KEY", "") if config else ""
        self.endpoint = config.get("endpoint", "https://api.openai.com/v1/chat/completions") if config else "https://api.openai.com/v1/chat/completions"
        self.model = config.get("model", "gpt-4o-mini") if config else "gpt-4o-mini"
        self.max_tokens = config.get("max_tokens", 2000) if config else 2000
        self.temperature = config.get("temperature", 0.2) if config else 0.2
        self.timeout = config.get("timeout", 120) if config else 120

    @property
    def name(self) -> str:
        return "openai_provider"

    @property
    def version(self) -> str:
        return "2.0.0"

    @property
    def supports_streaming(self) -> bool:
        return True

    async def validate(self) -> bool:
        """Validate API key is available."""
        if not self.api_key:
            self.error = "OpenAI API key not set"
            return False
        return True

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute AI analysis."""
        self.status = PluginStatus.RUNNING

        try:
            scan_data = context.get("scan_data", {})
            prompt = context.get("prompt", self._default_prompt())

            analysis = await self.analyze(scan_data, prompt)

            self.status = PluginStatus.COMPLETED
            self.results = {"analysis": analysis}
            return self.results

        except Exception as e:
            self.status = PluginStatus.FAILED
            self.error = str(e)
            raise

    async def analyze(self, data: Dict[str, Any], prompt: str) -> str:
        """Analyze data using OpenAI API."""
        # Prepare context from scan data
        context = self._prepare_context(data)

        messages = [
            {
                "role": "system",
                "content": "You are an expert security analyst specializing in penetration testing and vulnerability assessment. Analyze scan results and provide actionable security insights."
            },
            {
                "role": "user",
                "content": f"{prompt}\n\n{context}"
            }
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.endpoint,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"API error {response.status}: {error_text}")

                result = await response.json()
                return result["choices"][0]["message"]["content"]

    async def stream_analyze(self, data: Dict[str, Any], prompt: str) -> AsyncIterator[str]:
        """Stream analysis results in real-time."""
        context = self._prepare_context(data)

        messages = [
            {
                "role": "system",
                "content": "You are an expert security analyst. Provide concise, actionable security insights."
            },
            {
                "role": "user",
                "content": f"{prompt}\n\n{context}"
            }
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": True,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.endpoint,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"API error {response.status}: {error_text}")

                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        data_str = line[6:]
                        if data_str == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data_str)
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue

    def _prepare_context(self, data: Dict[str, Any]) -> str:
        """Prepare context from scan data."""
        lines = []

        # Nmap results
        hosts = data.get("nmap_results", {}).get("hosts", [])
        if hosts:
            lines.append("=== NMAP SCAN RESULTS ===\n")
            for host in hosts:
                lines.append(f"\nHost: {host.get('ip')} ({host.get('hostname', 'N/A')})")
                lines.append(f"State: {host.get('state')}")

                if host.get('os'):
                    lines.append(f"OS: {host['os'].get('name')} (accuracy: {host['os'].get('accuracy')}%)")

                if host.get('ports'):
                    lines.append("\nOpen Ports:")
                    for port in host['ports']:
                        service = port.get('service', {})
                        lines.append(
                            f"  - {port['port']}/{port['protocol']}: "
                            f"{service.get('name', 'unknown')} "
                            f"({service.get('product', '')} {service.get('version', '')})"
                        )

                        # Include script results
                        if port.get('scripts'):
                            for script in port['scripts']:
                                lines.append(f"    Script ({script['id']}): {script['output'][:200]}")

        # Nikto results
        nikto_results = data.get("nikto_results", {})
        if nikto_results.get("scans"):
            lines.append("\n\n=== NIKTO WEB SCAN RESULTS ===\n")
            for scan in nikto_results["scans"]:
                target = scan.get("target", {})
                lines.append(f"\nTarget: {target.get('url')}")
                findings = scan.get("findings", [])
                if findings:
                    lines.append(f"Findings ({len(findings)}):")
                    for finding in findings[:10]:  # Limit to top 10
                        lines.append(f"  - [{finding['severity'].upper()}] {finding['description'][:150]}")

        # DursVuln results
        dursvuln_data = data.get("dursvuln_results", {})
        if dursvuln_data:
            lines.append("\n\n=== DURSVULN CVE FINDINGS ===\n")
            lines.append(str(dursvuln_data)[:1000])

        # Enriched vulnerabilities
        vulns = data.get("vulnerabilities", [])
        if vulns:
            lines.append("\n\n=== ENRICHED VULNERABILITIES ===\n")
            for vuln in vulns[:15]:  # Top 15
                lines.append(f"\n{vuln.get('cve_id', 'N/A')}: {vuln.get('description', '')[:150]}")
                lines.append(f"  CVSS: {vuln.get('cvss_score', 'N/A')} | Severity: {vuln.get('severity', 'N/A')}")
                if vuln.get('epss_score'):
                    lines.append(f"  EPSS: {vuln.get('epss_score')} (Exploit Probability)")

        return "\n".join(lines)

    def _default_prompt(self) -> str:
        """Default analysis prompt."""
        return """Analyze these security scan results and provide:

1. **Executive Summary**: Brief overview of security posture
2. **Critical Findings**: Most severe vulnerabilities requiring immediate attention
3. **Attack Surface**: Key exposed services and potential entry points
4. **Risk Assessment**: Overall risk level and key concerns
5. **Prioritized Remediation**: Top 5-7 actionable recommendations, ordered by priority
6. **CVE Analysis**: Notable CVEs with exploitation likelihood
7. **Quick Wins**: Easy fixes for immediate security improvement

Format in clear, concise Markdown. Be specific and actionable."""
