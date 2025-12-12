"""Configuration management with profiles support."""

import yaml
import json
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigManager:
    """Manage configuration with profile support."""

    PROFILES = {
        "quick": {
            "description": "Quick scan for rapid assessment",
            "nmap": {
                "enabled": True,
                "nmap_params": "-sV -T4 --top-ports 100",
                "adaptive_mode": False,
            },
            "nikto": {"enabled": False},
            "enrichers": {
                "nvd": {"enabled": False},
                "epss": {"enabled": False},
                "exploitdb": {"enabled": False},
            },
            "ai": {"enabled": False},
        },
        "standard": {
            "description": "Standard comprehensive scan",
            "nmap": {
                "enabled": True,
                "nmap_params": "-sV -sC -T4 --top-ports 1000",
                "adaptive_mode": True,
            },
            "nikto": {"enabled": True, "concurrency": 3},
            "enrichers": {
                "nvd": {"enabled": True},
                "epss": {"enabled": True},
                "exploitdb": {"enabled": True},
            },
            "ai": {"enabled": True, "provider": "openai"},
        },
        "deep": {
            "description": "Deep thorough scan with all features",
            "nmap": {
                "enabled": True,
                "nmap_params": "-sV -sC -A -T4 -p-",
                "adaptive_mode": True,
            },
            "nikto": {"enabled": True, "concurrency": 5},
            "enrichers": {
                "nvd": {"enabled": True},
                "epss": {"enabled": True},
                "exploitdb": {"enabled": True},
            },
            "ai": {"enabled": True, "provider": "anthropic"},
        },
        "stealth": {
            "description": "Stealthy slow scan to avoid detection",
            "nmap": {
                "enabled": True,
                "nmap_params": "-sS -T2 --top-ports 200 -f",
                "adaptive_mode": False,
            },
            "nikto": {"enabled": False},
            "enrichers": {
                "nvd": {"enabled": True},
                "epss": {"enabled": False},
                "exploitdb": {"enabled": False},
            },
            "ai": {"enabled": False},
        },
    }

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path
        self.config: Dict[str, Any] = {}

    def load_profile(self, profile_name: str) -> Dict[str, Any]:
        """Load a predefined scan profile."""
        if profile_name not in self.PROFILES:
            raise ValueError(f"Unknown profile: {profile_name}. Available: {', '.join(self.PROFILES.keys())}")

        return self.PROFILES[profile_name].copy()

    def load_from_file(self, path: Path) -> Dict[str, Any]:
        """Load configuration from YAML or JSON file."""
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        content = path.read_text()

        if path.suffix in ['.yaml', '.yml']:
            return yaml.safe_load(content)
        elif path.suffix == '.json':
            return json.loads(content)
        else:
            raise ValueError(f"Unsupported config format: {path.suffix}")

    def save_to_file(self, config: Dict[str, Any], path: Path):
        """Save configuration to file."""
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.suffix in ['.yaml', '.yml']:
            path.write_text(yaml.dump(config, default_flow_style=False))
        elif path.suffix == '.json':
            path.write_text(json.dumps(config, indent=2))
        else:
            raise ValueError(f"Unsupported config format: {path.suffix}")

    def merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Merge two configurations (override takes precedence)."""
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge_configs(result[key], value)
            else:
                result[key] = value

        return result

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "nmap": {
                "enabled": True,
                "nmap_params": "-sV -T4 --top-ports 1000",
                "adaptive_mode": False,
            },
            "nikto": {
                "enabled": True,
                "concurrency": 2,
            },
            "dursvuln": {
                "enabled": False,
                "use_global": False,
            },
            "enrichers": {
                "nvd": {"enabled": True},
                "epss": {"enabled": True},
                "exploitdb": {"enabled": True},
            },
            "ai": {
                "enabled": False,
                "provider": "openai",
                "model": "gpt-4o-mini",
                "max_tokens": 2000,
                "temperature": 0.2,
            },
            "reporting": {
                "formats": ["json", "markdown", "html", "csv"],
            },
            "vulnerability_engine": {
                "scoring_weights": {
                    "cvss": 0.35,
                    "epss": 0.25,
                    "exploit_available": 0.20,
                    "service_exposure": 0.10,
                    "age": 0.10,
                },
            },
        }

    @staticmethod
    def list_profiles() -> Dict[str, str]:
        """List available profiles with descriptions."""
        return {name: profile["description"] for name, profile in ConfigManager.PROFILES.items()}
