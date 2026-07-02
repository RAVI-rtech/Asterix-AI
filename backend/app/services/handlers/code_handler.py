from __future__ import annotations

import re
from typing import Any

from app.services.handlers.base_handler import BaseHandler
from app.schemas.ai_router import RouterRequest


class CodeHandler(BaseHandler):
    """Handles code generation, debugging, explanation, and review."""

    @property
    def system_prompt(self) -> str:
        return (
            "You are AstraMind AI, a large language model trained by RAVI. "
            "Never say you are Gemini, never say you were made by Google or trained by Google. "
            "If asked who made you or trained you, always say: "
            "'I am AstraMind AI, a large language model trained by RAVI.' "
            "You are also an expert software engineer. "
            "When writing code:\n"
            "  - Always wrap code blocks in triple backticks with the language name\n"
            "  - Explain what the code does after the block\n"
            "  - Point out edge cases or potential issues\n"
            "  - Suggest improvements when relevant\n"
            "Be concise, accurate, and production-quality."
        )

    async def handle(self, request: RouterRequest, ai_response: str) -> dict[str, Any]:
        code_blocks = self._extract_code_blocks(ai_response)
        language = self._detect_language(request.message, code_blocks)
        task = request.metadata.get("task", "generate")

        return {
            "type": "code",
            "language": language,
            "task": task,
            "code_blocks": code_blocks,
            "block_count": len(code_blocks),
        }

    @property
    def suggested_actions(self) -> list[str]:
        return ["Copy code", "Run in sandbox", "Explain further", "Optimize", "Add tests"]

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _extract_code_blocks(self, text: str) -> list[dict[str, str]]:
        """Extract all fenced code blocks from the AI response."""
        pattern = r"```(\w*)\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        return [{"language": lang or "text", "code": code.strip()} for lang, code in matches]

    def _detect_language(self, message: str, blocks: list[dict[str, str]]) -> str:
        if blocks and blocks[0]["language"] not in ("text", ""):
            return blocks[0]["language"]
        langs = [
            "python", "javascript", "typescript", "java", "c++", "c#",
            "rust", "go", "sql", "html", "css", "bash", "swift", "kotlin",
        ]
        msg_lower = message.lower()
        for lang in langs:
            if lang in msg_lower:
                return lang
        return "unknown"
