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


async def add_to_cart(form, current_user):
    try:
        user_id = current_user.get("user_id")

        res = await db.call_function(
            "fn_cart",
            "add",
            user_id,
            form.product_id,
            form.quantity
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Add to cart failed"))

        return successResponse(HSC_200, res.get("msg"), res.get("cart_data"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Add to cart error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


async def view_cart(current_user):
    try:
        user_id = current_user.get("user_id")

        res = await db.call_function(
            "fn_cart",
            "view",
            user_id,
            None,
            None
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Cart fetch failed"))

        return successResponse(HSC_200, res.get("msg"), res.get("cart_data"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"View cart error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


async def update_cart_quantity(form, current_user):
    try:
        user_id = current_user.get("user_id")

        res = await db.call_function(
            "fn_cart",
            "update_quantity",
            user_id,
            form.product_id,
            form.quantity
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Cart quantity update failed"))

        return successResponse(HSC_200, res.get("msg"), res.get("cart_data"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Update cart quantity error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


async def remove_from_cart(form, current_user):
    try:
        user_id = current_user.get("user_id")

        res = await db.call_function(
            "fn_cart",
            "remove",
            user_id,
            form.product_id,
            None
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Remove from cart failed"))

        return successResponse(HSC_200, res.get("msg"), res.get("cart_data"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Remove from cart error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


async def clear_cart(current_user):
    try:
        user_id = current_user.get("user_id")

        res = await db.call_function(
            "fn_cart",
            "clear",
            user_id,
            None,
            None
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Clear cart failed"))

        return successResponse(HSC_200, res.get("msg"), res.get("cart_data"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Clear cart error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)