import json
import redis

from config.config import settings


try:
    redis_client = redis.Redis(
        host=getattr(settings, "REDIS_HOST", "localhost"),
        port=int(getattr(settings, "REDIS_PORT", 6379)),
        password=getattr(settings, "REDIS_PASSWORD", None),
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2,
    )

    redis_client.ping()
    REDIS_AVAILABLE = True

except Exception:
    redis_client = None
    REDIS_AVAILABLE = False


def get_cache(key: str):
    if not REDIS_AVAILABLE or redis_client is None:
        return None

    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
        return None

    except Exception:
        return None


def set_cache(key: str, value, expire: int = 60):
    if not REDIS_AVAILABLE or redis_client is None:
        return None

    try:
        redis_client.setex(
            key,
            expire,
            json.dumps(value, default=str)
        )
    except Exception:
        return None


def delete_cache(key: str):
    if not REDIS_AVAILABLE or redis_client is None:
        return None

    try:
        redis_client.delete(key)
    except Exception:
        return None