from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

ProviderName = Literal[
    "openai",
    "anthropic",
    "gemini",
    "ollama",
]

MessageRole = Literal[
    "system",
    "user",
    "assistant",
]

Category = Literal[
    "billing",
    "technical",
    "account",
    "general",
]

Priority = Literal[
    "low",
    "medium",
    "high",
    "urgent",
]


class Message(BaseModel):
    role: MessageRole
    content: str = Field(min_length=1, description="The content of the message.")


class ChatRequest(BaseModel):
    messages: list[Message] = Field(
        min_length=1,
        description="A list of messages to send to the model. The last message is considered the user's input.",
    )
    provider: ProviderName | None = None
    model: str | None = None


class ChatResponse(BaseModel):
    content: str = Field(description="The response content from the model.")
    provider: ProviderName = Field(
        description="The provider used to generate the response."
    )
    model: str = Field(description="The model used to generate the response.")


class TicketRequest(BaseModel):
    text: str = Field(min_length=1)
    provider: ProviderName | None = None
    model: str | None = None


class TicketClassification(BaseModel):
    model_config = ConfigDict(extra="forbid")
    category: Category = Field(
        description="The primary category of the support ticket."
    )
    priority: Priority = Field(description="The urgency of the support ticket.")
    summary: str = Field(
        min_length=1, description="A brief summary of the customer's issue."
    )


class TicketClassificationResponse(TicketClassification):
    provider: str
    model: str
