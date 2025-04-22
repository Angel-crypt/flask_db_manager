import os
import bcrypt
import jwt as pyjwt
from datetime import datetime, timedelta
from services.db_client import DBClient
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
EXP_HOURS = int(os.getenv("JWT_EXP_HOURS", 24))

def hash_password(raw_pw: str) -> str:
    return bcrypt.hashpw(raw_pw.encode(), bcrypt.gensalt()).decode()

def verify_password(raw_pw: str, hashed: str) -> bool:
    return bcrypt.checkpw(raw_pw.encode(), hashed.encode())

def register_user(data: dict) -> int:
    data = data.copy()
    data["password_hash"] = hash_password(data.pop("password"))
    data.setdefault("role", "user")
    return DBClient.create_user(data)

def authenticate(email: str, password: str):
    user = DBClient.get_user_by_email(email)
    if not user or not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return None

    payload = {
        "user_id": user["id"],
        "role":    user["role"],
        "exp":     datetime.utcnow() + timedelta(hours=EXP_HOURS)
    }
    token = pyjwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {
        "token": token,
        "user":  {k: user[k] for k in ("id", "name", "email", "role")}
    }

def decode_token(token: str):
    try:
        return pyjwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except pyjwt.PyJWTError:
        return None