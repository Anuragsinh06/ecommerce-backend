# Common functions
# Common functions
# Common functions
# Common functions
import hashlib
import hmac
import sys
import traceback
import re
import time
import secrets
import string
from pathlib import Path
import math

import certifi
import httpx

import requests
from contextlib import asynccontextmanager
import logging
from datetime import timedelta, datetime, timezone
import pyotp
import contextvars
from fastapi import FastAPI, Depends, HTTPException, status, Request, Header
from fastapi.exceptions import RequestValidationError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from config.config import settings
from .common_response import errorResponse, HEC_400, HEC_401, HEM_UNAUTHORIZED, successResponse, HSC_200
import bcrypt
from  shared.db import db
import bcrypt
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from aiosmtplib import SMTP
import smtplib
import ssl
import os
from dotenv import load_dotenv
load_dotenv()

from .scheduler import scheduler


security = HTTPBearer()


logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger("auth-service")
# payment_logger = logging.getLogger("payment-service")

FROM_EMAIL = os.getenv("FROM_EMAIL")
ZEPTO_BASE_URL = os.getenv("ZEPTO_BASE_URL")
ZEPTO_TOKEN = os.getenv("ZEPTO_TOKEN")

# Context variable to store client IP for logging
client_ip_var = contextvars.ContextVar("client_ip", default="-")

class IPFilter(logging.Filter):
    def filter(self, record):
        record.client_ip = client_ip_var.get()
        return True

class ColoredFormatter(logging.Formatter):
    def __init__(self, use_color=True):
        self.use_color = use_color
        self.white = "\x1b[37m"
        self.yellow = "\x1b[33m"
        self.reset = "\x1b[0m"

    def format(self, record):
        # Default IP if not set
        client_ip = getattr(record, "client_ip", "-")
        
        # Select color based on log level
        level_color = {
            logging.DEBUG: "\x1b[35m",     # Magenta
            logging.INFO: "\x1b[32m",      # Green
            logging.WARNING: "\x1b[33m",   # Yellow
            logging.ERROR: "\x1b[31m",     # Red
            logging.CRITICAL: "\x1b[41m\x1b[37m", # Red background, white text
        }.get(record.levelno, "\x1b[37m")

        # Format: Date - [IP] - [Logger] - Level - Message
        # We use yellow for the IP as requested
        log_fmt = f"{level_color}%(asctime)s{self.reset} - {self.yellow}[{client_ip}]{self.reset} - {self.white}[%(name)s]{self.reset} - {level_color}%(levelname)s - %(message)s"
        
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

import os
from logging.handlers import TimedRotatingFileHandler

# Create logs directory if it doesn't exist
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logger(name):
    root_logger = logging.getLogger()
    
    if not hasattr(root_logger, "_custom_handlers_set"):
        # Remove any existing handlers to start fresh (prevents duplication with uvicorn/standard handlers)
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
                
        # Add Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(ColoredFormatter())
        console_handler.addFilter(IPFilter())
        root_logger.addHandler(console_handler)

        # Add File Handler
        try:
            log_dir = Path(LOG_DIR)
            log_dir.mkdir(exist_ok=True)
            file_handler = TimedRotatingFileHandler(
                filename=log_dir / "app.log",
                when="midnight",
                interval=1,
                backupCount=7,
                encoding="utf-8"
            )
            # IP is yellow in file too if we want, but usually plain is better for files. 
            # However, the user asked for "yellow" so I'll put it in the formatter.
            file_formatter = logging.Formatter("%(asctime)s - [%(client_ip)s] - [%(name)s] - %(levelname)s - %(message)s")
            file_handler.setFormatter(file_formatter)
            file_handler.addFilter(IPFilter())
            root_logger.addHandler(file_handler)
        except Exception as e:
            print(f"Error setting up file logging: {e}")

        root_logger.setLevel(logging.INFO)
        root_logger._custom_handlers_set = True
        
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = True
    
    # Ensure child logger also has the IP filter so it can provide the IP to parent handlers
    if not any(isinstance(f, IPFilter) for f in logger.filters):
        logger.addFilter(IPFilter())
    
    return logger

from pydantic import BaseModel, field_validator

class SecurityBaseModel(BaseModel):
    @field_validator("*", mode="before")
    @classmethod
    def validate_security(cls, v):
        return validate_json_security(v)

def validate_json_security(data):
    """
    Recursively check a dictionary or list for any string values containing
    HTML, CSS, JS, or XML-like tags to prevent malicious code injection.
    """
    if isinstance(data, dict):
        for k, v in data.items():
            validate_json_security(k)
            validate_json_security(v)
    elif isinstance(data, list):
        for item in data:
            validate_json_security(item)
    elif isinstance(data, str):
        # Prevent HTML, XML, script tags, etc. using a strict regex
        if re.search(r"<[^>]*[a-zA-Z]+[^>]*>", data):
            raise ValueError(f"Malicious code (HTML/Script) detected in input")
        
        # Check for javascript: execution context
        if re.search(r"javascript\s*:", data, re.IGNORECASE):
            raise ValueError(f"Javascript execution context detected in input")
    return data

def process_db_response(res, fallback_error_msg, fallback_success_msg="Success"):
    check_res = res[0] if isinstance(res, list) and len(res) > 0 else res
    
    if not check_res or (isinstance(check_res, dict) and check_res.get('msgcode', '').lower() == "fail"):
        error_msg = check_res.get("msg") if isinstance(check_res, dict) and check_res.get("msg") else fallback_error_msg
        return errorResponse(HEC_400, error_msg)
        
    msg = check_res.get("msg", fallback_success_msg) if isinstance(check_res, dict) else fallback_success_msg
    return successResponse(HSC_200, msg, res)

# Active logger for shared library use (like db.py)
_active_logger = None

def set_active_logger(logger_instance):
    global _active_logger
    _active_logger = logger_instance

def get_active_logger():
    global _active_logger
    if _active_logger:
        return _active_logger
    return logger # fallback to thetimemachine

# Initialize fallback loggers after setup_logger is defined
logger = setup_logger("Ecommerce")
# payment_logger = setup_logger("payment-service")

def _get_peppered_password(password: str) -> bytes:
    # Use HMAC-SHA256 to hash the password with the secret key first (Pepper)
    secret = settings.SECRET_KEY.encode('utf-8')
    return hmac.new(secret, password.encode('utf-8'), hashlib.sha256).hexdigest().encode('utf-8')

def hash_password(password: str) -> str:
    # Create peppered password bytes
    pwd_bytes = _get_peppered_password(password)
    # Hash with bcrypt
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')
def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        # 1. Validation: If the DB has plain text or is empty, skip bcrypt
        if not hashed_password or not hashed_password.startswith('$'):
            logger.warning("Verify_password: Stored hash is missing or not a valid bcrypt format.")
            return False

        # 2. Preparation: Get the peppered bytes for the input password
        # Ensure _get_peppered_password returns bytes
        password_byte_enc = _get_peppered_password(plain_password)
        
        # 3. Encoding: Convert stored string hash to bytes
        hashed_password_byte_enc = hashed_password.encode('utf-8')
        
        # 4. Comparison
        return bcrypt.checkpw(password_byte_enc, hashed_password_byte_enc)

    except ValueError as ve:
        # This catches "Invalid salt" specifically
        logger.error(f"Bcrypt verification failed (Invalid Salt): {ve}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in verify_password: {e}")
        return False

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        decoded_token = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return decoded_token
    except jwt.ExpiredSignatureError:
        # Token has expired
        return None
    except jwt.InvalidTokenError:
        # Invalid token
        return None

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials

        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        return {
            "user_id": payload.get("user_id"),
            "role": payload.get("role")   # 🔥 IMPORTANT
        }

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_admin_user(current_user=Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to database
    logger.info("Starting up: Connecting to database pool...")
    await db.connect()
    
    # Start the background scheduler
    logger.info("Starting background scheduler...")
    scheduler.start()
    
    # Run once immediately on startup
    from .scheduler import expire_campaigns
    await expire_campaigns()
    
    yield
    
    # Shutdown: Stop the background scheduler
    logger.info("Shutting down background scheduler...")
    scheduler.shutdown()
    
    # Shutdown: Disconnect from database
    logger.info("Shutting down: Closing database pool...")
    await db.disconnect()

async def validation_exception_handler(request, exc: RequestValidationError):
    # Extract the first error message
    errors = exc.errors()
    if errors:
        # Get the first error message and field
        msg = errors[0].get("msg", "Validation error")
        field = errors[0]['loc'][-1]
        full_msg = f"Invalid {field}: {msg}"
    else:
        full_msg = "Validation error"
        
    return errorResponse(HEC_400, full_msg) 

async def custom_http_exception_handler(request, exc: HTTPException):
    return errorResponse(exc.status_code, exc.detail)

async def global_exception_handler(request: Request, exc: Exception):
    error_msg = f"Internal Server Error on {request.url.path}: {str(exc)}\n{traceback.format_exc()}"
    logger.error(error_msg)
    return errorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal Server Error")

def verify_2fa_code(secret, code):
    totp = pyotp.TOTP(secret)
    return totp.verify(code)

def generate_temp_token(data: dict):
    """
    Generate a temporary token valid for 5 minutes.
    Data should usually contain 'email' and 'type'.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=5)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_temp_token(token: str):
    """
    Decode a temporary token and return the payload.
    """
    try:
        decoded_token = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return decoded_token
    except jwt.ExpiredSignatureError:
        return None

def create_admin_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.ADMIN_JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def generate_admin_temp_token(data: dict):
    """
    Generate a temporary admin token valid for 5 minutes.
    Data should usually contain 'email' and 'type'.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=5)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.ADMIN_JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_admin_temp_token(token: str):
    """
    Decode a temporary admin token and return the payload.
    """
    try:
        decoded_token = jwt.decode(token, settings.ADMIN_JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return decoded_token
    except jwt.ExpiredSignatureError:
        return None

def decode_admin_access_token(token: str):
    try:
        decoded_token = jwt.decode(token, settings.ADMIN_JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return decoded_token
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

async def get_current_admin(auth: HTTPAuthorizationCredentials = Depends(security)):
    from .redis_client import check_cache, set_cache
    token = auth.credentials
    payload = decode_admin_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=HEC_401,
            detail=HEM_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )

        res = await db.call_function("fn_verify_admin" , payload.get("id"))
        if not res or res.get('msgcode', '').lower() == "fail":
            error_msg = res.get("msg") if res else "Admin verification failed"
            logger.warning(f"Admin verification failed for {payload.get('id')}: {error_msg}")
            raise HTTPException(
                status_code=HEC_401,
                detail=error_msg,
                headers={"WWW-Authenticate": "Bearer"},
            )
    

    email = payload.get("sub")
    token_version = payload.get("token_version")
    
    if email and token_version is not None:
        cache_key = f"admin:token_version:{email}"
        # 1. Check Redis Cache
        cached_version = await check_cache(cache_key)
        
        if cached_version is not None:
            if str(cached_version) != str(token_version):
                raise HTTPException(
                    status_code=HEC_401,
                    detail="Token has been invalidated. Please login again.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        else:
            # 2. Fallback to DB if not in cache
            db_res = await db.call_function("fn_admin_login", "get_token", email, None, None)
            if db_res:
                db_token_version = db_res.get("token") # Assuming the DB returns 'token' as per user's prompt
                if db_token_version is not None:
                    # Sync cache
                    await set_cache(cache_key, str(db_token_version), ttl=3600*24)
                    
                    if str(db_token_version) != str(token_version):
                        raise HTTPException(
                            status_code=HEC_401,
                            detail="Token has been invalidated. Please login again.",
                            headers={"WWW-Authenticate": "Bearer"},
                        )
    
    return payload

def create_vendor_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.VENDOR_JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_vendor_access_token(token: str):
    try:
        decoded_token = jwt.decode(token, settings.VENDOR_JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return decoded_token
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


async def get_current_vendor_user(auth: HTTPAuthorizationCredentials = Depends(security)):
    token = auth.credentials
    payload = decode_vendor_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=HEC_401,
            detail=HEM_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )

    res = await db.call_function("fn_verify_vendor", payload.get("vendor_id"))
    if not res or res.get("msgcode", "").lower() == "fail":
        error_msg = res.get("msg") if res else "Vendor verification failed"
        logger.warning(f"Vendor verification failed for {payload.get('vendor_id')}: {error_msg}")
        raise HTTPException(
            status_code=HEC_401,
            detail=error_msg,
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


def verify_google_access_token(access_token: str, email: str = None):

    """
    Verify Google OAuth2 Access Token using Google tokeninfo endpoint.
    """
    try:
        response = requests.get(f"https://www.googleapis.com/oauth2/v1/userinfo?access_token={access_token}")
        if response.status_code != 200:
            return {"status": False, "message": "Invalid or expired Google access token."}

        user_info = response.json()
        google_email = user_info.get("email")

        if not google_email:
            return {"status": False, "message": "Email not found in Google user info."}

        if email and google_email.lower() != email.lower():
            return {"status": False, "message": "Email mismatch between Google account and provided email."}

        return {
            "status": True,
            "message": "Google access token verified successfully.",
            "email": google_email,
            "user_info": user_info
        }

    except Exception as e:
        return {"status": False, "message": f"Verification failed: {str(e)}"}

import hashlib

async def templateFilters(user_id, template_name, rest):
    try:
        query = "select * from fn_mail_template($1, $2);"
        print("DEBUG - Query:", query, "| Params: user_id=", user_id, ", template_name=", template_name)
        rows = await db.fetch(
            query,
            user_id,
            template_name
        )

        if not rows:
            raise ValueError("Template not found")

        v_text = rows[0]["v_text"]
        v_subject = rows[0]["v_subject"]

        # Replace {{key}} placeholders
        for key, value in rest.items():
            pattern = r"{{\s*" + re.escape(str(key)) + r"\s*}}"
            v_text = re.sub(pattern, str(value), v_text)

        print("--------------------------")

        return {
            "v_text": v_text,
            "v_subject": v_subject
        }

    except Exception as error:
        logger.error("Template filters error", extra={"error": str(error)})
        raise

os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['CURL_CA_BUNDLE'] = certifi.where()

async def send_mail(user_id, template_name, to, rest):
    try:
        # return True
        smtp_host = os.getenv("ZEPTOMAIL_SMTP_HOST", "smtp.zeptomail.in")
        smtp_port = int(os.getenv("ZEPTOMAIL_SMTP_PORT", 587))
        sender_email = os.getenv("ZEPTOMAIL_SENDER_EMAIL", "info@thetimemachine.com")
        send_mail_token = os.getenv("ZEPTOMAIL_SEND_MAIL_TOKEN", "")

        # Equivalent to templateFilters(...)
        template = await templateFilters(user_id, template_name, rest)
        html = template["v_text"]
        subject = template["v_subject"]

        url = "https://api.zeptomail.com/v1.1/email"
        
        payload = {
            "from": {"address": sender_email},
            "to": [{"email_address": {"address": to}}],
            "subject": subject,
            "htmlbody": html
        }
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Zoho-enczapikey {send_mail_token}"
        }

        print("start email send using ZeptoMail REST API")
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()

        print("Email sent successfully!")

        return True

    except Exception as err:
        print("Failed to send email:", err)
        raise

def format_duration_from_hours(duration_in_hours):
    try:
        h = float(duration_in_hours)
    except (ValueError, TypeError):
        return '0 hour'

    if math.isnan(h) or h < 0:
        return '0 hour'
    if h == 0:
        return '0 hour'

    if h >= 24:
        days = math.floor(h / 24)
        remainder_hours = h % 24

        if remainder_hours == 0:
            return f"{days} day" if days == 1 else f"{days} days"

        mins = round((remainder_hours % 1) * 60)
        hrs = math.floor(remainder_hours)

        day_str = f"{days} day" if days == 1 else f"{days} days"

        if hrs == 0 and mins == 0:
            return day_str
        
        if mins == 0:
            return f"{day_str} {hrs} hour{'' if hrs == 1 else 's'}"

        return f"{day_str} {hrs} hour{'' if hrs == 1 else 's'} : {mins} minutes"

    if h >= 1:
        hours = math.floor(h)
        mins = round((h % 1) * 60)

        if mins == 0:
            return f"{hours} hour" if hours == 1 else f"{hours} hours"

        return f"{hours} hour{'' if hours == 1 else 's'} : {mins} minutes"

    mins = round(h * 60)
    return f"{mins} minute" if mins == 1 else f"{mins} minutes"


async def verify_guest_token(guest_token: str = Header(..., alias="guest-token")):
    """
    Dependency to verify guest token from headers.
    """
    res = await db.call_function("fn_verify_guest", guest_token)
    if not res or res.get('msgcode', '').lower() == "fail":
        raise HTTPException(
            status_code=401,
            detail=res.get("msg") if res else "Guest session expired, please login"
        )
    return res
