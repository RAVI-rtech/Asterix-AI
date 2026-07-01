from __future__ import annotations

from typing import Any

from app.services.handlers.base_handler import BaseHandler
from app.schemas.ai_router import RouterRequest


class PDFHandler(BaseHandler):
    """Handles PDF summarization, Q&A, data extraction, and translation."""

    @property
    def system_prompt(self) -> str:
        return (
            "You are AstraMind AI, a document analysis expert. "
            "When working with documents:\n"
            "  - Summarize clearly with key points as bullet lists\n"
            "  - Answer questions with direct references to the source\n"
            "  - Extract structured data in clean JSON when asked\n"
            "  - Preserve the original meaning when translating\n"
            "Be thorough, accurate, and cite sections where possible."
        )

    async def handle(self, request: RouterRequest, ai_response: str) -> dict[str, Any]:
        task = request.metadata.get("task", "summarize")
        file_id = request.metadata.get("file_id", "")

        data: dict[str, Any] = {
            "type": "pdf",
            "task": task,
            "file_id": file_id,
        }

        if task == "summarize":
            data["summary"] = ai_response
            data["bullet_points"] = self._extract_bullets(ai_response)
        elif task == "qa":
            data["answer"] = ai_response
            data["question"] = request.metadata.get("question", request.message)
        elif task == "extract":
            data["extracted_data"] = ai_response
        elif task == "translate":
            data["translation"] = ai_response
            data["target_language"] = request.metadata.get("target_language", "en")

        return data

    @property
    def suggested_actions(self) -> list[str]:
        return ["Ask a follow-up question", "Export summary", "Translate document", "Extract data"]

    def _extract_bullets(self, text: str) -> list[str]:
        import re
        lines = text.splitlines()
        return [
            re.sub(r"^[\-\*\•]\s*", "", line).strip()
            for line in lines
            if re.match(r"^[\-\*\•]\s+", line)
        ]
