from fastapi import APIRouter

user_router = APIRouter()

# @user_router.get("/ping")
# def ping():
#     return {"message": "user pong"}



from fastapi import APIRouter, Depends

from common.comman_function import get_current_user
from app.user.forms.model import UpdateProfileForm, ChangePasswordForm
from app.user.user import (
    get_user_profile,
    update_user_profile,
    change_user_password,
)

user_router = APIRouter(prefix="/user", tags=["User"])


@user_router.get("/profile")
async def profile_api(current_user=Depends(get_current_user)):
    return await get_user_profile(current_user)


@user_router.post("/profile/update")
async def update_profile_api(
    form: UpdateProfileForm,
    current_user=Depends(get_current_user)
):
    return await update_user_profile(form, current_user)


@user_router.post("/password/change")
async def change_password_api(
    form: ChangePasswordForm,
    current_user=Depends(get_current_user)
):
    return await change_user_password(form, current_user)
