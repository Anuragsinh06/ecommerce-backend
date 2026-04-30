import traceback

from common.comman_function import (
    logger,
    hash_password,
    verify_password,
)
from common.common_response import (
    successResponse,
    errorResponse,
    HSC_200,
    HEC_400,
    HEC_500,
    HEM_INTERNAL_SERVER_ERROR,
)
from shared.db import db


async def get_user_profile(current_user: dict):
    try:
        user_id = current_user.get("user_id")

        res = await db.call_function(
            "fn_user_profile",
            "details",
            user_id,
            None,
            None
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "User profile not found"))

        return successResponse(HSC_200, res.get("msg"), res.get("user_data"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Get user profile error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


async def update_user_profile(form, current_user: dict):
    try:
        user_id = current_user.get("user_id")

        res = await db.call_function(
            "fn_user_profile",
            "update_profile",
            user_id,
            form.username,
            None
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Profile update failed"))

        return successResponse(HSC_200, res.get("msg"), res.get("user_data"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Update user profile error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


async def change_user_password(form, current_user: dict):
    try:
        user_id = current_user.get("user_id")

        password_res = await db.call_function(
            "fn_user_profile",
            "get_password",
            user_id,
            None,
            None
        )

        if not password_res or password_res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, password_res.get("msg", "User not found"))

        old_hashed_password = password_res.get("password")

        if not verify_password(form.old_password, old_hashed_password):
            return errorResponse(HEC_400, "Old password is incorrect")

        new_hashed_password = hash_password(form.new_password)

        res = await db.call_function(
            "fn_user_profile",
            "change_password",
            user_id,
            None,
            new_hashed_password
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Password change failed"))

        return successResponse(HSC_200, res.get("msg"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Change password error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)