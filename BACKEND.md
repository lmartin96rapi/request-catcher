# Request Catcher Backend

## Purpose

The Request Catcher backend is a FastAPI-based service designed to capture, log, and simulate HTTP requests for debugging, integration testing, and webhook development. It allows developers and testers to inspect incoming requests, configure custom responses, and analyze HTTP traffic in a local, self-contained environment.

## Architecture

- **Framework:** FastAPI (Python)
- **Database:** SQLite (via SQLAlchemy ORM)
- **Server:** Uvicorn (ASGI)
- **Static Files:** Serves a simple frontend UI at `/static/index.html`
- **Dockerized:** Ready for containerized deployment

### Main Features
- Accepts any HTTP request on any path and method
- Logs request details: method, path, headers, body, timestamp, client IP, and origin
- Allows configuration of custom responses per route/method (status, headers, body, delay)
- Provides API endpoints to fetch logs and manage custom responses

---

## API Documentation

### 1. `GET /requests`
Fetch the latest captured requests.

**Response:**
```json
[
  {
    "id": 1,
    "method": "POST",
    "path": "/test/path",
    "headers": "{...}",
    "body": "...",
    "timestamp": "2024-07-02T13:00:00Z",
    "client_ip": "203.0.113.42",
    "origin": "https://example.com"
  },
  ...
]
```
- `headers` is a JSON string of the request headers.
- `client_ip` is the real client IP (uses X-Forwarded-For if behind a proxy).
- `origin` is the Origin header if present, otherwise null.

---

### 2. `POST /configure-response`
Configure a custom response for a given method and path.

**Request Body (JSON):**
```json
{
  "method": "POST",
  "path": "/webhook",
  "status": 200,
  "headers": {"Content-Type": "application/json"},
  "body": "{\"ok\":true}",
  "delay": 0
}
```
- `method`: HTTP method (e.g., GET, POST)
- `path`: Route to match (must start with `/`)
- `status`: HTTP status code to return
- `headers`: Response headers (object)
- `body`: Response body (string)
- `delay`: Delay in seconds before responding (optional)

**Response:**
```json
{
  "message": "Configured",
  "for": {"method": "POST", "path": "/webhook"}
}
```

---

### 3. `GET /custom-responses`
List all configured custom responses.

**Response:**
```json
[
  {
    "method": "POST",
    "path": "/webhook",
    "status": 200,
    "headers": {"Content-Type": "application/json"},
    "body": "{\"ok\":true}",
    "delay": 0
  },
  ...
]
```

---

### 4. `/{full_path:path}` (Catch-all endpoint)
Accepts any HTTP request on any path and method. Logs the request and returns either a configured custom response or a default JSON response.

- **Methods:** GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD
- **Path:** Any (except reserved API paths)

**Behavior:**
- Logs method, path, headers, body, timestamp, client IP, and origin.
- If a custom response is configured for the method/path, returns it (with optional delay).
- Otherwise, returns `{ "status": "captured" }` (HTTP 200).

---

## Database Schema (RequestLog)
| Field         | Type    | Description                       |
|---------------|---------|-----------------------------------|
| id            | int     | Primary key                       |
| method        | string  | HTTP method                       |
| path          | string  | Request path                      |
| headers       | text    | JSON string of headers            |
| body          | text    | Request body                      |
| timestamp     | datetime| Time received (UTC)               |
| client_ip     | string  | Real client IP (from proxy/header)|
| origin        | string  | Origin header (if present)        |
| response_*    | ...     | Response status, headers, body, ms|

---

## Usage Notes
- The backend is stateless except for the SQLite DB (`request_logs.db`).
- If you change the schema, delete the DB or use a migration tool.
- For accurate client IPs behind a proxy, ensure `X-Forwarded-For` is set by your proxy (e.g., nginx).
- Static frontend is served at `/static/index.html`.

---

## Example: Capturing a Request
```bash
curl -X POST http://localhost:8086/my/webhook -d '{"foo": "bar"}' -H 'Content-Type: application/json' -H 'Origin: https://example.com'
```

---

## License & Contributions
MIT License. Contributions welcome! 