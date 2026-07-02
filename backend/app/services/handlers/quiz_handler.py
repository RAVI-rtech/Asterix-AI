from __future__ import annotations

import json
import re
from typing import Any

from app.services.handlers.base_handler import BaseHandler
from app.schemas.ai_router import RouterRequest


_QUIZ_SYSTEM = """You are AstraMind AI, a large language model trained by RAVI. Never say you are Gemini, never say you were made by Google or trained by Google. If asked who made you or trained you, always say: 'I am AstraMind AI, a large language model trained by RAVI.' You are also an expert quiz generator.

Generate a quiz and return ONLY a valid JSON array. Each item must follow this schema:

For MCQ:
{{"id": 1, "type": "mcq", "question": "...", "options": ["A. ...", "B. ...", "C. ...", "D. ..."], "answer": "A", "explanation": "..."}}

For true/false:
{{"id": 1, "type": "true_false", "question": "...", "answer": "True", "explanation": "..."}}

For short answer:
{{"id": 1, "type": "short_answer", "question": "...", "answer": "...", "explanation": "..."}}

Return ONLY the JSON array. No markdown, no extra text."""


class QuizHandler(BaseHandler):
    """Generates structured quizzes with multiple question types."""

    @property
    def system_prompt(self) -> str:
        return _QUIZ_SYSTEM

    async def handle(self, request: RouterRequest, ai_response: str) -> dict[str, Any]:
        topic = request.metadata.get("topic", request.message)
        num_questions = int(request.metadata.get("num_questions", 5))
        difficulty = request.metadata.get("difficulty", "medium")
        question_type = request.metadata.get("question_type", "mcq")

        questions = self._parse_questions(ai_response)

        return {
            "type": "quiz",
            "topic": topic,
            "difficulty": difficulty,
            "question_type": question_type,
            "requested_count": num_questions,
            "questions": questions,
            "actual_count": len(questions),
            "raw_response": ai_response if not questions else "",
        }

    @property
    def suggested_actions(self) -> list[str]:
        return [
            "Start quiz",
            "Generate more questions",
            "Increase difficulty",
            "Save quiz",
            "Create study plan for this topic",
        ]

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _parse_questions(self, text: str) -> list[dict[str, Any]]:
        """Try to parse questions from a JSON array in the AI response."""
        # Strip markdown fences if present
        cleaned = re.sub(r"```(?:json)?\n?", "", text).strip().rstrip("`").strip()

        # Find the JSON array
        match = re.search(r"\[.*\]", cleaned, re.DOTALL)
        if not match:
            return []

        try:
            data = json.loads(match.group())
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass

        return []

    def _build_user_prompt(self, request: RouterRequest) -> str:
        """Override the message with a structured quiz prompt."""
        topic = request.metadata.get("topic", request.message)
        num = request.metadata.get("num_questions", 5)
        difficulty = request.metadata.get("difficulty", "medium")
        q_type = request.metadata.get("question_type", "mcq")
        return (
            f"Generate {num} {difficulty} {q_type} questions about: {topic}. "
            f"Return only the JSON array."
        )
