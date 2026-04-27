# CaaS — Setup & Usage Guide

> **One command to rule them all.**  
> After the initial venv setup, everything runs through `python run.py --caas`.

---

## Prerequisites

- Python 3.11 or later
- Git

---

## Step 1 — Clone the repository

```bash
git clone https://github.com/jayemscript/Config-as-a-Service.git
cd Config-as-a-Service
```

---

## Step 2 — Create and activate a virtual environment

**Windows (PowerShell)**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
python -m venv venv
source venv/bin/activate
```

> Your prompt should now show `(venv)` to confirm the environment is active.

---

## Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

---

## Step 4 — Launch CaaS

```bash
python run.py --caas
```

That's it. From here the interactive wizard handles everything else.

---

## What happens when you run `--caas`

### First run (no `.env` present)
The wizard walks you through 4 configuration steps:

| Step | What it configures |
|------|--------------------|
| 1    | **Database** — SQLite (default, zero setup) or PostgreSQL |
| 2    | **Auth & Security** — JWT secret, admin API token, algorithm, expiry |
| 3    | **Server** — host, port, environment type, debug/reload flags |
| 4    | **Encryption** — Fernet key for encrypting stored config values |

All values are saved to a `.env` file in the project root. Auto-generated secrets are used wherever you leave the prompt blank — **this is recommended**.

### Subsequent runs
If `.env` already exists, CaaS will ask whether you want to re-run the wizard or skip straight to the running server. Choose **No** to go straight to the operations menu.

---

## Operations Menu

Once the server is running you'll land in an interactive operations menu:

```
  [1] List all configs
  [2] Create config
  [3] Get config by app
  [4] Update config
  [5] Delete config
  [6] Server health check
  [0] Exit operations menu
```

All operations hit the live API on your behalf — no curl commands needed.

### Example: Creating a config

```
Select operation: 2
App name: my-backend
Environment: DEVELOPMENT
Values (JSON): {"DB_HOST": "localhost", "DB_PORT": "5432", "DEBUG": "true"}
```

### Example: Fetching a config

```
Select operation: 3
App name: my-backend
Environment: DEVELOPMENT
```

---

## Other run modes

| Command | Purpose |
|---------|---------|
| `python run.py --caas` | Full setup wizard + start server + ops menu |
| `python run.py --start` | Start server only (skips wizard, uses existing `.env`) |
| `python run.py --ops` | Open ops menu only (requires server already running) |
| `python run.py --reconfigure` | Re-run the configuration wizard |

---

## REST API

The server starts on port **12500** by default (configurable in the wizard).

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/health` | Health check |
| GET    | `/docs`   | Interactive API docs (Swagger UI) |
| GET    | `/api/v1/configs` | List all configs |
| POST   | `/api/v1/configs` | Create a config |
| GET    | `/api/v1/configs/{app_name}` | Get config by app |
| PUT    | `/api/v1/configs/{app_name}` | Update config |
| DELETE | `/api/v1/configs/{app_name}` | Delete config |

All endpoints (except `/health` and `/docs`) require the `Authorization: Bearer <ADMIN_API_TOKEN>` header. Your token is shown in the terminal after the wizard and is stored in `.env`.

---

## Environment types

CaaS supports three environment classifications:

- `DEVELOPMENT`
- `STAGING`
- `PRODUCTION`

Each app can have a separate config per environment type.

---

## Security notes

- **Never commit `.env` to version control.** It's already in `.gitignore`.
- The encryption key in `.env` is used to encrypt all stored config values. Back it up securely.
- If you lose the encryption key, stored values cannot be decrypted.
- For production use, set `DEBUG=false` and `RELOAD=false`.

---

## Troubleshooting

**`python run.py --caas` gives `ModuleNotFoundError`**  
→ Make sure your venv is activated and you ran `pip install -r requirements.txt`.

**Operations menu says "Cannot reach the server"**  
→ The server may have failed to start. Check the terminal output for errors.

**Port 12500 is already in use**  
→ Re-run `python run.py --reconfigure` and choose a different port.

---

## Next release

An `.exe`-based installer for Windows is planned for the next release. For now, this terminal-based setup is the supported self-hosting path.