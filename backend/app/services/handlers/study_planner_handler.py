from __future__ import annotations

import re
from typing import Any

from app.services.handlers.base_handler import BaseHandler
from app.schemas.ai_router import RouterRequest


class StudyPlannerHandler(BaseHandler):
    """Generates structured study plans, revision schedules, and learning roadmaps."""

    @property
    def system_prompt(self) -> str:
        return (
            "You are AstraMind AI, an expert learning coach and study planner. "
            "When creating study plans:\n"
            "  - Break the subject into logical daily or weekly sessions\n"
            "  - Include specific topics, resources, and goals per session\n"
            "  - Add review/revision checkpoints every few days\n"
            "  - Keep sessions realistic (1-3 hours each)\n"
            "  - Format the plan clearly with Day/Week headers\n"
            "  - End with tips tailored to the subject and learner level\n"
            "Be motivating, practical, and structured."
        )

    async def handle(self, request: RouterRequest, ai_response: str) -> dict[str, Any]:
        subject = request.metadata.get("subject", "")
        duration_days = int(request.metadata.get("duration_days", 7))
        level = request.metadata.get("level", "intermediate")

        sessions = self._parse_sessions(ai_response)

        return {
            "type": "study_planner",
            "subject": subject,
            "duration_days": duration_days,
            "level": level,
            "plan_text": ai_response,
            "sessions": sessions,
            "session_count": len(sessions),
        }

    @property
    def suggested_actions(self) -> list[str]:
        return [
            "Save study plan",
            "Set reminders",
            "Generate quiz for this topic",
            "Adjust difficulty",
            "Export as PDF",
        ]

    def _parse_sessions(self, text: str) -> list[dict[str, str]]:
        """Extract day/week sessions from the plan text."""
        sessions: list[dict[str, str]] = []
        current: dict[str, str] | None = None

        for line in text.splitlines():
            header = re.match(r"^(Day\s*\d+|Week\s*\d+)[:\s]*(.*)", line, re.IGNORECASE)
            if header:
                if current:
                    sessions.append(current)
                current = {
                    "label": header.group(1).strip(),
                    "title": header.group(2).strip(),
                    "content": "",
                }
            elif current and line.strip():
                current["content"] += line.strip() + " "

        if current:
            sessions.append(current)

        return sessions
