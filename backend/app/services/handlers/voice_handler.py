from __future__ import annotations

from typing import Any

from app.services.handlers.base_handler import BaseHandler
from app.schemas.ai_router import RouterRequest


class VoiceHandler(BaseHandler):
    """Handles voice-related requests: transcription help, TTS prep, translation."""

    @property
    def system_prompt(self) -> str:
        return (
            "You are AstraMind AI, a voice and audio specialist. "
            "For transcription: clean up and format the transcribed text accurately. "
            "For text-to-speech: optimize the text for natural-sounding speech — "
            "add punctuation, remove or spell out symbols, and keep sentences short. "
            "For translation: provide accurate, natural translations with pronunciation hints when useful."
        )

    async def handle(self, request: RouterRequest, ai_response: str) -> dict[str, Any]:
        task = request.metadata.get("task", "transcribe")
        audio_url = request.metadata.get("audio_url", "")

        return {
            "type": "voice",
            "task": task,
            "audio_url": audio_url,
            "processed_text": ai_response,
            "target_language": request.metadata.get("target_language", "en"),
            "tts_ready": task == "tts",
        }

    @property
    def suggested_actions(self) -> list[str]:
        return ["Play audio", "Save transcript", "Translate", "Copy text"]
