# CaaS API Reference

Base URL: `http://localhost:12500`  
You can test any of these endpoints using **Postman**, **curl**, **Insomnia**, or any HTTP client.  
Interactive docs (Swagger UI) are also available at `http://localhost:12500/docs` while the server is running.

---

## Authentication

All endpoints (except `/health` and `/cass/auth/token`) require a **Bearer token** in the header.

**Step 1 — Get a token:**

```http
POST /cass/auth/token
```

```bash
curl -X POST http://localhost:12500/cass/auth/token
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 86400
}
```

**Step 2 — Use the token in all subsequent requests:**

```http
Authorization: Bearer <access_token>
```

---

## Endpoints

### Health Check

```http
GET /health
```

No auth required.

```bash
curl http://localhost:12500/health
```

**Response:**
```json
{ "status": "ok" }
```

---

### Create Configuration

```http
POST /cass/create
```

```bash
curl -X POST http://localhost:12500/cass/create \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "my-app",
    "environment_type": "DEVELOPMENT",
    "values": {
      "DB_HOST": "localhost",
      "DB_PORT": "5432",
      "DEBUG": "true"
    }
  }'
```

**Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `app_name` | string | yes | Unique app identifier |
| `environment_type` | string | yes | `DEVELOPMENT`, `STAGING`, or `PRODUCTION` |
| `values` | object | yes | Key-value config pairs |

**Response `201`:**
```json
{
  "id": "4a0ca9f6-aee1-4e03-bdd3-398dacd09176",
  "app_name": "my-app",
  "environment_type": "DEVELOPMENT",
  "values": { "DB_HOST": "localhost", "DB_PORT": "5432", "DEBUG": "true" },
  "version": 1,
  "created_at": "2026-04-27T00:59:35.445950",
  "updated_at": "2026-04-27T00:59:35.445958"
}
```

---

### Get Configuration

```http
GET /cass/get/{app_name}?environment_type=DEVELOPMENT
```

```bash
curl http://localhost:12500/cass/get/my-app?environment_type=DEVELOPMENT \
  -H "Authorization: Bearer <token>"
```

**Path params:**

| Param | Description |
|-------|-------------|
| `app_name` | The app name used when creating |

**Query params:**

| Param | Required | Description |
|-------|----------|-------------|
| `environment_type` | no | Filter by `DEVELOPMENT`, `STAGING`, or `PRODUCTION`. Returns first match if omitted. |

**Response `200`:**
```json
{
  "id": "4a0ca9f6-aee1-4e03-bdd3-398dacd09176",
  "app_name": "my-app",
  "environment_type": "DEVELOPMENT",
  "values": { "DB_HOST": "localhost", "DB_PORT": "5432", "DEBUG": "true" },
  "version": 1,
  "created_at": "2026-04-27T00:59:35.445950",
  "updated_at": "2026-04-27T00:59:35.445958"
}
```

---

### List All Configurations (Paginated)

```http
GET /cass/get/paginated?page=1&limit=10
```

```bash
curl "http://localhost:12500/cass/get/paginated?page=1&limit=10" \
  -H "Authorization: Bearer <token>"
```

**Query params:**

| Param | Default | Description |
|-------|---------|-------------|
| `page` | `1` | Page number |
| `limit` | `10` | Results per page (max 100) |
| `search` | — | Filter by partial app name |
| `environment_type` | — | Filter by `DEVELOPMENT`, `STAGING`, or `PRODUCTION` |

**Example with filters:**
```bash
curl "http://localhost:12500/cass/get/paginated?page=1&limit=5&search=my&environment_type=PRODUCTION" \
  -H "Authorization: Bearer <token>"
```

**Response `200`:**
```json
{
  "items": [
    {
      "id": "4a0ca9f6-...",
      "app_name": "my-app",
      "environment_type": "DEVELOPMENT",
      "values": { "DB_HOST": "localhost" },
      "version": 1,
      "created_at": "2026-04-27T00:59:35.445950",
      "updated_at": "2026-04-27T00:59:35.445958"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 10,
  "pages": 1
}
```

---

### Full Update Configuration

Replaces **all** values entirely.

```http
PUT /cass/update
```

```bash
curl -X PUT http://localhost:12500/cass/update \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "my-app",
    "environment_type": "DEVELOPMENT",
    "values": {
      "DB_HOST": "prod-server",
      "DB_PORT": "5432",
      "DEBUG": "false"
    }
  }'
```

**Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `app_name` | string | yes | App to update |
| `environment_type` | string | yes | Environment to update |
| `values` | object | yes | New values — replaces everything |

**Response `200`:** Same as Get, with incremented `version`.

---

### Partial Update Configuration

Merges new values with existing — **only updates the keys you specify**, leaves others untouched.

```http
PATCH /cass/update/partial
```

```bash
curl -X PATCH http://localhost:12500/cass/update/partial \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "my-app",
    "environment_type": "DEVELOPMENT",
    "values": {
      "DEBUG": "false"
    }
  }'
```

**Response `200`:** Returns full merged config with incremented `version`.

---

### Delete Configuration

```http
DELETE /cass/delete
```

```bash
curl -X DELETE http://localhost:12500/cass/delete \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "my-app",
    "environment_type": "DEVELOPMENT"
  }'
```

**Response `200`:**
```json
{
  "message": "Configuration 'my-app' deleted successfully"
}
```

---

## Environment Types

| Value | Use for |
|-------|---------|
| `DEVELOPMENT` | Local dev machines |
| `STAGING` | Pre-production / QA |
| `PRODUCTION` | Live deployments |

Each `app_name` + `environment_type` combination is unique — one config record per app per environment.

---

## Error Responses

| Status | Meaning |
|--------|---------|
| `401` | Missing or invalid token |
| `404` | Config not found |
| `409` | Config already exists (on create) |
| `500` | Internal server error |

```json
{ "detail": "Configuration 'my-app' not found" }
```

---

## Postman Quick Setup

1. Create a new collection called **CaaS**
2. Add a collection-level variable `base_url` = `http://localhost:12500`
3. Add a collection-level variable `token` = *(leave blank for now)*
4. Create a request `POST {{base_url}}/cass/auth/token` and add this to the **Tests** tab:
   ```javascript
   pm.collectionVariables.set("token", pm.response.json().access_token);
   ```
5. On all other requests, set **Auth** → **Bearer Token** → `{{token}}`
6. Run the token request once — all other requests will use it automatically.