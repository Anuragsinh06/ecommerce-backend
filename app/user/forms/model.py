import re
from pydantic import Field, field_validator
from common.comman_function import SecurityBaseModel


class UpdateProfileForm(SecurityBaseModel):
    username: str = Field(..., min_length=2, max_length=100)

    @field_validator("username")
    @classmethod
    def validate_name(cls, v: str):
        if not re.fullmatch(r"[A-Za-z ]+", v):
            raise ValueError("username must contain only alphabets and spaces")
        return v


class ChangePasswordForm(SecurityBaseModel):
    old_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)

    @field_validator("new_password")
    @classmethod
    def validate_password_complexity(cls, v: str):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v