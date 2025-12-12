"""Anthropic Claude provider for AI analysis."""

import asyncio
import json
import os
from typing import Any, Dict, Optional, AsyncIterator
import aiohttp

from nmapai.core.base_plugin import AIProviderPlugin, PluginStatus


class AnthropicProvider(AIProviderPlugin):
    """Anthropic Claude API provider."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.api_key = config.get("api_key") or os.environ.get("ANTHROPIC_API_KEY", "") if config else ""
        self.endpoint = config.get("endpoint", "https://api.anthropic.com/v1/messages") if config else "https://api.anthropic.com/v1/messages"
        self.model = config.get("model", "claude-3-5-sonnet-20241022") if config else "claude-3-5-sonnet-20241022"
        self.max_tokens = config.get("max_tokens", 4096) if config else 4096
        self.temperature = config.get("temperature", 0.3) if config else 0.3

    @property
    def name(self) -> str:
        return "anthropic_provider"

    @property
    def version(self) -> str:
        return "2.0.0"

    @property
    def supports_streaming(self) -> bool:
        return True

    async def validate(self) -> bool:
        """Validate API key is available."""
        if not self.api_key:
            self.error = "Anthropic API key not set"
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
        """Analyze data using Anthropic API."""
        context = self._prepare_context(data)

        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "system": "You are an expert security analyst specializing in penetration testing, vulnerability assessment, and threat analysis. Provide detailed, actionable security insights.",
            "messages": [
                {
                    "role": "user",
                    "content": f"{prompt}\n\n{context}"
                }
            ]
        }

        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.endpoint,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"API error {response.status}: {error_text}")

                result = await response.json()
                return result["content"][0]["text"]

    async def stream_analyze(self, data: Dict[str, Any], prompt: str) -> AsyncIterator[str]:
        """Stream analysis results in real-time."""
        context = self._prepare_context(data)

        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "system": "You are an expert security analyst. Provide concise, actionable security insights.",
            "messages": [
                {
                    "role": "user",
                    "content": f"{prompt}\n\n{context}"
                }
            ],
            "stream": True
        }

        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.endpoint,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"API error {response.status}: {error_text}")

                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        data_str = line[6:]
                        try:
                            chunk = json.loads(data_str)
                            if chunk.get('type') == 'content_block_delta':
                                delta = chunk.get('delta', {})
                                text = delta.get('text', '')
                                if text:
                                    yield text
                        except json.JSONDecodeError:
                            continue

    def _prepare_context(self, data: Dict[str, Any]) -> str:
        """Prepare context from scan data - shared with OpenAI provider."""
        lines = []

        hosts = data.get("nmap_results", {}).get("hosts", [])
        if hosts:
            lines.append("=== NMAP SCAN RESULTS ===\n")
            for host in hosts:
                lines.append(f"\nHost: {host.get('ip')} ({host.get('hostname', 'N/A')})")
                if host.get('os'):
                    lines.append(f"OS: {host['os'].get('name')}")
                if host.get('ports'):
                    lines.append("Open Ports:")
                    for port in host['ports']:
                        service = port.get('service', {})
                        lines.append(
                            f"  - {port['port']}/{port['protocol']}: "
                            f"{service.get('name', 'unknown')} {service.get('product', '')} {service.get('version', '')}"
                        )

        nikto_results = data.get("nikto_results", {})
        if nikto_results.get("scans"):
            lines.append("\n\n=== NIKTO WEB SCAN RESULTS ===\n")
            for scan in nikto_results["scans"]:
                target = scan.get("target", {})
                lines.append(f"\nTarget: {target.get('url')}")
                for finding in scan.get("findings", [])[:10]:
                    lines.append(f"  - [{finding['severity'].upper()}] {finding['description'][:150]}")

        vulns = data.get("vulnerabilities", [])
        if vulns:
            lines.append("\n\n=== VULNERABILITIES ===\n")
            for vuln in vulns[:15]:
                lines.append(f"\n{vuln.get('cve_id', 'N/A')}: {vuln.get('description', '')[:150]}")
                lines.append(f"  CVSS: {vuln.get('cvss_score', 'N/A')} | EPSS: {vuln.get('epss_score', 'N/A')}")

        return "\n".join(lines)

    def _default_prompt(self) -> str:
        """Default analysis prompt."""
        return """Analyze these security scan results comprehensively:

1. **Executive Summary**: Security posture overview
2. **Critical Vulnerabilities**: Immediate threats
3. **Attack Vectors**: Potential exploitation paths
4. **Risk Assessment**: Overall security risk level
5. **Prioritized Actions**: Top 7 remediation steps
6. **CVE Analysis**: Exploitable vulnerabilities
7. **Defense Recommendations**: Hardening strategies

Provide clear, actionable Markdown output."""
