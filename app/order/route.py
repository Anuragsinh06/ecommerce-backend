from fastapi import APIRouter, Depends

from common.comman_function import get_current_user,get_admin_user
from app.order.forms.model import PlaceOrderForm, OrderDetailForm, CancelOrderForm,UpdateOrderStatusForm
from app.order.order import place_order, list_orders, order_detail, cancel_order,return_order,exchange_order,update_order_status

order_router = APIRouter(prefix="/order", tags=["Order"])


@order_router.post("/place")
async def place_order_api(
    form: PlaceOrderForm,
    current_user=Depends(get_current_user)
):
    return await place_order(form, current_user)


@order_router.get("/list")
async def list_orders_api(current_user=Depends(get_current_user)):
    return await list_orders(current_user)


@order_router.get("/detail")
async def order_detail_api(
    order_id: int,
    current_user=Depends(get_current_user)
):
    return await order_detail(order_id, current_user)


@order_router.post("/update-status")
async def update_order_status_api(
    form: UpdateOrderStatusForm,
    current_user=Depends(get_admin_user)
):
    return await update_order_status(form, current_user)


@order_router.post("/cancel")
async def cancel_order_api(
    form: CancelOrderForm,
    current_user=Depends(get_current_user)
):
    return await cancel_order(form, current_user)

@order_router.post("/return")
async def return_order_api(order_id: int, current_user=Depends(get_current_user)):
    return await return_order(order_id, current_user)


@order_router.post("/exchange")
async def exchange_order_api(order_id: int, current_user=Depends(get_current_user)):
    return await exchange_order(order_id, current_user)