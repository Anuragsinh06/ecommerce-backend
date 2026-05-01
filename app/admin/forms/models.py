from pydantic import Field, field_validator
from common.comman_function import SecurityBaseModel


class UserStatusForm(SecurityBaseModel):
    user_id: int
    is_active: bool


class MakeAdminForm(SecurityBaseModel):
    user_id: int


class StockUpdateForm(SecurityBaseModel):
    product_id: int
    stock: int = Field(..., ge=0)


class CouponUpdateForm(SecurityBaseModel):
    coupon_id: int
    discount_type: str | None = None
    discount_value: float | None = None
    min_order_amount: float | None = None
    max_discount_amount: float | None = None

    @field_validator("discount_type")
    @classmethod
    def validate_discount_type(cls, v):
        if v is not None and v.lower() not in ["percentage", "fixed"]:
            raise ValueError("discount_type must be percentage or fixed")
        return v.lower() if v else v


class CouponStatusForm(SecurityBaseModel):
    coupon_id: int
    is_active: bool


class ReturnExchangeActionForm(SecurityBaseModel):
    order_id: int
    action_type: str  # return or exchange
    decision: str     # approve or reject

    @field_validator("action_type")
    @classmethod
    def validate_action_type(cls, v):
        if v.lower() not in ["return", "exchange"]:
            raise ValueError("action_type must be return or exchange")
        return v.lower()

    @field_validator("decision")
    @classmethod
    def validate_decision(cls, v):
        if v.lower() not in ["approve", "reject"]:
            raise ValueError("decision must be approve or reject")
        return v.lower()