from fastapi import APIRouter, Depends

from common.comman_function import get_current_user
from app.cart.forms.model import CartAddForm, CartUpdateQuantityForm, CartRemoveForm
from app.cart.cart import add_to_cart, view_cart, update_cart_quantity, remove_from_cart, clear_cart

cart_router = APIRouter(prefix="/cart", tags=["Cart"])


@cart_router.post("/add")
async def add_to_cart_api(form: CartAddForm, current_user=Depends(get_current_user)):
    return await add_to_cart(form, current_user)


@cart_router.get("/view")
async def view_cart_api(current_user=Depends(get_current_user)):
    return await view_cart(current_user)


@cart_router.post("/update-quantity")
async def update_cart_quantity_api(
    form: CartUpdateQuantityForm,
    current_user=Depends(get_current_user)
):
    return await update_cart_quantity(form, current_user)


@cart_router.post("/remove")
async def remove_from_cart_api(form: CartRemoveForm, current_user=Depends(get_current_user)):
    return await remove_from_cart(form, current_user)


@cart_router.post("/clear")
async def clear_cart_api(current_user=Depends(get_current_user)):
    return await clear_cart(current_user)