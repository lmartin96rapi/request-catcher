# Request Catcher - FastAPI + SQLite + Plain HTML

## 🚀 Project Overview

**Goal:** Create a Request Catcher application to:

- Accept any incoming HTTP request (any path, any method)
- Store request details in SQLite database
- Display captured requests in a simple frontend
- Avoid changes to existing Django webhook consumers by providing a custom endpoint for testing

---

## 🔢 Project Structure

```
request-catcher/
├── app/
│   ├── main.py         # FastAPI server and routes
│   ├── db.py           # SQLite DB connection
│   ├── models.py       # RequestLog model definition
│   └── crud.py         # DB operations (insert, fetch)
├── static/
│   └── index.html      # Frontend UI to show captured requests
├── requirements.txt    # Python dependencies
└── README.md
```

---

## 🛠️ Technologies Used

- **FastAPI** — Lightweight, async web server
- **SQLite** — Embedded database for local storage
- **SQLAlchemy** — ORM for interacting with the database
- **Plain HTML + JS** — Frontend to view requests
- **Uvicorn** — ASGI server for running FastAPI
- **Docker** -- Needs to be dockerized

---

## 🌐 Core Features

### Backend

- Accepts **any HTTP request** on any route using wildcard matching
- Logs the following request details:
  - HTTP method
  - Path
  - Headers
  - Body
  - Timestamp
- Provides API to:
  - `GET /requests` ➔ Fetch latest stored requests
- Serves static frontend at `/static/index.html`

### Frontend

- Plain HTML/JS app
- Fetches captured requests every few seconds
- Displays requests in a readable format

---

## 💡 How It Works

1. Run the FastAPI app
2. Configure external services (e.g., Django webhooks) to point to this server:
   ```
   http://localhost:8000/any/path
   ```
3. Incoming requests are captured and stored in SQLite
4. Visit `http://localhost:8000/static/index.html` to view live request logs

---

## 📈 Example Database Record

| id | method | path       | headers (JSON) | body  | timestamp           |
| -- | ------ | ---------- | -------------- | ----- | ------------------- |
| 1  | POST   | /test/path | {...}          | {...} | 2025-07-02 13:00:00 |

---

## 📅 Future Enhancements

- Add WebSocket for real-time updates
- Filter or search captured requests
- Export logs as JSON
- Persist logs beyond in-memory limits (handled by SQLite now)

---

## 🔧 Setup & Run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```
3. Access frontend:
   ```
   http://localhost:8000/static/index.html
   ```
4. Test with requests:
   ```bash
   curl -X POST http://localhost:8000/my/webhook -d '{"test": 123}'
   ```

---

## 💪 Why This is Useful

- Non-intrusive — You don't modify existing Django webhook consumers
- Self-contained — Everything runs locally, no external DB setup
- Flexible — Easily extendable for more advanced features
- Reliable — SQLite provides persistence across restarts

---

## 📲 Next Steps

After setup, incoming requests from your Django app will appear in the frontend UI for easy debugging and inspection.

---

**End of Project Plan**

