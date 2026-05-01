from fastapi import APIRouter, Depends

from common.comman_function import get_current_user, get_admin_user
from app.coupon.forms.model import CouponCreateForm, ApplyCouponForm
from app.coupon.coupon import create_coupon, list_coupons, apply_coupon

coupon_router = APIRouter(prefix="/coupon", tags=["Coupon"])


#  ADMIN ONLY
@coupon_router.post("/create")
async def create_coupon_api(
    form: CouponCreateForm,
    current_user=Depends(get_admin_user)
):
    return await create_coupon(form, current_user)


#  USER ACCESS (view coupons)
@coupon_router.get("/list")
async def list_coupons_api(
    current_user=Depends(get_current_user)
):
    return await list_coupons(current_user)


#  USER ACCESS (apply coupon)
@coupon_router.post("/apply")
async def apply_coupon_api(
    form: ApplyCouponForm,
    current_user=Depends(get_current_user)
):
    return await apply_coupon(form, current_user)