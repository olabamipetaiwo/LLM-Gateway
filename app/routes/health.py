from fastapi import APIRouter, Depends
from typing import Annotated

from app.config.dependencies import get_llm_service
from app.services.llm_service import LLMService

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "LLM Service is up and running!"}


@router.get("/providers")
async def providers(llm_service: Annotated[LLMService, Depends(get_llm_service)]):
    return {"providers": llm_service.registry.names()}


# http://127.0.0.1:8000/docs
