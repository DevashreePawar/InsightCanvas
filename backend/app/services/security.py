import base64
import hashlib
import hmac
import json
import os
import time
from typing import Any, Dict

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import SECRET_KEY
from app.database import get_db

auth_scheme = HTTPBearer()


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return f"{base64.urlsafe_b64encode(salt).decode()}:{base64.urlsafe_b64encode(digest).decode()}"


def verify_password(password: str, stored_hash: str) -> bool:
    salt_b64, digest_b64 = stored_hash.split(":")
    salt = base64.urlsafe_b64decode(salt_b64.encode())
    expected = base64.urlsafe_b64decode(digest_b64.encode())
    actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return hmac.compare_digest(actual, expected)


def create_token(payload: Dict[str, Any]) -> str:
    body = {**payload, "exp": int(time.time()) + 60 * 60 * 24}
    encoded = base64.urlsafe_b64encode(json.dumps(body).encode()).decode()
    signature = hmac.new(SECRET_KEY.encode(), encoded.encode(), hashlib.sha256).hexdigest()
    return f"{encoded}.{signature}"


def decode_token(token: str) -> Dict[str, Any]:
    try:
        encoded, signature = token.split(".", 1)
        expected = hmac.new(SECRET_KEY.encode(), encoded.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError("Invalid signature")
        payload = json.loads(base64.urlsafe_b64decode(encoded.encode()).decode())
        if payload.get("exp", 0) < int(time.time()):
            raise ValueError("Expired token")
        return payload
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc


def current_user(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    payload = decode_token(credentials.credentials)
    with get_db() as db:
        user = db.execute("SELECT id, email FROM users WHERE id = ?", (payload["sub"],)).fetchone()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return {"id": user["id"], "email": user["email"]}
