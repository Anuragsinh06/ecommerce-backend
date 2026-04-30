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


async def get_dashboard_analytics(current_user):
    try:
        res = await db.call_function("fn_admin_dashboard")

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Dashboard analytics failed"))

        return successResponse(HSC_200, res.get("msg"), res.get("dashboard_data"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Admin dashboard error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


async def admin_list_users(page, size, current_user):
    try:
        offset = (page - 1) * size

        res = await db.call_function(
            "fn_admin_user",
            "list",
            None,
            None,
            offset,
            size
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "User list failed"))

        return successResponse(HSC_200, res.get("msg"), {
            "total": res.get("total"),
            "users": res.get("users")
        })

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Admin list users error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


async def admin_update_user_status(form, current_user):
    try:
        res = await db.call_function(
            "fn_admin_user",
            "status",
            form.user_id,
            form.is_active,
            None,
            None
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "User status update failed"))

        return successResponse(HSC_200, res.get("msg"), res.get("user_data"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Admin user status error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


async def admin_make_user_admin(form, current_user):
    try:
        res = await db.call_function(
            "fn_admin_user",
            "make_admin",
            form.user_id,
            None,
            None,
            None
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Make admin failed"))

        return successResponse(HSC_200, res.get("msg"), res.get("user_data"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Admin make user admin error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


async def admin_update_product_stock(form, current_user):
    try:
        res = await db.call_function(
            "fn_admin_product_stock",
            form.product_id,
            form.stock
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Stock update failed"))

        return successResponse(HSC_200, res.get("msg"), res.get("product_data"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Admin product stock error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


async def admin_update_coupon(form, current_user):
    try:
        res = await db.call_function(
            "fn_admin_coupon",
            "update",
            form.coupon_id,
            None,
            form.discount_type,
            form.discount_value,
            form.min_order_amount,
            form.max_discount_amount
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Coupon update failed"))

        return successResponse(HSC_200, res.get("msg"), res.get("coupon_data"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Admin coupon update error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


async def admin_update_coupon_status(form, current_user):
    try:
        res = await db.call_function(
            "fn_admin_coupon",
            "status",
            form.coupon_id,
            form.is_active,
            None,
            None,
            None,
            None
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Coupon status update failed"))

        return successResponse(HSC_200, res.get("msg"), res.get("coupon_data"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Admin coupon status error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


async def admin_list_orders(page, size, status, current_user):
    try:
        offset = (page - 1) * size

        res = await db.call_function(
            "fn_admin_orders",
            offset,
            size,
            status
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Admin order list failed"))

        return successResponse(HSC_200, res.get("msg"), {
            "total": res.get("total"),
            "orders": res.get("orders")
        })

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Admin orders error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


async def admin_return_exchange_action(form, current_user):
    try:
        res = await db.call_function(
            "fn_admin_return_exchange",
            form.order_id,
            form.action_type,
            form.decision
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Action failed"))

        return successResponse(HSC_200, res.get("msg"), res.get("order_data"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Admin return/exchange error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)