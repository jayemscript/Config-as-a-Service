# Config-as-a-Service (CaaS)

> A lightweight, self-hostable API for centralized application configuration.  
> Replace scattered `.env` files with a single source of truth — queryable over HTTP or CLI.

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/jayemscript/Config-as-a-Service.git
cd Config-as-a-Service

# 2. Virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
python run.py --caas
```

> **→ Read [GUIDE.md](GUIDE.md) for the full setup walkthrough.**

---

## What is CaaS?

CaaS lets you store and serve application configuration (environment variables, feature flags, runtime settings) through a central HTTP API — instead of maintaining separate `.env` files for every deployment.

Services query CaaS at runtime, so you can update config without redeploying.

---

## Features

- **Self-hosted** — runs entirely on your own infrastructure
- **Interactive setup** — one command wizard, no manual file editing
- **Encrypted storage** — sensitive values encrypted at rest with Fernet (AES-128)
- **Multi-environment** — DEVELOPMENT / STAGING / PRODUCTION per app
- **FastAPI-powered** — async, fast, with built-in Swagger docs at `/docs`
- **SQLite by default** — zero-dependency database, PostgreSQL also supported
- **Built-in operations menu** — create, read, update, delete configs interactively

---

## Data model

Each config record contains:

| Field | Description |
|-------|-------------|
| `app_name` | Your application's unique identifier |
| `environment_type` | DEVELOPMENT, STAGING, or PRODUCTION |
| `values` | JSON key-value pairs (encrypted) |
| `version` | Auto-incremented change counter |

---

## REST API

Once running (default port `12500`):

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/docs` | Swagger UI |
| GET | `/api/v1/configs` | List all configs |
| POST | `/api/v1/configs` | Create config |
| GET | `/api/v1/configs/{app_name}` | Get by app |
| PUT | `/api/v1/configs/{app_name}` | Update config |
| DELETE | `/api/v1/configs/{app_name}` | Delete config |

All data endpoints require `Authorization: Bearer <ADMIN_API_TOKEN>`.

---

## License

MIT — see [LICENSE.md](LICENSE.md)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before opening issues or PRs.