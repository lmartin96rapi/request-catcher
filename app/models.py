# NOTE: If you change the schema, delete request_logs.db to apply changes, or use a migration tool.
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
import datetime
from passlib.hash import bcrypt

Base = declarative_base()

class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, index=True)
    method = Column(String, nullable=False)
    path = Column(String, nullable=False)
    headers = Column(Text, nullable=False)  # Store as JSON string
    body = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    response_status = Column(Integer, nullable=True)
    response_headers = Column(Text, nullable=True)  # JSON string
    response_body = Column(Text, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    client_ip = Column(String, nullable=True)  # New: store client IP
    origin = Column(String, nullable=True)     # New: store Origin header

class CustomResponse(Base):
    __tablename__ = "custom_responses"

    id = Column(Integer, primary_key=True, index=True)
    method = Column(String, nullable=False)
    path = Column(String, nullable=False)
    status = Column(Integer, nullable=False, default=200)
    headers = Column(Text, nullable=False, default='{}')  # Store as JSON string
    body = Column(Text, nullable=True)
    delay = Column(Integer, nullable=True, default=0)  # Delay in seconds
    
    # Unique constraint on (method, path) could be added for upsert logic 

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)

    def verify_password(self, password):
        return bcrypt.verify(password, self.password_hash)

    @staticmethod
    def hash_password(password):
        return bcrypt.hash(password) 