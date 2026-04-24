# Getting Started with Config-as-a-Service

This guide walks you through installing and using CaaS locally for the first time.

---

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [API Usage](#api-usage)
4. [CLI Usage](#cli-usage)
5. [Troubleshooting](#troubleshooting)

---

## Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git (to clone the repository)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/Config-as-a-Service.git
cd Config-as-a-Service
```

### Step 2: Create a Virtual Environment

```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables

```bash
cp .env.example .env
```

Now generate and add encryption keys to `.env`:

```bash
# Generate Fernet encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Copy the output and set ENCRYPTION_KEY in .env

# Generate JWT secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Copy the output and set JWT_SECRET_KEY in .env
```

Your `.env` file should look like:

```
PORT=12500
HOST=127.0.0.1
DATABASE_URL=sqlite:///./caas_data.db
ENCRYPTION_KEY=your-generated-fernet-key
JWT_SECRET_KEY=your-generated-jwt-secret
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
LOG_LEVEL=INFO
```

---

## Quick Start

### 1. Start the API Server

```bash
python -m src.caas.main
```

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:12500 (Press CTRL+C to quit)
✓ Application started on 127.0.0.1:12500
```

Leave this running in one terminal.

### 2. In Another Terminal, Generate an API Token

```bash
# Activate the virtual environment if needed
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Generate and save token
python -m src.caas.cli auth generate-token
```

Output:

```
✓ Token saved to ~/.caas/token
✓ Token generated successfully
  Token: eyJhbGciOiJIUzI1NiI...
  Expires in: 86400 seconds
```

### 3. Create Your First Configuration

Using CLI:

```bash
python -m src.caas.cli config create \
  --app-name my_app \
  --env DEVELOPMENT \
  --inline '{"DB_NAME": "my_db", "DB_PASSWORD": "admin@123#"}'
```

Output:

```
✓ Configuration created successfully

============================================================
App Name:         my_app
Environment:      DEVELOPMENT
Version:          1
Created:          2024-04-24T10:30:00
Updated:          2024-04-24T10:30:00
------------------------------------------------------------
Configuration Values:
  DB_NAME: my_db
  DB_PASSWORD: admin@123#
============================================================
```

### 4. Retrieve the Configuration

```bash
python -m src.caas.cli config get my_app --env DEVELOPMENT
```

Output shows the same configuration with decrypted values.

### 5. Update a Configuration

Partial update (merge specific values):

```bash
python -m src.caas.cli config update \
  --app-name my_app \
  --env DEVELOPMENT \
  --inline '{"DB_PORT": "5432"}' \
  --partial
```

Full update (replace entire values):

```bash
python -m src.caas.cli config update \
  --app-name my_app \
  --env DEVELOPMENT \
  --inline '{"DB_NAME": "new_db", "DB_PASSWORD": "newpass"}'
```

### 6. List All Configurations

```bash
python -m src.caas.cli config list
```

Output:

```
App Name             Environment    Version
---------------------------------------------
my_app               DEVELOPMENT    2

Page 1 of 1 (Total: 1)
```

### 7. Delete a Configuration

```bash
python -m src.caas.cli config delete \
  --app-name my_app \
  --env DEVELOPMENT
```

Confirm with `y` when prompted.

---

## API Usage

### Using cURL

#### Generate Token

```bash
curl -X POST http://127.0.0.1:12500/cass/auth/token
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

#### Create Configuration

```bash
curl -X POST http://127.0.0.1:12500/cass/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "app_name": "my_app",
    "environment_type": "DEVELOPMENT",
    "values": {
      "DB_NAME": "my_db",
      "DB_PASSWORD": "admin@123#",
      "API_KEY": "secret-key"
    }
  }'
```

#### Get Configuration

```bash
curl http://127.0.0.1:12500/cass/get/my_app \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Update Configuration

Replace entire values (PUT):

```bash
curl -X PUT http://127.0.0.1:12500/cass/update \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "app_name": "my_app",
    "environment_type": "DEVELOPMENT",
    "values": {
      "DB_NAME": "new_db",
      "DB_PASSWORD": "newpass"
    }
  }'
```

Partial update (merge specific keys):

```bash
curl -X PATCH http://127.0.0.1:12500/cass/update/partial \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "app_name": "my_app",
    "environment_type": "DEVELOPMENT",
    "values": {
      "API_KEY": "new-key-value"
    }
  }'
```

#### List Configurations (Paginated)

```bash
curl "http://127.0.0.1:12500/cass/get/paginated?page=1&limit=10&search=my" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:

```json
{
  "items": [...],
  "total": 1,
  "page": 1,
  "limit": 10,
  "pages": 1
}
```

#### Delete Configuration

```bash
curl -X DELETE http://127.0.0.1:12500/cass/delete \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "app_name": "my_app",
    "environment_type": "DEVELOPMENT"
  }'
```

---

## CLI Usage

### Commands Reference

#### Authentication

```bash
# Generate and save token
caas auth generate-token

# Show current token
caas auth show

# Remove stored token
caas auth logout
```

#### Configuration Management

```bash
# Create from inline JSON
caas config create \
  --app-name myapp \
  --env DEVELOPMENT \
  --inline '{"KEY":"value"}'

# Create from JSON file
caas config create \
  --app-name myapp \
  --env DEVELOPMENT \
  --values config.json

# Get configuration
caas config get myapp --env DEVELOPMENT

# Update entire configuration
caas config update \
  --app-name myapp \
  --env DEVELOPMENT \
  --values new_config.json

# Partial update (merge)
caas config update \
  --app-name myapp \
  --env DEVELOPMENT \
  --inline '{"KEY":"new_value"}' \
  --partial

# List configurations
caas config list --page 1 --limit 20 --search myapp --env DEVELOPMENT

# Delete configuration
caas config delete --app-name myapp --env DEVELOPMENT
```

### Using a JSON File

Create `config.json`:

```json
{
  "DB_HOST": "localhost",
  "DB_PORT": "5432",
  "DB_NAME": "mydb",
  "DB_USER": "admin",
  "DB_PASSWORD": "secret"
}
```

Use in CLI:

```bash
caas config create --app-name my_app --env DEVELOPMENT --values config.json
```

---

## Troubleshooting

### Connection Refused

**Error:** `Connection failed. Is the API running?`

**Solution:** Make sure the API server is running:

```bash
python -m src.caas.main
```

### Invalid Token

**Error:** `No token stored` or token expired

**Solution:** Generate a new token:

```bash
caas auth generate-token
```

### Database Locked

**Error:** `database is locked`

**Solution:** This can happen with SQLite. Usually temporary. Wait a moment and retry.

### Port Already in Use

**Error:** `Address already in use`

**Solution:** Change the port in `.env`:

```
PORT=12501
```

Then restart the server.

### Invalid Environment Variable

**Error:** `Invalid encryption key format`

**Solution:** Ensure `ENCRYPTION_KEY` is a valid Fernet key:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy the output to `.env` and restart.

### Permission Denied on CLI

**Error:** `Permission denied` on `~/.caas/token`

**Solution:** Fix permissions:

```bash
chmod 600 ~/.caas/token
```

---

## Next Steps

1. **Run Tests:** `pytest` to verify everything works
2. **Explore API Docs:** Open http://127.0.0.1:12500/docs in a browser
3. **Read SECURITY.md:** Understand security considerations
4. **Check CONTRIBUTING.md:** Get involved in development

---

## Getting Help

- Check [SECURITY.md](SECURITY.md) for security questions
- See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
- Open an issue on GitHub for bugs
- Check existing issues for common problems

---

## Common Workflows

### Workflow: Development Environment Setup

```bash
# Create app config for local development
caas config create \
  --app-name backend \
  --env DEVELOPMENT \
  --values dev_config.json

# Where dev_config.json contains:
# {
#   "DB_HOST": "localhost",
#   "DB_PORT": "5432",
#   "API_DEBUG": "true",
#   "LOG_LEVEL": "DEBUG"
# }
```

### Workflow: Managing Multiple Environments

```bash
# Create DEVELOPMENT config
caas config create \
  --app-name myapp \
  --env DEVELOPMENT \
  --values dev_config.json

# Create STAGING config
caas config create \
  --app-name myapp \
  --env STAGING \
  --values staging_config.json

# Create PRODUCTION config
caas config create \
  --app-name myapp \
  --env PRODUCTION \
  --values prod_config.json

# Retrieve based on environment
caas config get myapp --env STAGING
```

### Workflow: Updating Credentials

```bash
# Only update specific values
caas config update \
  --app-name myapp \
  --env PRODUCTION \
  --inline '{"DB_PASSWORD":"new-secure-password"}' \
  --partial
```

---

Enjoy using Config-as-a-Service! 🚀
