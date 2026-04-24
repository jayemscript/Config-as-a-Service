# Config-as-a-Service (CaaS)

Config-as-a-Service is a lightweight, self-hostable API for centralized application configuration. It lets services fetch and manage environment variables, feature flags, and runtime settings via HTTP or CLI, replacing scattered .env files and enabling consistent, dynamic config across apps without redeployment.

## Overview

CaaS provides a single source of truth for application configurations across different environments. Instead of managing separate `.env` files for each deployment, services query the CaaS API to retrieve their configuration based on application name and environment type. All data is persisted locally using SQLite with built-in encryption for sensitive values.

## Core Features

### Self-Hosted & Lightweight
- Run entirely on your own infrastructure—no external dependencies
- Lightweight design with minimal resource footprint
- Default runs on port 12500 (configurable if port is already in use)
- Built with FastAPI for high performance and async support

### Encryption & Security
- CMD-based calling with encryption support for sensitive configuration values
- Secure storage of environment variables and credentials
- Encryption-aware value retrieval and management

### Environment Management
- Multi-environment support: **DEVELOPMENT**, **STAGING**, **PRODUCTION**
- Organize configurations by environment type for better control and segregation
- Version tracking for configuration changes over time

### Dynamic Configuration Storage
- Store configurations as flexible JSON key-value pairs
- Supports complex nested configurations and multiple data types
- Examples: database credentials, API keys, feature flags, service URLs, etc.

## Data Model

CaaS uses a single SQLite table with the following structure:

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Unique identifier for each configuration record |
| `app_name` | String (Unique) | Application identifier; each app has one config per environment |
| `environment_type` | Enum | Environment classification: DEVELOPMENT, STAGING, or PRODUCTION |
| `values` | JSON | Key-value pairs containing the actual configuration (encrypted) |
| `version` | Integer | Incremental version counter for tracking configuration changes |
| `created_at` | Timestamp | Record creation timestamp |
| `updated_at` | Timestamp | Last modification timestamp |

### Configuration Values Example
```json
{
  "DB_NAME": "my_db",
  "DB_PASSWORD": "admin@123#",
  "DB_PORT": "5432",
  "API_KEY": "secret-key-here",
  "DEBUG_MODE": "false"
}