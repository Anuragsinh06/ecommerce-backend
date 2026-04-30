from pydantic import Field, field_validator
from common.comman_function import SecurityBaseModel


class CartAddForm(SecurityBaseModel):
    product_id: int
    quantity: int = Field(..., ge=1)


class CartUpdateQuantityForm(SecurityBaseModel):
    product_id: int
    quantity: int = Field(..., ge=1)


class CartRemoveForm(SecurityBaseModel):
    product_id: int