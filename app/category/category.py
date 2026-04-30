import traceback
from common.comman_function import logger
from common.common_response import successResponse, errorResponse, HSC_200, HEC_400, HEC_500, HEM_INTERNAL_SERVER_ERROR
from shared.db import db


async def create_category(form, current_user):
    try:
        res = await db.call_function("fn_category", "create", None, form.name, form.description)

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Category creation failed"))

        return successResponse(HSC_200, res.get("msg"), res.get("category_data"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Create category error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)

async def list_categories(page, size, current_user):
    try:
        offset = (page - 1) * size

        res = await db.call_function(
            "fn_category",
            "list",
            offset,   # 🔥 NEW
            size,     # 🔥 NEW
            None
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Category list failed"))

        return successResponse(
            HSC_200,
            res.get("msg"),
            {
                "total": res.get("total"),
                "categories": res.get("categories")
            }
        )

    except Exception as e:
        traceback.print_exc()
        logger.error(f"List category error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)

async def update_category(form, current_user):
    try:
        res = await db.call_function("fn_category", "update", form.category_id, form.name, form.description)

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Category update failed"))

        return successResponse(HSC_200, res.get("msg"), res.get("category_data"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Update category error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


async def delete_category(form, current_user):
    try:
        res = await db.call_function("fn_category", "delete", form.category_id, None, None)

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Category delete failed"))

        return successResponse(HSC_200, res.get("msg"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Delete category error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)