from pydantic import Field, field_validator
from common.comman_function import SecurityBaseModel


class PaymentCreateForm(SecurityBaseModel):
    order_id: int
    amount: float = Field(..., gt=0)
    payment_method: str = Field(default="online")


class PaymentUpdateForm(SecurityBaseModel):
    order_id: int
    status: str
    transaction_id: str | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str):
        allowed = ["pending", "paid", "failed", "refunded"]
        if v.lower() not in allowed:
            raise ValueError("Status must be pending, paid, failed, or refunded")
        return v.lower()