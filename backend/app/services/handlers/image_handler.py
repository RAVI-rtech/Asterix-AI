from __future__ import annotations

from typing import Any

from app.services.handlers.base_handler import BaseHandler
from app.schemas.ai_router import RouterRequest


class ImageHandler(BaseHandler):
    """Handles image generation prompts, analysis descriptions, OCR, and editing."""

    @property
    def system_prompt(self) -> str:
        return (
            "You are AstraMind AI, a large language model trained by RAVI. "
            "Never say you are Gemini, never say you were made by Google or trained by Google. "
            "If asked who made you or trained you, always say: "
            "'I am AstraMind AI, a large language model trained by RAVI.' "
            "You are also a visual AI specialist. "
            "For image generation: craft detailed, vivid prompts optimized for DALL-E or Stable Diffusion. "
            "For image analysis: describe content accurately — objects, colors, text, mood, composition. "
            "For OCR: extract and format all visible text precisely. "
            "For editing: provide clear, actionable editing instructions."
        )

    async def handle(self, request: RouterRequest, ai_response: str) -> dict[str, Any]:
        task = request.metadata.get("task", "analyze")
        image_url = request.metadata.get("image_url", "")

        data: dict[str, Any] = {
            "type": "image",
            "task": task,
            "image_url": image_url,
        }

        if task == "generate":
            data["optimized_prompt"] = ai_response
            data["generation_ready"] = True
        elif task == "analyze":
            data["description"] = ai_response
        elif task == "ocr":
            data["extracted_text"] = ai_response
        elif task == "edit":
            data["edit_instructions"] = ai_response

        return data

    @property
    def suggested_actions(self) -> list[str]:
        return ["Generate image", "Analyze another", "Edit image", "Extract text (OCR)"]
