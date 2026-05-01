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


async def create_payment(form, current_user):
    try:
        user_id = current_user.get("user_id")

        res = await db.call_function(
            "fn_payment",
            "create",
            user_id,
            form.order_id,
            form.amount,
            "pending",
            form.payment_method,
            None
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Payment creation failed"))

        return successResponse(HSC_200, res.get("msg"), res.get("payment_data"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Create payment error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


async def update_payment_status(form, current_user):
    try:
        res = await db.call_function(
            "fn_payment",
            "update",
            None,
            form.order_id,
            None,
            form.status,
            None,
            form.transaction_id
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Payment update failed"))

        return successResponse(HSC_200, res.get("msg"), res.get("payment_data"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Update payment error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


async def get_payment_detail(order_id, current_user):
    try:
        user_id = current_user.get("user_id")
        role = current_user.get("role")

        res = await db.call_function(
            "fn_payment",
            "detail",
            user_id,
            order_id,
            None,
            None,
            None,
            None
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Payment not found"))

        return successResponse(HSC_200, res.get("msg"), res.get("payment_data"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Payment detail error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)