from fastapi import APIRouter, Depends

from common.comman_function import get_current_user, get_admin_user
from app.category.forms.model import (
    CategoryCreateForm,
    CategoryUpdateForm,
    CategoryDeleteForm,
)
from app.category.category import (
    create_category,
    list_categories,
    update_category,
    delete_category,
)

category_router = APIRouter(prefix="/category", tags=["Category"])


@category_router.post("/create")
async def create_category_api(
    form: CategoryCreateForm,
    current_user=Depends(get_admin_user)
):
    return await create_category(form, current_user)


@category_router.get("/list")
async def list_category_api(
    page: int = 1,
    size: int = 10,
    current_user=Depends(get_current_user)
):
    return await list_categories(page, size, current_user)


@category_router.post("/update")
async def update_category_api(
    form: CategoryUpdateForm,
    current_user=Depends(get_admin_user)
):
    return await update_category(form, current_user)


@category_router.post("/delete")
async def delete_category_api(
    form: CategoryDeleteForm,
    current_user=Depends(get_admin_user)
):
    return await delete_category(form, current_user)