"""
AI Router schemas — request/response models for the intelligent request classifier.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


# ── Category Enum ─────────────────────────────────────────────────────────────

class RequestCategory(str, Enum):
    CHAT = "chat"
    CODE = "code"
    PDF = "pdf"
    IMAGE = "image"
    VOICE = "voice"
    STUDY_PLANNER = "study_planner"
    QUIZ = "quiz"
    GENERAL = "general"


# ── Supported models ───────────────────────────────────────────────────────────

AIModel = Literal["gpt-4o", "gpt-4o-mini", "claude-3-5-sonnet", "gemini-pro"]


# ── Core request/response ──────────────────────────────────────────────────────

class RouterRequest(BaseModel):
    """Single entry-point for all AI requests. The router classifies and dispatches."""

    message: str = Field(..., min_length=1, max_length=32_000, description="User message or prompt")
    model: AIModel = Field("gpt-4o", description="AI model to use for the response")
    context: list[dict[str, str]] = Field(
        default_factory=list,
        description="Prior conversation turns [{role, content}, ...]",
    )
    # Optional overrides — skip classification and force a category
    force_category: RequestCategory | None = Field(
        None, description="Skip classification and force a specific category"
    )
    # Per-category extras (passed through to handlers)
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Extra data for specific handlers (e.g. file_id for PDF, topic for Quiz)",
    )
    # Generation parameters
    max_tokens: int = Field(2048, ge=1, le=8192)
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    stream: bool = Field(False, description="Reserved for future streaming support")


class ClassificationResult(BaseModel):
    """Output of the classifier — category + confidence breakdown."""

    category: RequestCategory
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in chosen category")
    scores: dict[str, float] = Field(
        default_factory=dict, description="Raw score for every category"
    )
    method: Literal["keyword", "ai", "forced"] = Field(
        "keyword", description="How the classification was determined"
    )
    reasoning: str = Field("", description="Optional explanation of why this category was chosen")


class RouterResponse(BaseModel):
    """Full response returned by the AI router endpoint."""

    classification: ClassificationResult
    content: str = Field(..., description="AI-generated response text")
    model: str
    tokens_used: int = Field(0)
    category_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Category-specific structured output (e.g. quiz questions, study plan)",
    )
    suggested_actions: list[str] = Field(
        default_factory=list,
        description="UI-level follow-up actions the client may offer the user",
    )


# ── Category-specific metadata models ─────────────────────────────────────────

class CodeMeta(BaseModel):
    language: str = ""
    task: Literal["generate", "debug", "explain", "review", "optimize"] = "generate"


class PDFMeta(BaseModel):
    file_id: str = ""
    task: Literal["summarize", "qa", "extract", "translate"] = "summarize"
    question: str = ""


class ImageMeta(BaseModel):
    task: Literal["analyze", "generate", "edit", "ocr"] = "generate"
    image_url: str = ""


class VoiceMeta(BaseModel):
    task: Literal["transcribe", "tts", "translate"] = "transcribe"
    audio_url: str = ""
    target_language: str = "en"


class StudyPlannerMeta(BaseModel):
    subject: str = ""
    duration_days: int = Field(7, ge=1, le=365)
    level: Literal["beginner", "intermediate", "advanced"] = "intermediate"


class QuizMeta(BaseModel):
    topic: str = ""
    num_questions: int = Field(5, ge=1, le=50)
    difficulty: Literal["easy", "medium", "hard"] = "medium"
    question_type: Literal["mcq", "true_false", "short_answer", "mixed"] = "mcq"
