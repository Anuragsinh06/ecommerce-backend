from fastapi import APIRouter, Depends

from common.comman_function import get_current_user, get_admin_user
from app.product.forms.model import (
    ProductCreateForm,
    ProductUpdateForm,
    ProductDeleteForm
)
from app.product.product import (
    create_product,
    list_products,
    product_detail,
    update_product,
    delete_product
)
from shared.limiter import limiter
from fastapi import Request

product_router = APIRouter(prefix="/product", tags=["Product"])


#  ADMIN ONLY
@product_router.post("/create")
async def create_product_api(
    form: ProductCreateForm,
    current_user=Depends(get_admin_user)
):
    return await create_product(form, current_user)


@product_router.get("/list")
@limiter.limit("30/minute")
async def list_products_api(
    request: Request, 
    page: int = 1,
    size: int = 10,
    category_id: int | None = None,
    search: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    current_user=Depends(get_current_user),
    
):
    return await list_products(
        page,
        size,
        category_id,
        search,
        min_price,
        max_price,
        current_user
    )


# USER ACCESS
@product_router.get("/detail")
async def product_detail_api(
    product_id: int,
    current_user=Depends(get_current_user)
):
    return await product_detail(product_id, current_user)


# ADMIN ONLY
@product_router.post("/update")
async def update_product_api(
    form: ProductUpdateForm,
    current_user=Depends(get_admin_user)
):
    return await update_product(form, current_user)


#  ADMIN ONLY
@product_router.post("/delete")
async def delete_product_api(
    form: ProductDeleteForm,
    current_user=Depends(get_admin_user)
):
    return await delete_product(form, current_user)