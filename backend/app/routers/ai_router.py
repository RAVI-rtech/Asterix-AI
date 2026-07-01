"""
AI Router — intelligent request classification and dispatch.

Endpoints:
  POST /api/ai/route      — classify + dispatch + respond (main endpoint)
  POST /api/ai/classify   — classify only, no AI call
  POST /api/ai/complete   — raw completion (bypass classifier)
  GET  /api/ai/models     — list available models
  GET  /api/ai/categories — list all supported categories
"""

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.ai_router import (
    AIModel,
    ClassificationResult,
    RequestCategory,
    RouterRequest,
    RouterResponse,
)
from app.services.classifier_service import ClassifierService
from app.services.router_service import RouterService

router = APIRouter()


# ── Shared service instances (stateless, safe to reuse) ───────────────────────

_router_service = RouterService()
_classifier_service = ClassifierService()


# ── 1. Main route endpoint ─────────────────────────────────────────────────────

@router.post(
    "/route",
    response_model=RouterResponse,
    summary="Classify and respond",
    description=(
        "The primary endpoint. Automatically classifies the user message into one of "
        "8 categories (Chat, Code, PDF, Image, Voice, Study Planner, Quiz, General), "
        "dispatches it to the appropriate handler, calls the AI model, and returns a "
        "structured response with category-specific data and suggested UI actions."
    ),
)
async def route_request(
    body: RouterRequest,
    current_user: User = Depends(get_current_user),
) -> RouterResponse:
    try:
        return await _router_service.route(body)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Router error: {exc}",
        ) from exc


# ── 2. Classify-only endpoint ──────────────────────────────────────────────────

class ClassifyRequest(BaseModel):
    message: str
    context: list[dict] = []
    force_category: RequestCategory | None = None


@router.post(
    "/classify",
    response_model=ClassificationResult,
    summary="Classify only",
    description=(
        "Classify a message without calling an AI model. "
        "Useful for previewing how a request would be routed."
    ),
)
async def classify_only(
    body: ClassifyRequest,
    current_user: User = Depends(get_current_user),
) -> ClassificationResult:
    return await _classifier_service.classify(
        message=body.message,
        force_category=body.force_category,
        context=body.context,
    )


# ── 3. Raw completion (bypass classifier) ─────────────────────────────────────

class CompletionRequest(BaseModel):
    prompt: str
    model: AIModel = "gpt-4o"
    system_prompt: str = "You are AstraMind AI, a helpful assistant."
    max_tokens: int = 2048
    temperature: float = 0.7


class CompletionResponse(BaseModel):
    content: str
    model: str
    tokens_used: int


@router.post(
    "/complete",
    response_model=CompletionResponse,
    summary="Raw completion",
    description="Send a prompt directly to the AI model, bypassing classification.",
)
async def complete(
    body: CompletionRequest,
    current_user: User = Depends(get_current_user),
) -> CompletionResponse:
    from app.services.ai_service import AIService
    service = AIService()
    result = await service.complete(
        prompt=body.prompt,
        model=body.model,
        system_prompt=body.system_prompt,
        max_tokens=body.max_tokens,
        temperature=body.temperature,
    )
    return CompletionResponse(**result)


# ── 4. Model listing ───────────────────────────────────────────────────────────

@router.get(
    "/models",
    summary="List AI models",
    description="Return all available AI models and their metadata.",
)
async def list_models(current_user: User = Depends(get_current_user)):
    return {
        "models": [
            {
                "id": "gpt-4o",
                "name": "AstraMind AI",
                "provider": "openai",
                "description": "Most capable · Recommended",
                "context_window": 128_000,
            },
            {
                "id": "gpt-4o-mini",
                "name": "AstraMind AI Mini",
                "provider": "openai",
                "description": "Fast & efficient",
                "context_window": 128_000,
            },
            {
                "id": "claude-3-5-sonnet",
                "name": "AstraMind AI 3.5",
                "provider": "anthropic",
                "description": "Excellent reasoning",
                "context_window": 200_000,
            },
            {
                "id": "gemini-pro",
                "name": "AstraMind AI Pro",
                "provider": "google",
                "description": "Our best model",
                "context_window": 1_000_000,
            },
        ]
    }


# ── 5. Category listing ────────────────────────────────────────────────────────

@router.get(
    "/categories",
    summary="List categories",
    description="Return all supported request categories with descriptions.",
)
async def list_categories(current_user: User = Depends(get_current_user)):
    return {
        "categories": [
            {
                "id": RequestCategory.CHAT,
                "label": "Chat",
                "description": "General conversation and Q&A",
                "icon": "chatbubble-ellipses-outline",
            },
            {
                "id": RequestCategory.CODE,
                "label": "Code",
                "description": "Code generation, debugging, and explanation",
                "icon": "code-slash-outline",
            },
            {
                "id": RequestCategory.PDF,
                "label": "PDF",
                "description": "Document summarization, Q&A, extraction, translation",
                "icon": "document-text-outline",
            },
            {
                "id": RequestCategory.IMAGE,
                "label": "Image",
                "description": "Image generation, analysis, OCR, and editing",
                "icon": "images-outline",
            },
            {
                "id": RequestCategory.VOICE,
                "label": "Voice",
                "description": "Speech-to-text, text-to-speech, and translation",
                "icon": "mic-outline",
            },
            {
                "id": RequestCategory.STUDY_PLANNER,
                "label": "Study Planner",
                "description": "Study schedules, learning roadmaps, revision plans",
                "icon": "calendar-outline",
            },
            {
                "id": RequestCategory.QUIZ,
                "label": "Quiz",
                "description": "MCQ, true/false, and short-answer quiz generation",
                "icon": "help-circle-outline",
            },
            {
                "id": RequestCategory.GENERAL,
                "label": "General",
                "description": "Fallback for requests that don't fit a specific category",
                "icon": "sparkles-outline",
            },
        ]
    }
