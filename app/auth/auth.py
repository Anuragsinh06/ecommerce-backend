import jwt
import traceback
from datetime import datetime, timedelta

from config.config import settings
from common.token import create_access_token, create_refresh_token
from common.comman_function import (
    hash_password,
    verify_password,
    generate_temp_token,
    decode_temp_token,
    logger,
)
from common.common_response import (
    successResponse,
    errorResponse,
    HSC_200,
    HEC_400,
    HEC_500,
    HEM_INTERNAL_SERVER_ERROR,
)
from shared.db import db


async def register_user(form, client_ip: str):
    try:
        logger.info(f"IP: {client_ip} - Register request for {form.email}")

        hashed_pwd = hash_password(form.password)

        res = await db.call_function(
            "fn_register_user",
            "register",
            form.username,
            form.email,
            hashed_pwd,
            None,
            form.phone_number,
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Registration failed"))

        temp_token = generate_temp_token({
            "email": form.email,
            "type": "register"
        })

        return successResponse(
            HSC_200,
            res.get("msg"),
            {
                "token": temp_token,
                "otp": res.get("otp")
            }
        )

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


async def verify_user_registration(form):
    try:
        payload = decode_temp_token(form.token)

        if not payload or payload.get("type") != "register":
            return errorResponse(HEC_400, "Invalid or expired token")

        email = payload.get("email")

        res = await db.call_function(
            "fn_register_user",
            "verify",
            None,
            email,
            None,
            form.otp,
            None,
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Verification failed"))

        user_data = res.get("user_data")

        access_token = create_access_token({
            "sub": email,
            "user_id": user_data.get("id"),
            "username": user_data.get("username"),
            "role": user_data.get("role", "user")
        })

        refresh_token = create_refresh_token({
            "user_id": user_data.get("id")
        })

        await db.execute(
            """
            INSERT INTO refresh_tokens (user_id, token, expires_at)
            VALUES ($1, $2, $3)
            """,
            user_data.get("id"),
            refresh_token,
            datetime.utcnow() + timedelta(days=7)
        )

        return successResponse(
            HSC_200,
            res.get("msg"),
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "user": user_data
            }
        )

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Verify registration error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


async def login_user(form):
    try:
        user_input = form.username if form.username else form.phone_number

        password_res = await db.call_function(
            "fn_login_user",
            "password_verify",
            user_input,
            None,
            None
        )

        if not password_res or not password_res.get("password"):
            return errorResponse(HEC_400, "Invalid username/phone or password")

        if not verify_password(form.password, password_res.get("password")):
            return errorResponse(HEC_400, "Invalid username/phone or password")

        res = await db.call_function(
            "fn_login_user",
            "login",
            user_input,
            None,
            None
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Login failed"))

        temp_token = generate_temp_token({
            "identifier": user_input,
            "type": "login"
        })

        return successResponse(
            HSC_200,
            res.get("msg"),
            {
                "token": temp_token,
                "otp": res.get("otp")
            }
        )

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Login error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


async def verify_user_login(form):
    try:
        payload = decode_temp_token(form.token)

        if not payload or payload.get("type") != "login":
            return errorResponse(HEC_400, "Invalid or expired token")

        identifier = payload.get("identifier")

        res = await db.call_function(
            "fn_login_user",
            "verify",
            identifier,
            form.otp,
            None
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Login verification failed"))

        user_data = res.get("user_data")

        access_token = create_access_token({
            "sub": identifier,
            "user_id": user_data.get("id"),
            "username": user_data.get("username"),
            "role": user_data.get("role", "user")
        })

        refresh_token = create_refresh_token({
            "user_id": user_data.get("id")
        })

        await db.execute(
            """
            INSERT INTO refresh_tokens (user_id, token, expires_at)
            VALUES ($1, $2, $3)
            """,
            user_data.get("id"),
            refresh_token,
            datetime.utcnow() + timedelta(days=7)
        )

        return successResponse(
            HSC_200,
            res.get("msg"),
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "user": user_data
            }
        )

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Verify login error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


async def resend_otp_logic(form):
    try:
        payload = decode_temp_token(form.token)

        if not payload:
            return errorResponse(HEC_400, "Invalid or expired token")

        user = payload.get("identifier") or payload.get("email")
        otp_type = payload.get("type")

        check_user = await db.call_function(
            "fn_login_user",
            "password_verify",
            user,
            None,
            None
        )

        if not check_user or not check_user.get("password"):
            return errorResponse(HEC_400, "User not found. Cannot resend OTP.")

        res = await db.call_function(
            "fn_resend_otp",
            user,
            otp_type
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Resend OTP failed"))

        return successResponse(
            HSC_200,
            res.get("msg"),
            {
                "otp": res.get("otp")
            }
        )

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Resend OTP error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


async def process_forgot_password(form):
    try:
        user_input = form.username if form.username else form.phone_number

        res = await db.call_function(
            "fn_forgot_password",
            "forgot",
            user_input,
            None,
            None,
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Forgot password failed"))

        temp_token = generate_temp_token({
            "identifier": user_input,
            "type": "forgot"
        })

        return successResponse(
            HSC_200,
            res.get("msg"),
            {
                "token": temp_token,
                "otp": res.get("otp")
            }
        )

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Forgot password error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


async def verify_user_forgot_password(form):
    try:
        payload = decode_temp_token(form.token)

        if not payload or payload.get("type") != "forgot":
            return errorResponse(HEC_400, "Invalid or expired token")

        identifier = payload.get("identifier")

        res = await db.call_function(
            "fn_forgot_password",
            "verify",
            identifier,
            form.otp,
            None,
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Forgot password verification failed"))

        return successResponse(HSC_200, res.get("msg"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Verify forgot password error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


async def reset_user_password(form):
    try:
        payload = decode_temp_token(form.token)

        if not payload or payload.get("type") != "forgot":
            return errorResponse(HEC_400, "Invalid or expired token")

        identifier = payload.get("identifier")
        hashed_pwd = hash_password(form.password)

        res = await db.call_function(
            "fn_forgot_password",
            "update",
            identifier,
            form.otp,
            hashed_pwd,
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Reset password failed"))

        return successResponse(HSC_200, res.get("msg"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Reset password error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


async def refresh_token_handler(refresh_token: str):
    try:
        payload = jwt.decode(
            refresh_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        if payload.get("type") != "refresh":
            return errorResponse(HEC_400, "Invalid token type")

        user_id = payload.get("user_id")

        token_row = await db.fetchrow(
            """
            SELECT * FROM refresh_tokens
            WHERE token = $1 AND is_revoked = FALSE
            """,
            refresh_token
        )

        if not token_row:
            return errorResponse(HEC_400, "Invalid or revoked token")

        if token_row["expires_at"] < datetime.utcnow():
            return errorResponse(HEC_400, "Token expired")

        user_row = await db.fetchrow(
            "SELECT id, username, role FROM users WHERE id = $1",
            user_id
        )

        if not user_row:
            return errorResponse(HEC_400, "User not found")

        access_token = create_access_token({
            "user_id": user_row["id"],
            "username": user_row["username"],
            "role": user_row["role"]
        })

        return successResponse(
            HSC_200,
            "New access token generated",
            {
                "access_token": access_token,
                "token_type": "bearer"
            }
        )

    except jwt.ExpiredSignatureError:
        return errorResponse(HEC_400, "Refresh token expired")

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Refresh token error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


async def logout_handler(refresh_token: str):
    try:
        await db.execute(
            """
            UPDATE refresh_tokens
            SET is_revoked = TRUE
            WHERE token = $1
            """,
            refresh_token
        )

        return successResponse(
            HSC_200,
            "Logged out successfully"
        )

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Logout error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)