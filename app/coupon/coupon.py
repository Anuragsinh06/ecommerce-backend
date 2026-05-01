import traceback

from common.comman_function import logger
from common.common_response import (
    successResponse,
    errorResponse,
    HSC_200,
    HEC_400,
    HEC_500,
    HEM_INTERNAL_SERVER_ERROR,
)
from shared.db import db


async def create_coupon(form, current_user):
    try:
        res = await db.call_function(
            "fn_coupon",
            "create",
            form.code.upper(),
            form.discount_type,
            form.discount_value,
            form.min_order_amount,
            form.max_discount_amount,
            current_user.get("user_id")
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Coupon creation failed"))

        return successResponse(HSC_200, res.get("msg"), res.get("coupon_data"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Create coupon error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


async def list_coupons(current_user):
    try:
        res = await db.call_function(
            "fn_coupon",
            "list",
            None,
            None,
            None,
            None,
            None,
            current_user.get("user_id")
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Coupon list failed"))

        return successResponse(HSC_200, res.get("msg"), res.get("coupons"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"List coupon error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


async def apply_coupon(form, current_user):
    try:
        res = await db.call_function(
            "fn_apply_coupon",
            current_user.get("user_id"),
            form.code.upper()
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Coupon apply failed"))

        return successResponse(HSC_200, res.get("msg"), res.get("discount_data"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Apply coupon error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)