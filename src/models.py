import reflex as rx
from sqlmodel import Field,  Relationship
import bcrypt
from datetime import datetime, timedelta

# Security Helpers
def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_bytes = plain_password.encode('utf-8')
    hash_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(pwd_bytes, hash_bytes)

def hash_token(token: str) -> str:
    """Hash a session token for secure storage"""
    token_bytes = token.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(token_bytes, salt)
    return hashed.decode('utf-8')

def verify_token(plain_token: str, hashed_token: str) -> bool:
    """Verify a plain token against its hashed version"""
    token_bytes = plain_token.encode('utf-8')
    hash_bytes = hashed_token.encode('utf-8')
    return bcrypt.checkpw(token_bytes, hash_bytes)

# Database Model
class User(rx.Model, table=True):
    username: str = Field(unique=True, index=True)
    password_hash: str
    failed_attempts: int = 0
    locked_until: datetime | None = None

class AuthSession(rx.Model, table=True):
    user_id: int = Field(foreign_key="user.id")
    token: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime

class ChatThread(rx.Model, table=True):
    user_id: int = Field(foreign_key="user.id")
    title: str = "New Chat"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    messages: list["Message"] = Relationship(
        back_populates="thread",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

class Message(rx.Model, table=True):
    thread_id: int = Field(foreign_key="chatthread.id")
    text: str
    is_user: bool  # True = User, False = AI
    created_at: datetime = Field(default_factory=datetime.utcnow)
    thread: "ChatThread" = Relationship(back_populates="messages")
