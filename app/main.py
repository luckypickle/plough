# -*- coding: utf-8 -*-

from fastapi import Depends, FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.core.config import get_app_settings
from app.api.api_v1.api import api_router


# from .dependencies import get_query_token, get_token_header
# from .internal import admin
# from .routers import items, users

def get_application() -> FastAPI:
    settings = get_app_settings()
    settings.configure_logging()
    application = FastAPI(
        # title=settings.title, #openapi_url=f"{settings.api_prefix}/openapi.json",
        **settings.fastapi_kwargs
    )
    if settings.BACKEND_CORS_ORIGINS:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    application.include_router(api_router, prefix=settings.api_prefix)
    return application


app = get_application()


@app.get("/")
async def root():
    return {"message": "Hello Plough!"}
