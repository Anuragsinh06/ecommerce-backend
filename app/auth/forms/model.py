import re
from pydantic import EmailStr, Field, field_validator
from common.comman_function import SecurityBaseModel


class RegisterForm(SecurityBaseModel):
    username: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=8)
    phone_number: str = Field(..., max_length=10)
    

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v


class VerifyRegistrationForm(SecurityBaseModel):
    token: str
    otp: str


class LoginForm(SecurityBaseModel):
     username: str = Field(..., min_length=2)
     phone_number: str = Field(..., max_length=10)
    #  email: EmailStr
     password: str


class VerifyLoginForm(SecurityBaseModel):
    token: str
    otp: str


class ResendOtpForm(SecurityBaseModel):
    token: str


class ForgotPasswordForm(SecurityBaseModel):
    username: str = Field(..., min_length=2)
    phone_number: str = Field(..., max_length=10)


class VerifyForgotPasswordForm(SecurityBaseModel):
    token: str
    otp: str


class ResetPasswordForm(SecurityBaseModel):
    token: str
    otp: str
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v