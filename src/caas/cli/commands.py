"""CLI commands for Config-as-a-Service."""

import click
import json
import requests
from typing import Optional
from pathlib import Path

from src.caas.cli.utils import (
    save_token,
    load_token,
    delete_token,
    load_json_file,
    print_config_table,
)


API_BASE_URL = "http://127.0.0.1:12500"


def get_headers() -> dict:
    """Get headers with auth token."""
    token = load_token()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


@click.group()
def cli():
    """Config-as-a-Service CLI - Manage configurations from the command line."""
    pass


# ============================================================================
# Authentication Commands
# ============================================================================

@cli.group()
def auth():
    """Authentication commands."""
    pass


@auth.command("generate-token")
def generate_token():
    """Generate a new API token."""
    try:
        response = requests.post(f"{API_BASE_URL}/cass/auth/token")
        response.raise_for_status()
        data = response.json()
        
        token = data["access_token"]
        save_token(token)
        click.echo(click.style(f"✓ Token generated successfully", fg="green"))
        click.echo(f"  Token: {token[:20]}...")
        click.echo(f"  Expires in: {data['expires_in']} seconds")
    except requests.exceptions.ConnectionError:
        click.echo(click.style("✗ Connection failed. Is the API running?", fg="red"))
        raise click.Abort()
    except requests.exceptions.HTTPError as e:
        click.echo(click.style(f"✗ Failed to generate token: {e}", fg="red"))
        raise click.Abort()


@auth.command("logout")
def logout():
    """Remove stored token."""
    delete_token()
    click.echo(click.style("✓ Logged out successfully", fg="green"))


@auth.command("show")
def show_token():
    """Show current stored token."""
    token = load_token()
    if token:
        click.echo(f"Current token: {token[:20]}...")
    else:
        click.echo(click.style("No token stored", fg="yellow"))


# ============================================================================
# Configuration Commands
# ============================================================================

@cli.group()
def config():
    """Configuration management commands."""
    pass


@config.command("create")
@click.option("--app-name", required=True, help="Application name")
@click.option("--env", required=True, type=click.Choice(["DEVELOPMENT", "STAGING", "PRODUCTION"]), help="Environment")
@click.option("--values", type=click.Path(exists=True), help="Path to JSON file with values")
@click.option("--inline", help="Inline JSON string with values")
def create_config(app_name: str, env: str, values: Optional[str], inline: Optional[str]):
    """Create a new configuration."""
    try:
        if not values and not inline:
            click.echo(click.style("✗ Must provide either --values or --inline", fg="red"))
            raise click.Abort()
        
        if values:
            config_values = load_json_file(values)
        else:
            config_values = json.loads(inline)
        
        payload = {
            "app_name": app_name,
            "environment_type": env,
            "values": config_values
        }
        
        response = requests.post(
            f"{API_BASE_URL}/cass/create",
            json=payload,
            headers=get_headers()
        )
        response.raise_for_status()
        
        config = response.json()
        click.echo(click.style(f"✓ Configuration created successfully", fg="green"))
        print_config_table(config)
    
    except requests.exceptions.ConnectionError:
        click.echo(click.style("✗ Connection failed. Is the API running?", fg="red"))
        raise click.Abort()
    except requests.exceptions.HTTPError as e:
        error_msg = e.response.json().get("detail", str(e))
        click.echo(click.style(f"✗ {error_msg}", fg="red"))
        raise click.Abort()


@config.command("get")
@click.argument("app_name")
@click.option("--env", type=click.Choice(["DEVELOPMENT", "STAGING", "PRODUCTION"]), help="Environment (optional)")
def get_config(app_name: str, env: Optional[str]):
    """Retrieve a configuration."""
    try:
        url = f"{API_BASE_URL}/cass/get/{app_name}"
        params = {}
        if env:
            params["environment_type"] = env
        
        response = requests.get(
            url,
            params=params,
            headers=get_headers()
        )
        response.raise_for_status()
        
        config = response.json()
        print_config_table(config)
    
    except requests.exceptions.ConnectionError:
        click.echo(click.style("✗ Connection failed. Is the API running?", fg="red"))
        raise click.Abort()
    except requests.exceptions.HTTPError as e:
        error_msg = e.response.json().get("detail", str(e))
        click.echo(click.style(f"✗ {error_msg}", fg="red"))
        raise click.Abort()


@config.command("update")
@click.option("--app-name", required=True, help="Application name")
@click.option("--env", required=True, type=click.Choice(["DEVELOPMENT", "STAGING", "PRODUCTION"]), help="Environment")
@click.option("--values", type=click.Path(exists=True), help="Path to JSON file with new values")
@click.option("--inline", help="Inline JSON string with new values")
@click.option("--partial", is_flag=True, help="Merge values instead of replacing (PATCH)")
def update_config(app_name: str, env: str, values: Optional[str], inline: Optional[str], partial: bool):
    """Update a configuration."""
    try:
        if not values and not inline:
            click.echo(click.style("✗ Must provide either --values or --inline", fg="red"))
            raise click.Abort()
        
        if values:
            config_values = load_json_file(values)
        else:
            config_values = json.loads(inline)
        
        payload = {
            "app_name": app_name,
            "environment_type": env,
            "values": config_values
        }
        
        endpoint = "/cass/update/partial" if partial else "/cass/update"
        response = requests.put(
            f"{API_BASE_URL}{endpoint}",
            json=payload,
            headers=get_headers()
        )
        response.raise_for_status()
        
        config = response.json()
        click.echo(click.style(f"✓ Configuration updated successfully", fg="green"))
        print_config_table(config)
    
    except requests.exceptions.ConnectionError:
        click.echo(click.style("✗ Connection failed. Is the API running?", fg="red"))
        raise click.Abort()
    except requests.exceptions.HTTPError as e:
        error_msg = e.response.json().get("detail", str(e))
        click.echo(click.style(f"✗ {error_msg}", fg="red"))
        raise click.Abort()


@config.command("list")
@click.option("--page", default=1, help="Page number")
@click.option("--limit", default=10, help="Items per page")
@click.option("--search", help="Search by app name")
@click.option("--env", type=click.Choice(["DEVELOPMENT", "STAGING", "PRODUCTION"]), help="Filter by environment")
def list_configs(page: int, limit: int, search: Optional[str], env: Optional[str]):
    """List all configurations with pagination."""
    try:
        params = {
            "page": page,
            "limit": limit
        }
        if search:
            params["search"] = search
        if env:
            params["environment_type"] = env
        
        response = requests.get(
            f"{API_BASE_URL}/cass/get/paginated",
            params=params,
            headers=get_headers()
        )
        response.raise_for_status()
        
        data = response.json()
        
        if not data["items"]:
            click.echo(click.style("No configurations found", fg="yellow"))
            return
        
        click.echo(f"\n{'App Name':<20} {'Environment':<15} {'Version':<8}")
        click.echo("-" * 45)
        for item in data["items"]:
            click.echo(f"{item['app_name']:<20} {item['environment_type']:<15} {item['version']:<8}")
        
        click.echo(f"\nPage {data['page']} of {data['pages']} (Total: {data['total']})\n")
    
    except requests.exceptions.ConnectionError:
        click.echo(click.style("✗ Connection failed. Is the API running?", fg="red"))
        raise click.Abort()
    except requests.exceptions.HTTPError as e:
        error_msg = e.response.json().get("detail", str(e))
        click.echo(click.style(f"✗ {error_msg}", fg="red"))
        raise click.Abort()


@config.command("delete")
@click.option("--app-name", required=True, help="Application name")
@click.option("--env", required=True, type=click.Choice(["DEVELOPMENT", "STAGING", "PRODUCTION"]), help="Environment")
@click.confirmation_option(prompt="Are you sure you want to delete this configuration?")
def delete_config(app_name: str, env: str):
    """Delete a configuration (irreversible)."""
    try:
        payload = {
            "app_name": app_name,
            "environment_type": env
        }
        
        response = requests.delete(
            f"{API_BASE_URL}/cass/delete",
            json=payload,
            headers=get_headers()
        )
        response.raise_for_status()
        
        result = response.json()
        click.echo(click.style(f"✓ {result['message']}", fg="green"))
    
    except requests.exceptions.ConnectionError:
        click.echo(click.style("✗ Connection failed. Is the API running?", fg="red"))
        raise click.Abort()
    except requests.exceptions.HTTPError as e:
        error_msg = e.response.json().get("detail", str(e))
        click.echo(click.style(f"✗ {error_msg}", fg="red"))
        raise click.Abort()


if __name__ == "__main__":
    cli()
