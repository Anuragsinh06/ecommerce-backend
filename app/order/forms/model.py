from pydantic import Field
from common.comman_function import SecurityBaseModel


class PlaceOrderForm(SecurityBaseModel):
    shipping_address: str = Field(..., min_length=10)
    payment_method: str = Field(default="COD")


class OrderDetailForm(SecurityBaseModel):
    order_id: int


class UpdateOrderStatusForm(SecurityBaseModel):
    order_id: int
    status: str


class CancelOrderForm(SecurityBaseModel):
    order_id: int

