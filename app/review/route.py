from fastapi import APIRouter, Depends

from common.comman_function import get_current_user
from app.review.forms.model import ReviewCreateForm, ReviewUpdateForm, ReviewDeleteForm
from app.review.review import create_review, product_reviews, update_review, delete_review

review_router = APIRouter(prefix="/review", tags=["Review"])


@review_router.post("/create")
async def create_review_api(
    form: ReviewCreateForm,
    current_user=Depends(get_current_user)
):
    return await create_review(form, current_user)


@review_router.get("/product")
async def product_reviews_api(
    product_id: int,
    current_user=Depends(get_current_user)
):
    return await product_reviews(product_id, current_user)


@review_router.post("/update")
async def update_review_api(
    form: ReviewUpdateForm,
    current_user=Depends(get_current_user)
):
    return await update_review(form, current_user)


@review_router.post("/delete")
async def delete_review_api(
    form: ReviewDeleteForm,
    current_user=Depends(get_current_user)
):
    return await delete_review(form, current_user)