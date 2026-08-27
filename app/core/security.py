from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.core import get_settings

JWT_ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    bytes_pass: bytes = password.encode("utf-8")
    salt: bytes = bcrypt.gensalt()
    hashed_password: bytes = bcrypt.hashpw(bytes_pass, salt)
    return hashed_password.decode("utf-8")


def check_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def encode_access_token(user_email: str) -> str:
    settings = get_settings()
    jwt_lifetime_minutes = settings.jwt_lifetime_minutes
    jwt_secret = settings.jwt_secret
    payload = {"type": "access", "sub": user_email, "exp": datetime.now(UTC) + timedelta(minutes=jwt_lifetime_minutes)}
    access_token = jwt.encode(payload, key=jwt_secret, algorithm=JWT_ALGORITHM)
    return access_token


def encode_refresh_token(user_email: str) -> str:
    settings = get_settings()
    jwt_refresh_lifetime_seconds = settings.jwt_refresh_lifetime_seconds
    jwt_refresh_secret = settings.jwt_refresh_secret
    payload = {
        "type": "refresh",
        "sub": user_email,
        "exp": datetime.now(UTC) + timedelta(seconds=jwt_refresh_lifetime_seconds),
    }
    refresh_token = jwt.encode(payload, key=jwt_refresh_secret, algorithm=JWT_ALGORITHM)
    return refresh_token


def decode_access_token(access_token: str) -> dict | None:
    jwt_secret = get_settings().jwt_secret

    try:
        payload = jwt.decode(access_token, key=jwt_secret, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


def decode_refresh_token(refresh_token: str) -> dict | None:
    jwt_refresh_secret = get_settings().jwt_refresh_secret

    try:
        payload = jwt.decode(refresh_token, key=jwt_refresh_secret, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None
