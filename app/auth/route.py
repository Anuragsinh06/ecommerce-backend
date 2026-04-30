from fastapi import APIRouter, Request
from app.auth.forms.model import (
    RegisterForm,
    VerifyRegistrationForm,
    LoginForm,
    VerifyLoginForm,
    ResendOtpForm,
    ForgotPasswordForm,
    VerifyForgotPasswordForm,
    ResetPasswordForm,
)
from app.auth.auth import (
    register_user,
    verify_user_registration,
    login_user,
    verify_user_login,
    resend_otp_logic,
    process_forgot_password,
    verify_user_forgot_password,
    reset_user_password,
    refresh_token_handler,
    logout_handler,
)
from shared.limiter import limiter
from fastapi import Request

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/register")
@limiter.limit("5/minute")
async def register_api(form: RegisterForm, request: Request):
    return await register_user(form, request.client.host)


@auth_router.post("/verify-registration")
async def verify_registration_api(form: VerifyRegistrationForm):
    return await verify_user_registration(form)


@auth_router.post("/login")
@limiter.limit("5/minute")
async def login_api(form: LoginForm,request: Request, ):
    return await login_user(form)


@auth_router.post("/verify-login")
@limiter.limit("10/minute")
async def verify_login_api(form: VerifyLoginForm,request: Request):
    return await verify_user_login(form)


@auth_router.post("/resend-otp")
async def resend_otp_api(form: ResendOtpForm):
    return await resend_otp_logic(form)


@auth_router.post("/forgot-password")
async def forgot_password_api(form: ForgotPasswordForm):
    return await process_forgot_password(form)


@auth_router.post("/verify-forgot-password")
async def verify_forgot_password_api(form: VerifyForgotPasswordForm):
    return await verify_user_forgot_password(form)


@auth_router.post("/reset-password")
async def reset_password_api(form: ResetPasswordForm):
    return await reset_user_password(form)

@auth_router.post("/refresh-token")
async def refresh_token_api(refresh_token: str):
    return await refresh_token_handler(refresh_token)

@auth_router.post("/logout")
async def logout_api(refresh_token: str):
    return await logout_handler(refresh_token)