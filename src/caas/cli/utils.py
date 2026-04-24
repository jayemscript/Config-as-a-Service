"""CLI utility functions for Config-as-a-Service."""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

# CLI config directory
CLI_CONFIG_DIR = Path.home() / ".caas"
TOKEN_FILE = CLI_CONFIG_DIR / "token"


def ensure_config_dir():
    """Ensure CLI config directory exists."""
    CLI_CONFIG_DIR.mkdir(exist_ok=True, parents=True)


def save_token(token: str):
    """Save token to local config."""
    ensure_config_dir()
    TOKEN_FILE.write_text(token)
    TOKEN_FILE.chmod(0o600)  # Make it readable only by owner
    print(f"✓ Token saved to {TOKEN_FILE}")


def load_token() -> Optional[str]:
    """Load token from local config."""
    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text().strip()
    return None


def delete_token():
    """Delete stored token."""
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()
        print(f"✓ Token deleted from {TOKEN_FILE}")


def load_json_file(filepath: str) -> Dict[str, Any]:
    """Load JSON values from a file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"✗ File not found: {filepath}")
        raise
    except json.JSONDecodeError:
        print(f"✗ Invalid JSON in file: {filepath}")
        raise


def print_config_table(config: Dict[str, Any]):
    """Pretty print a configuration."""
    print("\n" + "=" * 60)
    print(f"App Name:         {config['app_name']}")
    print(f"Environment:      {config['environment_type']}")
    print(f"Version:          {config['version']}")
    print(f"Created:          {config['created_at']}")
    print(f"Updated:          {config['updated_at']}")
    print("-" * 60)
    print("Configuration Values:")
    for key, value in config['values'].items():
        print(f"  {key}: {value}")
    print("=" * 60 + "\n")
