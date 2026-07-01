"""
Router Service — orchestrates classification → handler dispatch → AI call → response.
"""

from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.schemas.ai_router import (
    ClassificationResult,
    RequestCategory,
    RouterRequest,
    RouterResponse,
)
from app.services.classifier_service import ClassifierService
from app.services.handlers import (
    BaseHandler,
    ChatHandler,
    CodeHandler,
    GeneralHandler,
    ImageHandler,
    PDFHandler,
    QuizHandler,
    StudyPlannerHandler,
    VoiceHandler,
)


class RouterService:
    """
    Main orchestrator.

    Flow:
      request → ClassifierService.classify() → pick handler
              → build AI messages → call AI model
              → handler.handle() → RouterResponse
    """

    def __init__(self) -> None:
        self._classifier = ClassifierService()
        self._registry: dict[RequestCategory, BaseHandler] = self._build_registry()

    def _build_registry(self) -> dict[RequestCategory, BaseHandler]:
        return {
            RequestCategory.CHAT: ChatHandler(),
            RequestCategory.CODE: CodeHandler(),
            RequestCategory.PDF: PDFHandler(),
            RequestCategory.IMAGE: ImageHandler(),
            RequestCategory.VOICE: VoiceHandler(),
            RequestCategory.STUDY_PLANNER: StudyPlannerHandler(),
            RequestCategory.QUIZ: QuizHandler(),
            RequestCategory.GENERAL: GeneralHandler(),
        }

    async def route(self, request: RouterRequest) -> RouterResponse:
        # 1. Classify
        classification = await self._classifier.classify(
            message=request.message,
            force_category=request.force_category,
            context=request.context,
        )

        # 2. Pick handler
        handler = self._registry.get(classification.category, self._registry[RequestCategory.GENERAL])

        # 3. Build prompt (quiz overrides the message)
        prompt = self._build_prompt(request, handler, classification.category)

        # 4. Call AI
        ai_result = await self._call_ai(
            system_prompt=handler.system_prompt,
            prompt=prompt,
            context=request.context,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )

        # 5. Post-process via handler
        category_data = await handler.handle(request, ai_result["content"])

        return RouterResponse(
            classification=classification,
            content=ai_result["content"],
            model=ai_result["model"],
            tokens_used=ai_result["tokens_used"],
            category_data=category_data,
            suggested_actions=handler.suggested_actions,
        )

    # ── Private helpers ───────────────────────────────────────────────────────

    def _build_prompt(
        self,
        request: RouterRequest,
        handler: BaseHandler,
        category: RequestCategory,
    ) -> str:
        """Let quiz handler override the prompt; others use message as-is."""
        if category == RequestCategory.QUIZ and hasattr(handler, "_build_user_prompt"):
            return handler._build_user_prompt(request)  # type: ignore[attr-defined]
        return request.message

    async def _call_ai(
        self,
        system_prompt: str,
        prompt: str,
        context: list[dict[str, str]],
        model: str,
        max_tokens: int,
        temperature: float,
    ) -> dict[str, Any]:
        """Dispatch to the correct AI provider; fall back to stub when no key."""
        if model.startswith("gpt"):
            return await self._openai(system_prompt, prompt, context, model, max_tokens, temperature)
        if model.startswith("claude"):
            return await self._anthropic(system_prompt, prompt, context, model, max_tokens, temperature)
        if model.startswith("gemini"):
            return await self._google(system_prompt, prompt, context, model, max_tokens, temperature)
        return self._stub(model)

    # ── Provider adapters ─────────────────────────────────────────────────────

    async def _openai(
        self, system_prompt: str, prompt: str, context: list[dict[str, str]],
        model: str, max_tokens: int, temperature: float,
    ) -> dict[str, Any]:
        if not settings.OPENAI_API_KEY:
            return self._stub(model)

        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        messages = [{"role": "system", "content": system_prompt}, *context, {"role": "user", "content": prompt}]
        resp = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return {
            "content": resp.choices[0].message.content or "",
            "model": model,
            "tokens_used": resp.usage.total_tokens if resp.usage else 0,
        }

    async def _anthropic(
        self, system_prompt: str, prompt: str, context: list[dict[str, str]],
        model: str, max_tokens: int, temperature: float,
    ) -> dict[str, Any]:
        if not settings.ANTHROPIC_API_KEY:
            return self._stub(model)

        import anthropic
        client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        messages = [*context, {"role": "user", "content": prompt}]
        resp = await client.messages.create(
            model="claude-3-5-sonnet-20241022",
            system=system_prompt,
            messages=messages,
            max_tokens=max_tokens,
        )
        return {
            "content": resp.content[0].text if resp.content else "",
            "model": model,
            "tokens_used": resp.usage.input_tokens + resp.usage.output_tokens,
        }

    async def _google(
        self, system_prompt: str, prompt: str, context: list[dict[str, str]],
        model: str, max_tokens: int, temperature: float,
    ) -> dict[str, Any]:
        if not settings.GOOGLE_API_KEY:
            return self._stub(model)

        import google.generativeai as genai
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        gemini = genai.GenerativeModel("gemini-1.5-pro", system_instruction=system_prompt)
        history = [{"role": t["role"], "parts": [t["content"]]} for t in context]
        chat = gemini.start_chat(history=history)
        resp = await chat.send_message_async(prompt)
        return {
            "content": resp.text,
            "model": model,
            "tokens_used": 0,
        }

    @staticmethod
    def _stub(model: str) -> dict[str, Any]:
        return {
            "content": (
                f"[{model}] AI features are not yet configured. "
                "Add your API keys to backend/.env to enable real responses."
            ),
            "model": model,
            "tokens_used": 0,
        }
