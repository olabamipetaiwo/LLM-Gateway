from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.config.dependencies import get_llm_service
from app.config.schemas import ChatRequest, ChatResponse
from app.services.llm_service import LLMService
from app.config.schemas import (
    TicketRequest,
    TicketClassificationResponse,
    TicketClassification,
    Message,
)

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    llm_service: Annotated[LLMService, Depends(get_llm_service)],
) -> ChatResponse:
    content, provider, model = await llm_service.chat(
        messages=request.messages,
        provider_name=request.provider,
        model=request.model,
    )

    return ChatResponse(content=content, provider=provider, model=model)


@router.post(
    "/classify-ticket",
    response_model=TicketClassificationResponse,
)
async def classify_ticket(
    request: TicketRequest,
    llm_service: Annotated[LLMService, Depends(get_llm_service)],
) -> TicketClassificationResponse:

    messages = [
        Message(
            role="system",
            content=("Classify customer support " "requests accurately."),
        ),
        Message(
            role="user",
            content=request.text,
        ),
    ]

    result, provider, model = await llm_service.structured(
        messages=messages,
        output_schema=TicketClassification,
        provider_name=request.provider,
        model=request.model,
    )

    return TicketClassificationResponse(
        **result.model_dump(),
        provider=provider,
        model=model,
    )
