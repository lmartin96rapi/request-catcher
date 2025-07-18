from fastapi import FastAPI, Request, Response, Body, Depends, HTTPException, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from .db import SessionLocal
from .crud import create_request_log, get_latest_request_logs, upsert_custom_response, get_custom_response, load_all_custom_responses, update_request_log_response, authenticate_user, create_user, get_user_by_username
import asyncio
from fastapi.middleware.cors import CORSMiddleware
import datetime
from typing import Dict, Any
import threading
import json
import time
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from datetime import timedelta

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

custom_responses_lock = threading.Lock()
custom_responses: Dict[tuple, Dict[str, Any]] = {}

SECRET_KEY = "your-secret-key"  # Change this to a secure value
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user_jwt(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    db = SessionLocal()
    user = get_user_by_username(db, username)
    db.close()
    if user is None:
        raise credentials_exception
    return user

def reload_custom_responses():
    db = SessionLocal()
    all_configs = load_all_custom_responses(db)
    db.close()
    with custom_responses_lock:
        custom_responses.clear()
        for conf in all_configs:
            custom_responses[(conf.method.upper(), conf.path)] = {
                "status": conf.status,
                "headers": json.loads(conf.headers),
                "body": conf.body or "",
                "delay": conf.delay
            }

# Load configs on startup
reload_custom_responses()

def get_real_ip(request):
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else None

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    user = authenticate_user(db, form_data.username, form_data.password)
    db.close()
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/requests")
def fetch_requests(user=Depends(get_current_user_jwt)):
    db = SessionLocal()
    logs = get_latest_request_logs(db)
    db.close()
    return [
        {
            "id": log.id,
            "method": log.method,
            "path": log.path,
            "headers": log.headers,
            "body": log.body,
            "timestamp": log.timestamp.replace(tzinfo=datetime.timezone.utc).isoformat() if log.timestamp.tzinfo is None else log.timestamp.astimezone(datetime.timezone.utc).isoformat(),
            "client_ip": getattr(log, "client_ip", None),
            "origin": getattr(log, "origin", None),
            "response_status": getattr(log, "response_status", None),
            "response_headers": getattr(log, "response_headers", None),
            "response_body": getattr(log, "response_body", None),
            "response_time_ms": getattr(log, "response_time_ms", None)
        }
        for log in logs
    ]

@app.post("/configure-response")
def configure_response(
    method: str = Body(...),
    path: str = Body(...),
    status: int = Body(200),
    headers: dict = Body({}),
    body: str = Body(""),
    delay: int = Body(0),
    user=Depends(get_current_user_jwt)
):
    db = SessionLocal()
    upsert_custom_response(db, method.upper(), path, status, headers, body, delay)
    db.close()
    reload_custom_responses()
    return {"message": "Configured", "for": {"method": method.upper(), "path": path}}

@app.get("/custom-responses")
def list_custom_responses(user=Depends(get_current_user_jwt)):
    db = SessionLocal()
    all_configs = load_all_custom_responses(db)
    db.close()
    return [
        {
            "method": conf.method,
            "path": conf.path,
            "status": conf.status,
            "headers": json.loads(conf.headers),
            "body": conf.body or "",
            "delay": conf.delay
        }
        for conf in all_configs
    ]

@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
async def catch_all(request: Request, full_path: str):
    # Filter out unwanted paths
    ignored_paths = ["favicon.ico", "requests", "configure-response", "custom-responses"]
    if full_path in ignored_paths:
        return Response(status_code=204)
    db = SessionLocal()
    body = await request.body()
    client_ip = get_real_ip(request)
    origin = request.headers.get("origin")
    log = create_request_log(
        db,
        method=request.method,
        path="/" + full_path,
        headers=dict(request.headers),
        body=body.decode(errors="replace"),
        client_ip=client_ip,
        origin=origin
    )
    db.commit()
    db.refresh(log)
    db.close()
    start = time.perf_counter()
    
    key = (request.method.upper(), "/" + full_path)
    with custom_responses_lock:
        conf = custom_responses.get(key)
    delay = conf["delay"] if conf and "delay" in conf else 0
    if delay:
        await asyncio.sleep(delay)
    if conf:
        status = conf["status"]
        headers = conf["headers"]
        resp_body = conf["body"]
        resp = Response(content=resp_body, status_code=status, headers=headers)
    else:
        status = 200
        headers = {}
        resp_body = "{\"status\": \"captured\"}"
        resp = JSONResponse({"status": "captured"})
    elapsed = int((time.perf_counter() - start) * 1000)
    db = SessionLocal()
    update_request_log_response(db, log.id, status, headers, resp_body, elapsed)
    db.close()
    return resp 

@app.post("/create-user")
def create_user_endpoint(username: str = Body(...), password: str = Body(...), user=Depends(get_current_user_jwt)):
    db = SessionLocal()
    if db.query(type(user)).filter_by(username=username).first():
        db.close()
        raise HTTPException(status_code=400, detail="Username already exists")
    new_user = create_user(db, username, password)
    db.close()
    return {"message": f"User {username} created"} 