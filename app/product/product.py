import traceback
import redis

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
from shared.cache import get_cache, set_cache


# ================= CACHE CLEAR =================
def clear_product_cache():
    redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

    for key in redis_client.scan_iter("products:*"):
        redis_client.delete(key)


# ================= CREATE PRODUCT =================
async def create_product(form, current_user):
    try:
        res = await db.call_function(
            "fn_product",
            "create",
            None,
            form.category_id,
            form.name,
            form.description,
            form.price,
            form.stock,
            form.image_url,
            None,
            None,
            None
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Product creation failed"))

        clear_product_cache()  # IMPORTANT

        return successResponse(HSC_200, res.get("msg"), res.get("product_data"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Create product error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


# ================= LIST PRODUCTS (CACHE ENABLED) =================
async def list_products(page, size, category_id, search, min_price, max_price, current_user):
    try:
        cache_key = f"products:{page}:{size}:{category_id}:{search}:{min_price}:{max_price}"

        # Check cache
        cached_data = get_cache(cache_key)
        if cached_data:
            return successResponse(HSC_200, "Products fetched (cache)", cached_data)

        offset = (page - 1) * size

        res = await db.call_function(
            "fn_product_list",
            offset,
            size,
            category_id,
            search,
            min_price,
            max_price
        )

        if not res:
            return errorResponse(HEC_400, "Failed to fetch products")

        # Store cache
        set_cache(cache_key, res, expire=120)

        return successResponse(HSC_200, "Products fetched", res)

    except Exception as e:
        traceback.print_exc()
        logger.error(f"List product error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


# ================= PRODUCT DETAIL =================
async def product_detail(product_id, current_user):
    try:
        res = await db.call_function(
            "fn_product",
            "detail",
            product_id,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Product not found"))

        return successResponse(HSC_200, res.get("msg"), res.get("product_data"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Product detail error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


# ================= UPDATE PRODUCT =================
async def update_product(form, current_user):
    try:
        res = await db.call_function(
            "fn_product",
            "update",
            form.product_id,
            form.category_id,
            form.name,
            form.description,
            form.price,
            form.stock,
            form.image_url,
            None,
            None,
            None
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Product update failed"))

        clear_product_cache()  # 🔥 IMPORTANT

        return successResponse(HSC_200, res.get("msg"), res.get("product_data"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Update product error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)


# ================= DELETE PRODUCT =================
async def delete_product(form, current_user):
    try:
        res = await db.call_function(
            "fn_product",
            "delete",
            form.product_id,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None
        )

        if not res or res.get("msgcode", "").lower() == "fail":
            return errorResponse(HEC_400, res.get("msg", "Product delete failed"))

        clear_product_cache()  # IMPORTANT

        return successResponse(HSC_200, res.get("msg"))

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Delete product error: {str(e)}", exc_info=True)
        return errorResponse(HEC_500, HEM_INTERNAL_SERVER_ERROR)