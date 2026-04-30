"""
Main module of Ecommerce backend.
"""

import os
import pathlib
import uvicorn
import logging
import json
import logging.config
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from shared.db import db
from shared.limiter import limiter

from app.auth.route import auth_router
from app.user.route import user_router
from app.category.route import category_router
from app.product.route import product_router
from app.cart.route import cart_router
from app.order.route import order_router
from app.coupon.route import coupon_router
from app.review.route import review_router
from app.payment.route import payment_router
from app.admin.route import admin_router


module_path = pathlib.Path(__file__).parent.absolute()
config_path = os.path.join(module_path, "config", "logging_config.json")


def setup_logger():
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=logging.INFO)

    return logging.getLogger("Ecommerce")


logger = setup_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting app: connecting to database...")
    await db.connect()

    yield

    logger.info("Shutting down app: disconnecting from database...")
    await db.disconnect()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Ecommerce_API",
        debug=False,
        lifespan=lifespan
    )

    app.logger = logger

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        logger.info(f"Request: {request.method} {request.url.path}")
        response = await call_next(request)
        logger.info(f"Response: {request.method} {request.url.path} - {response.status_code}")
        return response

    @app.get("/")
    async def root():
        return {"message": "Ecommerce API is running"}

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    app.include_router(auth_router)
    app.include_router(admin_router)
    app.include_router(user_router)
    app.include_router(category_router)
    app.include_router(product_router)
    app.include_router(cart_router)
    app.include_router(order_router)
    app.include_router(coupon_router)
    app.include_router(payment_router)
    app.include_router(review_router)
    

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8060,
        ws_ping_interval=1,
        ws_ping_timeout=-1
    )