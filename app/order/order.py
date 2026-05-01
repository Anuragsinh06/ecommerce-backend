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


# ================= PLACE ORDER =================
async def place_order(form, current_user):
    try:
        user_id = current_user.get("user_id")

        res = await db.call_function(
            "fn_order",
            "place",
            user_id,
            None,
            form.shipping_address,
            form.payment_method
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Order place failed"))

        return successResponse(HSC_200, res.get("msg"), res.get("order_data"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Place order error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


# ================= LIST ORDERS =================
async def list_orders(current_user):
    try:
        user_id = current_user.get("user_id")

        res = await db.call_function(
            "fn_order",
            "list",
            user_id,
            None,
            None,
            None
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Order list failed"))

        return successResponse(HSC_200, res.get("msg"), res.get("orders"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"List order error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


# ================= ORDER DETAIL =================
async def order_detail(order_id, current_user):
    try:
        user_id = current_user.get("user_id")

        res = await db.call_function(
            "fn_order",
            "detail",
            user_id,
            order_id,
            None,
            None
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Order not found"))

        return successResponse(HSC_200, res.get("msg"), res.get("order_data"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Order detail error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


# ================= UPDATE ORDER STATUS (ADMIN) =================
async def update_order_status(form, current_user):
    try:
        res = await db.call_function(
            "fn_update_order_status",
            current_user.get("user_id"),
            form.order_id,
            form.status
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Order status update failed"))

        return successResponse(HSC_200, res.get("msg"), res.get("order_data"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Update order status error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


# ================= CANCEL ORDER =================
async def cancel_order(form, current_user):
    try:
        user_id = current_user.get("user_id")

        res = await db.call_function(
            "fn_order",
            "cancel",
            user_id,
            form.order_id,
            None,
            None
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Order cancel failed"))

        return successResponse(HSC_200, res.get("msg"), res.get("order_data"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Cancel order error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


# ================= RETURN ORDER =================
async def return_order(order_id, current_user):
    try:
        user_id = current_user.get("user_id")

        res = await db.call_function(
            "fn_return_exchange",
            "return",
            user_id,
            order_id
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Return failed"))

        return successResponse(HSC_200, res.get("msg"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Return order error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


# ================= EXCHANGE ORDER =================
async def exchange_order(order_id, current_user):
    try:
        user_id = current_user.get("user_id")

        res = await db.call_function(
            "fn_return_exchange",
            "exchange",
            user_id,
            order_id
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Exchange failed"))

        return successResponse(HSC_200, res.get("msg"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Exchange order error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)