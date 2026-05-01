import jwt
from datetime import datetime, timedelta
from config.config import settings

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM


def create_access_token(data: dict):
    payload = data.copy()
    payload.update({
        "exp": datetime.utcnow() + timedelta(minutes=15),
        "type": "access"
    })
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    payload = data.copy()
    payload.update({
        "exp": datetime.utcnow() + timedelta(days=7),
        "type": "refresh"
    })
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)