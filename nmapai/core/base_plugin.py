"""Base plugin interface for extensibility."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from enum import Enum
import asyncio


class PluginStatus(Enum):
    """Plugin execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class PluginPriority(Enum):
    """Plugin execution priority."""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


class BasePlugin(ABC):
    """Base class for all plugins."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.status = PluginStatus.PENDING
        self.error: Optional[str] = None
        self.results: Dict[str, Any] = {}
        self.metrics: Dict[str, Any] = {}

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version."""
        pass

    @property
    def priority(self) -> PluginPriority:
        """Plugin execution priority."""
        return PluginPriority.NORMAL

    @property
    def dependencies(self) -> List[str]:
        """List of plugin names this plugin depends on."""
        return []

    @abstractmethod
    async def validate(self) -> bool:
        """Validate plugin can run (dependencies, config, etc)."""
        pass

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute plugin logic. Returns results dictionary."""
        pass

    async def cleanup(self) -> None:
        """Cleanup resources after execution."""
        pass

    def get_status(self) -> PluginStatus:
        """Get current plugin status."""
        return self.status

    def get_results(self) -> Dict[str, Any]:
        """Get plugin execution results."""
        return self.results

    def get_metrics(self) -> Dict[str, Any]:
        """Get plugin execution metrics."""
        return self.metrics


class ScannerPlugin(BasePlugin):
    """Base class for scanner plugins (Nmap, Nikto, etc)."""

    @abstractmethod
    async def scan(self, targets: List[str], params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute scan on targets."""
        pass

    @abstractmethod
    async def parse_results(self, raw_output: str) -> Dict[str, Any]:
        """Parse raw scanner output into structured data."""
        pass


class AIProviderPlugin(BasePlugin):
    """Base class for AI provider plugins."""

    @abstractmethod
    async def analyze(self, data: Dict[str, Any], prompt: str) -> str:
        """Analyze data using AI model."""
        pass

    @abstractmethod
    async def stream_analyze(self, data: Dict[str, Any], prompt: str):
        """Stream analysis results in real-time."""
        pass

    @property
    @abstractmethod
    def supports_streaming(self) -> bool:
        """Whether this provider supports streaming."""
        pass


class EnricherPlugin(BasePlugin):
    """Base class for data enrichment plugins (CVE, EPSS, etc)."""

    @abstractmethod
    async def enrich(self, vulnerabilities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enrich vulnerability data with additional information."""
        pass


class ReporterPlugin(BasePlugin):
    """Base class for report generation plugins."""

    @abstractmethod
    async def generate(self, data: Dict[str, Any], output_path: str) -> str:
        """Generate report from scan data."""
        pass

    @property
    @abstractmethod
    def format(self) -> str:
        """Report format (html, pdf, json, etc)."""
        pass


class NotifierPlugin(BasePlugin):
    """Base class for notification plugins (Slack, Discord, Email)."""

    @abstractmethod
    async def notify(self, message: str, severity: str = "info") -> bool:
        """Send notification."""
        pass

    @abstractmethod
    async def notify_scan_complete(self, scan_results: Dict[str, Any]) -> bool:
        """Send scan completion notification."""
        pass
