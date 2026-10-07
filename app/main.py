from fastapi import FastAPI

from app.routes import router
from app.exceptions.error_handler import (
    register_error_handlers,
)

def create_app() -> FastAPI:
    application = FastAPI(title="LLM Gateway", version="0.1.0")
    application.include_router(router)
    return application


app = create_app()
register_error_handlers(app)


