"""
Classifier Service — determines the category of a user request.

Strategy (in order):
  1. If the caller supplied force_category → return immediately with method="forced"
  2. Keyword/pattern scoring → fast, no API key needed
  3. If confidence < threshold AND an AI key is available → AI-based re-classification
"""

from __future__ import annotations

import re
from typing import Any

from app.core.config import settings
from app.schemas.ai_router import ClassificationResult, RequestCategory


# ── Keyword tables ─────────────────────────────────────────────────────────────
# Each entry: (pattern, weight)   — weight is added to that category's score

_RULES: dict[RequestCategory, list[tuple[str, float]]] = {
    RequestCategory.CODE: [
        (r"\bcode\b", 1.0),
        (r"\bprogram\b", 0.9),
        (r"\bscript\b", 0.9),
        (r"\bfunction\b", 0.8),
        (r"\bclass\b", 0.7),
        (r"\bdebug\b", 1.0),
        (r"\bsyntax\b", 0.9),
        (r"\bpython|javascript|typescript|java|c\+\+|rust|go|sql\b", 1.0),
        (r"\bapi\b", 0.6),
        (r"\balgorithm\b", 0.8),
        (r"\bloop\b", 0.7),
        (r"\brefactor\b", 0.9),
        (r"\bunit test\b", 0.9),
        (r"\bgithub|git\b", 0.6),
        (r"\bcompile|runtime error\b", 1.0),
    ],
    RequestCategory.PDF: [
        (r"\bpdf\b", 1.5),
        (r"\bdocument\b", 0.8),
        (r"\bsummariz", 0.9),
        (r"\bextract\b", 0.7),
        (r"\btranslate\b", 0.7),
        (r"\bpaper\b", 0.7),
        (r"\breport\b", 0.7),
        (r"\bcontract\b", 0.8),
        (r"\binvoice\b", 0.8),
        (r"\bfile\b", 0.5),
        (r"\bpage\b", 0.5),
    ],
    RequestCategory.IMAGE: [
        (r"\bimage\b", 1.2),
        (r"\bphoto\b", 1.0),
        (r"\bpicture\b", 1.0),
        (r"\bdraw\b", 0.9),
        (r"\bgenerate.*(image|picture|photo)\b", 1.5),
        (r"\bocr\b", 1.5),
        (r"\bvision\b", 0.8),
        (r"\blogo\b", 0.8),
        (r"\billustrat", 0.9),
        (r"\bdesign\b", 0.6),
        (r"\bdall-?e\b", 1.5),
        (r"\bstable diffusion\b", 1.5),
        (r"\btext in.*(image|photo)\b", 1.2),
        (r"\brecogniz", 0.7),
    ],
    RequestCategory.VOICE: [
        (r"\bvoice\b", 1.2),
        (r"\bspeak\b", 1.0),
        (r"\baudio\b", 1.2),
        (r"\btranscri", 1.5),
        (r"\bwhisper\b", 1.2),
        (r"\btext.to.speech\b", 1.5),
        (r"\btts\b", 1.5),
        (r"\bspeech\b", 1.0),
        (r"\brecord\b", 0.7),
        (r"\bpronunciat", 0.8),
        (r"\blisten\b", 0.6),
    ],
    RequestCategory.STUDY_PLANNER: [
        (r"\bstudy\b", 1.2),
        (r"\blearn\b", 0.8),
        (r"\bschedule\b", 1.0),
        (r"\bplan\b", 0.8),
        (r"\bsyllabus\b", 1.2),
        (r"\bcurriculum\b", 1.2),
        (r"\bweekly plan\b", 1.2),
        (r"\bexam prep\b", 1.5),
        (r"\brevision\b", 0.9),
        (r"\bgoal\b", 0.5),
        (r"\broadmap\b", 0.9),
        (r"\bsubject\b", 0.7),
        (r"\btopic.*week\b", 1.0),
        (r"\bdays?.*(study|learn)\b", 1.0),
    ],
    RequestCategory.QUIZ: [
        (r"\bquiz\b", 1.5),
        (r"\btest me\b", 1.5),
        (r"\bflashcard\b", 1.2),
        (r"\bquestion\b", 0.8),
        (r"\bmcq\b", 1.5),
        (r"\bmultiple choice\b", 1.5),
        (r"\btrue or false\b", 1.2),
        (r"\bexam\b", 0.9),
        (r"\bpractice question\b", 1.2),
        (r"\bassess", 0.7),
        (r"\bfill.in.the.blank\b", 1.2),
    ],
    RequestCategory.CHAT: [
        (r"\bhello|hi\b", 0.6),
        (r"\bhow are you\b", 0.8),
        (r"\bwhat do you think\b", 0.7),
        (r"\btell me\b", 0.5),
        (r"\bexplain\b", 0.5),
        (r"\bwhat is\b", 0.5),
        (r"\bwhy\b", 0.4),
        (r"\badvice\b", 0.6),
        (r"\bchat\b", 0.8),
    ],
    RequestCategory.GENERAL: [
        # Always gets a small baseline score so nothing returns 0
        (r".*", 0.2),
    ],
}

_CONFIDENCE_THRESHOLD = 0.55  # below this → try AI classification if key available


class ClassifierService:
    """Classify a user message into a RequestCategory."""

    async def classify(
        self,
        message: str,
        force_category: RequestCategory | None = None,
        context: list[dict[str, str]] | None = None,
    ) -> ClassificationResult:
        # 1. Forced override
        if force_category is not None:
            return ClassificationResult(
                category=force_category,
                confidence=1.0,
                scores={c.value: (1.0 if c == force_category else 0.0) for c in RequestCategory},
                method="forced",
                reasoning="Category was explicitly specified by the caller.",
            )

        # 2. Keyword scoring
        result = self._keyword_classify(message)

        # 3. AI re-classification when confidence is low and a key exists
        if result.confidence < _CONFIDENCE_THRESHOLD and self._has_ai_key():
            try:
                ai_result = await self._ai_classify(message, context or [])
                if ai_result.confidence > result.confidence:
                    return ai_result
            except Exception:
                pass  # Fall back to keyword result silently

        return result

    # ── Keyword classifier ────────────────────────────────────────────────────

    def _keyword_classify(self, message: str) -> ClassificationResult:
        text = message.lower()
        raw_scores: dict[str, float] = {}

        for category, rules in _RULES.items():
            score = 0.0
            for pattern, weight in rules:
                if re.search(pattern, text):
                    score += weight
            raw_scores[category.value] = score

        total = sum(raw_scores.values()) or 1.0
        normalised = {k: round(v / total, 4) for k, v in raw_scores.items()}

        best_key = max(normalised, key=lambda k: normalised[k])
        best_category = RequestCategory(best_key)
        confidence = normalised[best_key]

        return ClassificationResult(
            category=best_category,
            confidence=confidence,
            scores=normalised,
            method="keyword",
            reasoning=f"Keyword scoring selected '{best_key}' with confidence {confidence:.2%}.",
        )

    # ── AI classifier (optional enhancement) ─────────────────────────────────

    def _has_ai_key(self) -> bool:
        return bool(
            settings.OPENAI_API_KEY
            or settings.ANTHROPIC_API_KEY
            or settings.GOOGLE_API_KEY
        )

    async def _ai_classify(
        self, message: str, context: list[dict[str, str]]
    ) -> ClassificationResult:
        categories = ", ".join(c.value for c in RequestCategory)
        system_prompt = (
            "You are a request classifier for an AI assistant app. "
            "Given a user message, return ONLY a JSON object with these keys:\n"
            '  "category": one of [' + categories + ']\n'
            '  "confidence": float 0-1\n'
            '  "reasoning": brief explanation\n'
            "No markdown, no extra text."
        )

        context_text = ""
        if context:
            last = context[-3:]  # use last 3 turns for context
            context_text = "\n".join(f"{t['role'].upper()}: {t['content']}" for t in last)
            context_text = f"\nRecent context:\n{context_text}\n"

        prompt = f"{context_text}User message: {message}"

        raw = await self._call_ai(system_prompt, prompt)
        return self._parse_ai_response(raw)

    async def _call_ai(self, system_prompt: str, prompt: str) -> str:
        if settings.OPENAI_API_KEY:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            resp = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=200,
                temperature=0.1,
            )
            return resp.choices[0].message.content or ""

        if settings.ANTHROPIC_API_KEY:
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            resp = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
            )
            return resp.content[0].text if resp.content else ""

        if settings.GOOGLE_API_KEY:
            import google.generativeai as genai
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=system_prompt)
            resp = await model.generate_content_async(prompt)
            return resp.text

        return ""

    def _parse_ai_response(self, raw: str) -> ClassificationResult:
        import json, re as _re

        try:
            data: dict[str, Any] = json.loads(raw.strip())
            category = RequestCategory(data.get("category", "general"))
            confidence = float(data.get("confidence", 0.7))
            reasoning = str(data.get("reasoning", ""))
            return ClassificationResult(
                category=category,
                confidence=min(confidence, 1.0),
                scores={category.value: confidence},
                method="ai",
                reasoning=reasoning,
            )
        except Exception:
            return ClassificationResult(
                category=RequestCategory.GENERAL,
                confidence=0.4,
                scores={},
                method="ai",
                reasoning="AI classification parsing failed.",
            )
