from fastapi import APIRouter, Depends

from common.comman_function import get_current_user, get_admin_user
from app.payment.forms.model import PaymentCreateForm, PaymentUpdateForm
from app.payment.payment import create_payment, update_payment_status, get_payment_detail

payment_router = APIRouter(prefix="/payment", tags=["Payment"])


@payment_router.post("/create")
async def create_payment_api(
    form: PaymentCreateForm,
    current_user=Depends(get_current_user)
):
    return await create_payment(form, current_user)


@payment_router.post("/update-status")
async def update_payment_status_api(
    form: PaymentUpdateForm,
    current_user=Depends(get_admin_user)
):
    return await update_payment_status(form, current_user)


@payment_router.get("/detail")
async def get_payment_detail_api(
    order_id: int,
    current_user=Depends(get_current_user)
):
    return await get_payment_detail(order_id, current_user)