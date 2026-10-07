from fastapi import APIRouter

from app.routes.chat import router as chat_router
from app.routes.health import router as health_router

router = APIRouter()
router.include_router(health_router)
router.include_router(chat_router)
