"""Configuration management for NetApp CLI."""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class NetAppConfig(BaseModel):
    """NetApp API configuration model."""

    host: str = Field(..., description="NetApp ActiveIQ host")
    username: str = Field(..., description="API username")
    password: str = Field(..., description="API password")
    verify_ssl: bool = Field(True, description="Verify SSL certificates")
    timeout: int = Field(30, description="Request timeout in seconds")
    api_version: str = Field("v1", description="API version")


class Config:
    """Main configuration class."""

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self._find_config_file()
        self._config_data: Dict[str, Any] = {}
        self._netapp_config: Optional[NetAppConfig] = None
        self.load_config()

    def _find_config_file(self) -> Optional[str]:
        """Find configuration file in standard locations."""
        possible_locations = [
            "~/.netapp-cli/netapp-cli.yaml",
            "~/.netapp-cli/netapp-cli.yml",
            "netapp-cli.yaml",
            "netapp-cli.yml",
            "~/.netapp-cli.yaml",
            "~/.netapp-cli.yml",
            "~/.config/netapp-cli/config.yaml",
            "~/.config/netapp-cli/config.yml",
        ]

        for location in possible_locations:
            expanded_path = Path(location).expanduser()
            if expanded_path.exists():
                return str(expanded_path)

        return None

    def load_config(self):
        """Load configuration from file or environment."""
        if self.config_file and Path(self.config_file).exists():
            with open(self.config_file, 'r') as f:
                self._config_data = yaml.safe_load(f) or {}

        # Override with environment variables
        env_config = {
            "host": os.getenv("NETAPP_HOST"),
            "username": os.getenv("NETAPP_USERNAME"),
            "password": os.getenv("NETAPP_PASSWORD"),
            "verify_ssl": os.getenv("NETAPP_VERIFY_SSL", "true").lower() == "true",
            "timeout": int(os.getenv("NETAPP_TIMEOUT", "30")),
            "api_version": os.getenv("NETAPP_API_VERSION", "v1"),
        }

        # Merge configurations
        netapp_config = self._config_data.get("netapp", {})
        for key, value in env_config.items():
            if value is not None:
                netapp_config[key] = value

        if netapp_config.get("host"):
            try:
                self._netapp_config = NetAppConfig(**netapp_config)
            except Exception as e:
                raise ValueError(f"Invalid NetApp configuration: {e}")

    @property
    def netapp(self) -> Optional[NetAppConfig]:
        """Get NetApp API configuration."""
        return self._netapp_config

    def is_configured(self) -> bool:
        """Check if NetApp API is properly configured."""
        return self._netapp_config is not None

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        return self._config_data.get(key, default)

    def save_config(self, config_file: Optional[str] = None):
        """Save current configuration to file."""
        target_file = config_file or self.config_file
        if not target_file:
            target_file = Path.home() / ".netapp-cli" / "netapp-cli.yaml"

        config_dir = Path(target_file).parent
        config_dir.mkdir(parents=True, exist_ok=True)

        with open(target_file, 'w') as f:
            yaml.dump(self._config_data, f, default_flow_style=False)

    def create_sample_config(self, output_file: Optional[str] = None):
        """Create a sample configuration file."""
        if output_file is None:
            output_file = str(Path.home() / ".netapp-cli" / "netapp-cli.yaml")

        # Ensure the directory exists
        config_dir = Path(output_file).parent
        config_dir.mkdir(parents=True, exist_ok=True)

        sample_config = {
            "netapp": {
                "host": "your-netapp-cluster.example.com",
                "username": "admin",
                "password": "your-password",
                "verify_ssl": True,
                "timeout": 30,
                "api_version": "v1"
            },
            "output": {
                "format": "table",
                "colors": True
            },
            "logging": {
                "level": "INFO",
                "file": "netapp-cli.log"
            }
        }

        with open(output_file, 'w') as f:
            yaml.dump(sample_config, f, default_flow_style=False)

        return output_file
