# Placeholder for CRUD operations 
from sqlalchemy.orm import Session
from .models import RequestLog, CustomResponse, User
import json

def create_request_log(db: Session, method: str, path: str, headers: dict, body: str, client_ip: str = None, origin: str = None):
    db_log = RequestLog(
        method=method,
        path=path,
        headers=json.dumps(headers),
        body=body,
        client_ip=client_ip,
        origin=origin
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_latest_request_logs(db: Session, limit: int = 20):
    return db.query(RequestLog).order_by(RequestLog.timestamp.desc()).limit(limit).all()

def upsert_custom_response(db: Session, method: str, path: str, status: int, headers: dict, body: str, delay: int = 0):
    obj = db.query(CustomResponse).filter_by(method=method, path=path).first()
    if obj:
        obj.status = status
        obj.headers = json.dumps(headers)
        obj.body = body
        obj.delay = delay
    else:
        obj = CustomResponse(
            method=method,
            path=path,
            status=status,
            headers=json.dumps(headers),
            body=body,
            delay=delay
        )
        db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def get_custom_response(db: Session, method: str, path: str):
    obj = db.query(CustomResponse).filter_by(method=method, path=path).first()
    return obj

def load_all_custom_responses(db: Session):
    return db.query(CustomResponse).all()

def update_request_log_response(db: Session, log_id: int, status: int, headers: dict, body: str, response_time_ms: int):
    log = db.query(RequestLog).filter_by(id=log_id).first()
    if log:
        log.response_status = status
        log.response_headers = json.dumps(headers)
        log.response_body = body
        log.response_time_ms = response_time_ms
        db.commit()
        db.refresh(log)
    return log

# User CRUD
def create_user(db: Session, username: str, password: str):
    user = User(username=username, password_hash=User.hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter_by(username=username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if user and user.verify_password(password):
        return user
    return None 