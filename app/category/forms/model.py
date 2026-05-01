from pydantic import Field, field_validator
from common.comman_function import SecurityBaseModel


class CategoryCreateForm(SecurityBaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: str | None = None


class CategoryUpdateForm(SecurityBaseModel):
    category_id: int
    name: str = Field(..., min_length=2, max_length=100)
    description: str | None = None


class CategoryDeleteForm(SecurityBaseModel):
    category_id: int