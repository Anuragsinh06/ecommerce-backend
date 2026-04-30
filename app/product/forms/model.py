from pydantic import Field, field_validator
from common.comman_function import SecurityBaseModel


class ProductCreateForm(SecurityBaseModel):
    category_id: int
    name: str = Field(..., min_length=2, max_length=150)
    description: str | None = None
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    image_url: str | None = None


class ProductUpdateForm(SecurityBaseModel):
    product_id: int
    category_id: int | None = None
    name: str | None = None
    description: str | None = None
    price: float | None = None
    stock: int | None = None
    image_url: str | None = None

    @field_validator("price")
    @classmethod
    def validate_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Price must be greater than 0")
        return v

    @field_validator("stock")
    @classmethod
    def validate_stock(cls, v):
        if v is not None and v < 0:
            raise ValueError("Stock cannot be negative")
        return v


class ProductDeleteForm(SecurityBaseModel):
    product_id: int