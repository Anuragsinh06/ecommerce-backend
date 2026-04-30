from fastapi import APIRouter, Depends

from common.comman_function import get_admin_user
from app.admin.admin import (
    get_dashboard_analytics,
    admin_list_users,
    admin_update_user_status,
    admin_make_user_admin,
    admin_update_product_stock,
    admin_update_coupon,
    admin_update_coupon_status,
    admin_list_orders,
    admin_return_exchange_action,
)
from app.admin.forms.models import (
    UserStatusForm,
    MakeAdminForm,
    StockUpdateForm,
    CouponUpdateForm,
    CouponStatusForm,
    ReturnExchangeActionForm,
)

admin_router = APIRouter(prefix="/admin", tags=["Admin"])


@admin_router.get("/dashboard")
async def dashboard_analytics_api(current_user=Depends(get_admin_user)):
    return await get_dashboard_analytics(current_user)


@admin_router.get("/users")
async def admin_list_users_api(
    page: int = 1,
    size: int = 10,
    current_user=Depends(get_admin_user)
):
    return await admin_list_users(page, size, current_user)


@admin_router.post("/user/status")
async def admin_update_user_status_api(
    form: UserStatusForm,
    current_user=Depends(get_admin_user)
):
    return await admin_update_user_status(form, current_user)


@admin_router.post("/user/make-admin")
async def admin_make_user_admin_api(
    form: MakeAdminForm,
    current_user=Depends(get_admin_user)
):
    return await admin_make_user_admin(form, current_user)


@admin_router.post("/product/stock")
async def admin_update_product_stock_api(
    form: StockUpdateForm,
    current_user=Depends(get_admin_user)
):
    return await admin_update_product_stock(form, current_user)


@admin_router.post("/coupon/update")
async def admin_update_coupon_api(
    form: CouponUpdateForm,
    current_user=Depends(get_admin_user)
):
    return await admin_update_coupon(form, current_user)


@admin_router.post("/coupon/status")
async def admin_update_coupon_status_api(
    form: CouponStatusForm,
    current_user=Depends(get_admin_user)
):
    return await admin_update_coupon_status(form, current_user)


@admin_router.get("/orders")
async def admin_list_orders_api(
    page: int = 1,
    size: int = 10,
    status: str | None = None,
    current_user=Depends(get_admin_user)
):
    return await admin_list_orders(page, size, status, current_user)


@admin_router.post("/return-exchange/action")
async def admin_return_exchange_action_api(
    form: ReturnExchangeActionForm,
    current_user=Depends(get_admin_user)
):
    return await admin_return_exchange_action(form, current_user)