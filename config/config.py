import os
from dotenv import load_dotenv

#  Load .env file
load_dotenv()


class Settings:
    # ================= SECURITY =================
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    ADMIN_JWT_SECRET_KEY: str = os.getenv("ADMIN_JWT_SECRET_KEY")
    VENDOR_JWT_SECRET_KEY: str = os.getenv("VENDOR_JWT_SECRET_KEY")

    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # ================= DATABASE =================
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    # ================= REDIS =================
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))

    # ================= ENV =================
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")


settings = Settings()