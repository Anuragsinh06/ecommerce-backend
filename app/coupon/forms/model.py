from pydantic import Field, field_validator
from common.comman_function import SecurityBaseModel


class CouponCreateForm(SecurityBaseModel):
    code: str = Field(..., min_length=3, max_length=30)
    discount_type: str = Field(..., description="percentage or fixed")
    discount_value: float = Field(..., gt=0)
    min_order_amount: float = Field(default=0, ge=0)
    max_discount_amount: float | None = None

    @field_validator("discount_type")
    @classmethod
    def validate_discount_type(cls, v):
        if v.lower() not in ["percentage", "fixed"]:
            raise ValueError("discount_type must be percentage or fixed")
        return v.lower()


class ApplyCouponForm(SecurityBaseModel):
    code: str