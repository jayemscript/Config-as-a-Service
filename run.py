"""
Config-as-a-Service (CaaS) — Single Entry Point
Run: python run.py --caas
"""

import os
import sys
import json
import secrets
import subprocess
import threading
import time
from pathlib import Path

import click

# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

BANNER = r"""
  ____           __ _                        _____                 _
 / ___|___  _ __|  _(_) __ _    __ _ ___    / ___|  ___ _ ____   _(_) ___ ___
| |   / _ \| '_ \ |_| |/ _` |  / _` / __|   \___ \ / _ \ '__\ \ / / |/ __/ _ \
| |__| (_) | | | |  _| | (_| | | (_| \__ \    ___) |  __/ |   \ V /| | (_|  __/
 \____\___/|_| |_|_| |_|\__, |  \__,_|___/   |____/ \___|_|    \_/ |_|\___\___|
                         |___/
  Self-Hostable Configuration API  •  v0.1.0
"""

ENV_FILE = Path(".env")
DB_DIR   = Path("data")


def print_banner():
    click.echo(click.style(BANNER, fg="cyan"))


def print_step(n: int, total: int, msg: str):
    click.echo(click.style(f"\n[{n}/{total}] ", fg="yellow", bold=True) + msg)


def print_success(msg: str):
    click.echo(click.style("  ✔ ", fg="green") + msg)


def print_error(msg: str):
    click.echo(click.style("  ✘ ", fg="red") + msg)


def prompt_with_default(label: str, default: str, secret: bool = False) -> str:
    suffix = f" [{default}]" if (default and not secret) else ""
    value = click.prompt(
        click.style(f"  {label}{suffix}", fg="white"),
        default=default,
        hide_input=secret,
        show_default=False,
    )
    return value or default


def choose(label: str, choices: list, default: str) -> str:
    choices_str = " / ".join(
        click.style(c, fg="cyan", bold=True) if c == default else c
        for c in choices
    )
    click.echo(f"  {label}: {choices_str}")
    while True:
        val = click.prompt(
            click.style("  Enter choice", fg="white"),
            default=default,
            show_default=False,
        )
        if val in choices:
            return val
        click.echo(click.style("  Invalid choice. Try again.", fg="red"))


# ──────────────────────────────────────────────
# Step: Database configuration
# ──────────────────────────────────────────────

def step_database() -> dict:
    click.echo(click.style("\n  Configure Database", fg="cyan", bold=True))
    click.echo("  CaaS uses SQLite by default (zero setup). You can switch to PostgreSQL.")

    db_type = choose("Database type", ["sqlite", "postgresql"], default="sqlite")

    if db_type == "sqlite":
        DB_DIR.mkdir(exist_ok=True)
        db_path = prompt_with_default("SQLite file path", str(DB_DIR / "caas.db"))
        db_url  = f"sqlite:///{db_path}"
        print_success(f"SQLite database → {db_path}")
    else:
        click.echo(click.style("\n  PostgreSQL Connection", fg="white"))
        host   = prompt_with_default("Host", "localhost")
        port   = prompt_with_default("Port", "5432")
        name   = prompt_with_default("Database name", "caas")
        user   = prompt_with_default("Username", "postgres")
        passwd = prompt_with_default("Password", "", secret=True)
        db_url = f"postgresql://{user}:{passwd}@{host}:{port}/{name}"
        print_success(f"PostgreSQL → {host}:{port}/{name}")

    return {"DATABASE_URL": db_url}


# ──────────────────────────────────────────────
# Step: Auth / Security
# ──────────────────────────────────────────────

def step_auth() -> dict:
    click.echo(click.style("\n  Configure Authentication & Security", fg="cyan", bold=True))

    auto_key = secrets.token_hex(32)
    click.echo(click.style("  JWT Secret Key (press Enter to auto-generate):", fg="white"))
    secret_key = click.prompt("  >", default="", hide_input=True, show_default=False)
    if not secret_key.strip():
        secret_key = auto_key
        print_success("Auto-generated secret key.")
    else:
        print_success("Custom secret key set.")

    algo = choose("JWT Algorithm", ["HS256", "HS512"], default="HS256")

    expire_hours = prompt_with_default("Token expiry (hours)", "24")

    return {
        "JWT_SECRET_KEY":       secret_key,
        "JWT_ALGORITHM":        algo,
        "JWT_EXPIRATION_HOURS": expire_hours,
    }


# ──────────────────────────────────────────────
# Step: Server settings
# ──────────────────────────────────────────────

def step_server() -> dict:
    click.echo(click.style("\n  Configure Server", fg="cyan", bold=True))

    host = prompt_with_default("Host", "0.0.0.0")
    port = prompt_with_default("Port", "12500")
    debug_val = choose("Log level", ["true", "false"], default="false")

    print_success(f"Server will start at http://{host}:{port}")

    return {
        "HOST": host,
        "PORT": port,
        "LOG_LEVEL": "DEBUG" if debug_val == "true" else "INFO",
    }


# ──────────────────────────────────────────────
# Step: Encryption
# ──────────────────────────────────────────────

def step_encryption() -> dict:
    click.echo(click.style("\n  Configure Encryption", fg="cyan", bold=True))
    click.echo("  CaaS encrypts sensitive config values at rest using Fernet (AES-128).")

    auto_enc = secrets.token_urlsafe(32)
    click.echo(click.style("  Encryption key (press Enter to auto-generate):", fg="white"))
    enc_key = click.prompt("  >", default="", hide_input=True, show_default=False)
    if not enc_key.strip():
        enc_key = auto_enc
        print_success("Auto-generated encryption key.")
    else:
        print_success("Custom encryption key set.")

    return {"ENCRYPTION_KEY": enc_key}


# ──────────────────────────────────────────────
# Write .env
# ──────────────────────────────────────────────

def write_env(config: dict):
    lines = [
        "# Config-as-a-Service — generated by `python run.py --caas`",
        "# Do NOT commit this file to version control.\n",
    ]
    sections = {
        "Database":   ["DATABASE_URL"],
        "JWT":        ["JWT_SECRET_KEY", "JWT_ALGORITHM", "JWT_EXPIRATION_HOURS"],
        "Server":     ["HOST", "PORT", "LOG_LEVEL"],
        "Encryption": ["ENCRYPTION_KEY"],
    }
    for section, keys in sections.items():
        lines.append(f"# ── {section}")
        for k in keys:
            if k in config:
                lines.append(f"{k}={config[k]}")
        lines.append("")

    ENV_FILE.write_text("\n".join(lines), encoding="utf-8")
    print_success(f".env written → {ENV_FILE.resolve()}")


# ──────────────────────────────────────────────
# Operations menu
# ──────────────────────────────────────────────

def load_env_config() -> dict:
    cfg = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                cfg[k.strip()] = v.strip()
    return cfg


def get_base_url(cfg: dict) -> str:
    host = cfg.get("HOST", "0.0.0.0")
    display_host = "127.0.0.1" if host in ("0.0.0.0", "") else host
    port = cfg.get("PORT", "12500")
    return f"http://{display_host}:{port}"


def api_call(method: str, url: str, token: str, payload: dict = None):
    """Make an HTTP call to the running CaaS API."""
    try:
        import requests
    except ImportError:
        print_error("'requests' not installed. Run: pip install requests")
        return None

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        if method == "GET":
            r = requests.get(url, headers=headers, timeout=5)
        elif method == "POST":
            r = requests.post(url, headers=headers, json=payload, timeout=5)
        elif method == "PUT":
            r = requests.put(url, headers=headers, json=payload, timeout=5)
        elif method == "DELETE":
            r = requests.delete(url, headers=headers, timeout=5)
        else:
            return None
        return r
    except requests.exceptions.ConnectionError:
        print_error("Cannot reach the server. Is CaaS running? (Start with: python run.py --caas --start)")
        return None


def ops_menu(cfg: dict):
    base   = get_base_url(cfg)
    token  = cfg.get("ADMIN_API_TOKEN", cfg.get("JWT_SECRET_KEY", ""))

    ops = {
        "1": ("List all configs",     "list"),
        "2": ("Create config",        "create"),
        "3": ("Get config by app",    "get"),
        "4": ("Update config",        "update"),
        "5": ("Delete config",        "delete"),
        "6": ("Server health check",  "health"),
        "0": ("Exit operations menu", "exit"),
    }

    while True:
        click.echo(click.style("\n  ── Operations ──────────────────────────", fg="cyan"))
        for key, (label, _) in ops.items():
            click.echo(f"  [{key}] {label}")

        choice = click.prompt(click.style("\n  Select operation", fg="white"), default="0")

        if choice not in ops:
            print_error("Invalid option.")
            continue

        action = ops[choice][1]

        if action == "exit":
            break

        elif action == "health":
            r = api_call("GET", f"{base}/health", token)
            if r:
                click.echo(click.style(f"\n  Status {r.status_code}: ", fg="green") + r.text)

        elif action == "list":
            r = api_call("GET", f"{base}/api/v1/configs", token)
            if r:
                _pretty(r)

        elif action == "get":
            app_name = click.prompt("  App name")
            env      = choose("Environment", ["DEVELOPMENT", "STAGING", "PRODUCTION"], "DEVELOPMENT")
            r = api_call("GET", f"{base}/api/v1/configs/{app_name}?environment={env}", token)
            if r:
                _pretty(r)

        elif action == "create":
            app_name = click.prompt("  App name")
            env      = choose("Environment", ["DEVELOPMENT", "STAGING", "PRODUCTION"], "DEVELOPMENT")
            click.echo("  Enter config values as JSON key-value pairs.")
            click.echo("  Example: {\"DB_HOST\": \"localhost\", \"DEBUG\": \"true\"}")
            raw = click.prompt("  Values (JSON)")
            try:
                values = json.loads(raw)
            except json.JSONDecodeError:
                print_error("Invalid JSON. Please try again.")
                continue
            payload = {"app_name": app_name, "environment_type": env, "values": values}
            r = api_call("POST", f"{base}/api/v1/configs", token, payload)
            if r:
                _pretty(r)

        elif action == "update":
            app_name = click.prompt("  App name")
            env      = choose("Environment", ["DEVELOPMENT", "STAGING", "PRODUCTION"], "DEVELOPMENT")
            click.echo("  Enter updated values as JSON (only keys you want to change).")
            raw = click.prompt("  Values (JSON)")
            try:
                values = json.loads(raw)
            except json.JSONDecodeError:
                print_error("Invalid JSON. Please try again.")
                continue
            payload = {"values": values}
            r = api_call("PUT", f"{base}/api/v1/configs/{app_name}?environment={env}", token, payload)
            if r:
                _pretty(r)

        elif action == "delete":
            app_name = click.prompt("  App name")
            env      = choose("Environment", ["DEVELOPMENT", "STAGING", "PRODUCTION"], "DEVELOPMENT")
            confirm  = click.confirm(f"  Delete config for '{app_name}' [{env}]?", default=False)
            if confirm:
                r = api_call("DELETE", f"{base}/api/v1/configs/{app_name}?environment={env}", token)
                if r:
                    _pretty(r)
            else:
                click.echo("  Cancelled.")


def _pretty(response):
    try:
        data = response.json()
        formatted = json.dumps(data, indent=2)
        color = "green" if response.status_code < 400 else "red"
        click.echo(click.style(f"\n  HTTP {response.status_code}", fg=color, bold=True))
        click.echo(formatted)
    except Exception:
        click.echo(response.text)


# ──────────────────────────────────────────────
# Start server in background thread
# ──────────────────────────────────────────────

def start_server(cfg: dict):
    host      = cfg.get("HOST", "0.0.0.0")
    port      = cfg.get("PORT", "12500")
    log_level = cfg.get("LOG_LEVEL", "INFO").lower()

    # Launch uvicorn as a subprocess — avoids circular import:
    #   main.py does `import src.caas.api.routes` before cipher_manager is defined,
    #   so importing main directly from run.py triggers ImportError.
    cmd = [
        sys.executable, "-m", "uvicorn",
        "src.caas.main:app",
        "--host", host,
        "--port", str(port),
        "--log-level", log_level,
    ]

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError:
        print_error("uvicorn not found. Run: pip install -r requirements.txt")
        return False, None

    # Stream server logs in a background thread
    def _stream(p):
        for line in iter(p.stdout.readline, ""):
            click.echo(click.style("  [server] ", fg="bright_black") + line.rstrip())

    threading.Thread(target=_stream, args=(proc,), daemon=True).start()

    # Wait up to 5 s for the port to open
    display_host = "127.0.0.1" if host in ("0.0.0.0", "") else host
    import socket
    for _ in range(10):
        time.sleep(0.5)
        if proc.poll() is not None:
            print_error(f"Server exited early (code {proc.returncode}).")
            return False, None
        try:
            with socket.create_connection((display_host, int(port)), timeout=0.3):
                break
        except OSError:
            pass

    if proc.poll() is not None:
        print_error("Server failed to start.")
        return False, None

    print_success(f"Server started  -> http://{display_host}:{port}")
    print_success(f"API Docs        -> http://{display_host}:{port}/docs")
    return True, proc


# ──────────────────────────────────────────────
# Main CLI
# ──────────────────────────────────────────────

@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--caas",       is_flag=True, help="Launch interactive CaaS setup & operations")
@click.option("--start",      is_flag=True, help="Start the API server only (skip setup if .env exists)")
@click.option("--ops",        is_flag=True, help="Open operations menu only (requires server running)")
@click.option("--reconfigure",is_flag=True, help="Re-run the configuration wizard")
def main(caas, start, ops, reconfigure):
    """Config-as-a-Service — self-hostable configuration API."""

    if not any([caas, start, ops, reconfigure]):
        click.echo("Usage: python run.py --caas")
        click.echo("       python run.py --help")
        sys.exit(0)

    print_banner()

    # ── Reconfigure only
    if reconfigure:
        _run_setup()
        return

    # ── Ops only (server must already be running separately)
    if ops and not caas and not start:
        cfg = load_env_config()
        if not cfg:
            print_error("No .env found. Run `python run.py --caas` first.")
            sys.exit(1)
        ops_menu(cfg)
        return

    # ── Full --caas flow
    if caas:
        env_exists = ENV_FILE.exists()

        if env_exists and not reconfigure:
            click.echo(click.style("\n  Found existing .env configuration.", fg="green"))
            reconfig = click.confirm("  Re-run configuration wizard?", default=False)
            if reconfig:
                _run_setup()
        else:
            _run_setup()

        cfg = load_env_config()

        # Start server
        click.echo(click.style("\n  Starting CaaS Server…", fg="cyan", bold=True))
        ok, proc = start_server(cfg)
        if not ok:
            sys.exit(1)

        base = get_base_url(cfg)
        click.echo(click.style(f"""
  ─────────────────────────────────────────────
  CaaS is running!

  API Base   : {base}
  API Docs   : {base}/docs
  JWT Secret : (see .env JWT_SECRET_KEY)
  ─────────────────────────────────────────────
""", fg="cyan"))

        # Drop into ops menu
        ops_menu(cfg)

        click.echo(click.style("\n  Shutting down. Goodbye!\n", fg="yellow"))
        if proc:
            proc.terminate()

    # ── Start only
    elif start:
        cfg = load_env_config()
        if not cfg:
            print_error("No .env found. Run `python run.py --caas` first.")
            sys.exit(1)
        ok, proc = start_server(cfg)
        if not ok:
            sys.exit(1)
        base = get_base_url(cfg)
        click.echo(click.style(f"\n  Server is running at {base}\n  Press Ctrl+C to stop.\n", fg="green"))
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            click.echo(click.style("\n  Server stopped.", fg="yellow"))
            if proc:
                proc.terminate()


def _run_setup():
    """Walk through all configuration steps."""
    total = 4
    click.echo(click.style("\n  Starting CaaS Configuration Wizard…", fg="cyan", bold=True))

    print_step(1, total, "Database")
    db_cfg = step_database()

    print_step(2, total, "Authentication & Security")
    auth_cfg = step_auth()

    print_step(3, total, "Server")
    server_cfg = step_server()

    print_step(4, total, "Encryption")
    enc_cfg = step_encryption()

    full_cfg = {**db_cfg, **auth_cfg, **server_cfg, **enc_cfg}

    click.echo(click.style("\n  Writing configuration…", fg="cyan"))
    write_env(full_cfg)

    click.echo(click.style("\n  ✔ Configuration complete!\n", fg="green", bold=True))


if __name__ == "__main__":
    main()