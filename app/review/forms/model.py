from pydantic import Field, field_validator
from common.comman_function import SecurityBaseModel


class ReviewCreateForm(SecurityBaseModel):
    product_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = Field(None, max_length=500)


class ReviewUpdateForm(SecurityBaseModel):
    review_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = Field(None, max_length=500)


class ReviewDeleteForm(SecurityBaseModel):
    review_id: int