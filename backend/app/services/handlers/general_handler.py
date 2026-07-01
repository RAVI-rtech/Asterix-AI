from __future__ import annotations

from typing import Any

from app.services.handlers.base_handler import BaseHandler
from app.schemas.ai_router import RouterRequest


class GeneralHandler(BaseHandler):
    """Fallback handler for requests that don't fit a specific category."""

    @property
    def system_prompt(self) -> str:
        return (
            "You are AstraMind AI, a versatile and helpful AI assistant. "
            "Answer the user's request thoughtfully and concisely. "
            "If the request could benefit from a specific feature (like code execution, "
            "document analysis, or image generation), mention that capability."
        )

    async def handle(self, request: RouterRequest, ai_response: str) -> dict[str, Any]:
        return {
            "type": "general",
            "response_length": len(ai_response),
        }

    @property
    def suggested_actions(self) -> list[str]:
        return ["Ask a follow-up", "Try a specific feature", "Save response"]
