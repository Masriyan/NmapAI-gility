"""Ollama local LLM provider for offline AI analysis."""

import asyncio
import json
from typing import Any, Dict, Optional, AsyncIterator
import aiohttp

from nmapai.core.base_plugin import AIProviderPlugin, PluginStatus


class OllamaProvider(AIProviderPlugin):
    """Ollama provider for local/offline AI analysis."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.endpoint = config.get("endpoint", "http://localhost:11434") if config else "http://localhost:11434"
        self.model = config.get("model", "llama3.1:8b") if config else "llama3.1:8b"
        self.temperature = config.get("temperature", 0.3) if config else 0.3

    @property
    def name(self) -> str:
        return "ollama_provider"

    @property
    def version(self) -> str:
        return "2.0.0"

    @property
    def supports_streaming(self) -> bool:
        return True

    async def validate(self) -> bool:
        """Validate Ollama is available."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.endpoint}/api/tags", timeout=aiohttp.ClientTimeout(total=5)) as response:
                    return response.status == 200
        except Exception as e:
            self.error = f"Ollama not available: {e}"
            return False

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
        """Analyze data using Ollama."""
        context = self._prepare_context(data)

        payload = {
            "model": self.model,
            "prompt": f"System: You are a security expert. Analyze these scan results.\n\n{prompt}\n\n{context}",
            "stream": False,
            "options": {
                "temperature": self.temperature,
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.endpoint}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=300)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ollama error {response.status}: {error_text}")

                result = await response.json()
                return result.get("response", "")

    async def stream_analyze(self, data: Dict[str, Any], prompt: str) -> AsyncIterator[str]:
        """Stream analysis results."""
        context = self._prepare_context(data)

        payload = {
            "model": self.model,
            "prompt": f"System: You are a security expert.\n\n{prompt}\n\n{context}",
            "stream": True,
            "options": {
                "temperature": self.temperature,
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.endpoint}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=300)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ollama error {response.status}: {error_text}")

                async for line in response.content:
                    try:
                        chunk = json.loads(line.decode('utf-8'))
                        text = chunk.get("response", "")
                        if text:
                            yield text
                        if chunk.get("done"):
                            break
                    except json.JSONDecodeError:
                        continue

    def _prepare_context(self, data: Dict[str, Any]) -> str:
        """Prepare context from scan data."""
        lines = []

        hosts = data.get("nmap_results", {}).get("hosts", [])
        if hosts:
            lines.append("SCAN RESULTS:\n")
            for host in hosts[:10]:  # Limit for local LLM context
                lines.append(f"\nHost: {host.get('ip')}")
                for port in host.get('ports', [])[:5]:
                    service = port.get('service', {})
                    lines.append(f"  - Port {port['port']}: {service.get('name', 'unknown')}")

        return "\n".join(lines)[:2000]  # Limit context for local models

    def _default_prompt(self) -> str:
        """Default analysis prompt for local models (simpler)."""
        return """Analyze security scan results. Provide:
1. Key findings
2. Critical vulnerabilities
3. Top 5 recommendations

Be concise."""
