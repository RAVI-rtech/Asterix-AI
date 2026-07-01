from __future__ import annotations

from typing import Any

from app.services.handlers.base_handler import BaseHandler
from app.schemas.ai_router import RouterRequest


class ChatHandler(BaseHandler):
    """Handles general conversational requests."""

    @property
    def system_prompt(self) -> str:
        return (
            "You are AstraMind AI, a helpful, precise, and professional AI assistant. "
            "Respond clearly, concisely, and in a friendly tone. "
            "If you don't know something, say so honestly."
        )

    async def handle(self, request: RouterRequest, ai_response: str) -> dict[str, Any]:
        return {
            "type": "chat",
            "response_length": len(ai_response),
        }

    @property
    def suggested_actions(self) -> list[str]:
        return ["Continue conversation", "Save to notes", "Share response"]
