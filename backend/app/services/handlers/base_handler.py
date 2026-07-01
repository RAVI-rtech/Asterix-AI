"""
BaseHandler — abstract interface every category handler must implement.

To add a new category:
  1. Subclass BaseHandler
  2. Implement `system_prompt`, `handle`, and `suggested_actions`
  3. Register it in RouterService._build_registry()
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.schemas.ai_router import RouterRequest, RouterResponse


class BaseHandler(ABC):
    """Abstract base class for category-specific AI handlers."""

    # ── Required overrides ────────────────────────────────────────────────────

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """System prompt injected before every request for this category."""

    @abstractmethod
    async def handle(self, request: RouterRequest, ai_response: str) -> dict[str, Any]:
        """
        Post-process the raw AI response into category_data.

        Args:
            request:     Original router request (includes message + metadata)
            ai_response: Raw text returned by the AI model

        Returns:
            dict that will be merged into RouterResponse.category_data
        """

    @property
    def suggested_actions(self) -> list[str]:
        """UI-level follow-up actions to surface after this handler runs."""
        return []

    # ── Helpers ───────────────────────────────────────────────────────────────

    def build_messages(self, request: RouterRequest) -> list[dict[str, str]]:
        """Assemble the messages list: system + prior context + current message."""
        msgs: list[dict[str, str]] = [{"role": "system", "content": self.system_prompt}]
        msgs.extend(request.context)
        msgs.append({"role": "user", "content": request.message})
        return msgs
