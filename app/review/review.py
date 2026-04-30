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


async def create_review(form, current_user):
    try:
        user_id = current_user.get("user_id")

        res = await db.call_function(
            "fn_review",
            "create",
            None,
            user_id,
            form.product_id,
            form.rating,
            form.comment
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Review creation failed"))

        return successResponse(HSC_200, res.get("msg"), res.get("review_data"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Create review error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


async def product_reviews(product_id, current_user):
    try:
        user_id = current_user.get("user_id")

        res = await db.call_function(
            "fn_review",
            "list",
            None,
            user_id,
            product_id,
            None,
            None
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Reviews fetch failed"))

        return successResponse(HSC_200, res.get("msg"), res.get("review_data"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Product reviews error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


async def update_review(form, current_user):
    try:
        user_id = current_user.get("user_id")

        res = await db.call_function(
            "fn_review",
            "update",
            form.review_id,
            user_id,
            None,
            form.rating,
            form.comment
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Review update failed"))

        return successResponse(HSC_200, res.get("msg"), res.get("review_data"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Update review error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


async def delete_review(form, current_user):
    try:
        user_id = current_user.get("user_id")

        res = await db.call_function(
            "fn_review",
            "delete",
            form.review_id,
            user_id,
            None,
            None,
            None
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Review delete failed"))

        return successResponse(HSC_200, res.get("msg"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Delete review error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)