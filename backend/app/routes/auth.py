from fastapi import APIRouter, HTTPException

from app.database import get_db
from app.schemas import AuthRequest, TokenResponse
from app.services.security import create_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=TokenResponse)
def signup(payload: AuthRequest):
    with get_db() as db:
        try:
            cursor = db.execute(
                "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                (payload.email.lower(), hash_password(payload.password)),
            )
        except Exception as exc:
            raise HTTPException(status_code=409, detail="An account with this email already exists.") from exc
        user_id = cursor.lastrowid
    user = {"id": user_id, "email": payload.email.lower()}
    return {"token": create_token({"sub": user_id}), "user": user}


@router.post("/login", response_model=TokenResponse)
def login(payload: AuthRequest):
    with get_db() as db:
        row = db.execute("SELECT id, email, password_hash FROM users WHERE email = ?", (payload.email.lower(),)).fetchone()
    if not row or not verify_password(payload.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    user = {"id": row["id"], "email": row["email"]}
    return {"token": create_token({"sub": row["id"]}), "user": user}
