"""Configuration loader for Writers Factory.

Loads agent configurations, credentials, and settings.
"""

from pathlib import Path
import yaml
import json
from typing import Dict, Any


def get_config_dir() -> Path:
    """Get the configuration directory."""
    return Path(__file__).parent


def get_root_dir() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent.parent


def load_agent_config() -> Dict[str, Any]:
    """Load agent configuration from agents.yaml."""
    config_path = get_config_dir() / "agents.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Agent config not found: {config_path}")

    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def load_settings() -> Dict[str, Any]:
    """Load settings from settings.yaml."""
    config_path = get_config_dir() / "settings.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Settings not found: {config_path}")

    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def load_credentials() -> Dict[str, Any]:
    """Load credentials from config/credentials.json."""
    creds_path = get_root_dir() / "config" / "credentials.json"

    if not creds_path.exists():
        raise FileNotFoundError(f"Credentials not found: {creds_path}")

    with open(creds_path, 'r') as f:
        return json.load(f)


def get_agent_config(agent_name: str) -> Dict[str, Any]:
    """Get configuration for a specific agent."""
    config = load_agent_config()
    agents = config.get("agents", {})

    if agent_name not in agents:
        raise ValueError(f"Agent '{agent_name}' not found in configuration")

    return agents[agent_name]


def get_agent_group(group_name: str) -> list:
    """Get list of agents in a predefined group."""
    config = load_agent_config()
    groups = config.get("agent_groups", {})

    if group_name not in groups:
        raise ValueError(f"Agent group '{group_name}' not found")

    return groups[group_name]


def get_enabled_agents() -> Dict[str, Dict[str, Any]]:
    """Get all enabled agents."""
    config = load_agent_config()
    agents = config.get("agents", {})

    return {
        name: cfg
        for name, cfg in agents.items()
        if cfg.get("enabled", True)
    }


def get_api_key(provider: str) -> str:
    """Get API key for a specific provider."""
    creds = load_credentials()

    if provider not in creds:
        raise ValueError(f"No credentials found for provider: {provider}")

    provider_creds = creds[provider]

    if isinstance(provider_creds, dict):
        return provider_creds.get("api_key", "")
    else:
        return provider_creds
