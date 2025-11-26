"""Wrapper around the OpenAI API to generate contextual suggestions."""

from __future__ import annotations

import os
from typing import Iterable, Optional

try:
    import openai
except ImportError:  # pragma: no cover - optional dependency
    openai = None  # type: ignore

from ai_reviewer.reporting import Issue


PROMPT_TEMPLATE = """
You are an expert code reviewer. Summarize the following issues and propose actionable fixes.
Return short bullet points.

Issues:
{issues}
"""


class OpenAIClient:
    def __init__(self, model: str, enabled: bool = False) -> None:
        self.model = model
        # Only enable when explicitly requested, the dependency is installed, and
        # an API key is present. Cast to bool because os.getenv returns a string.
        self.enabled = bool(enabled and openai is not None and os.getenv("OPENAI_API_KEY"))

    def summarize(self, issues: Iterable[Issue]) -> Optional[str]:
        if not self.enabled:
            return None
        formatted = "\n".join(
            f"- {issue.severity.upper()} {issue.path}:{issue.line or '?'} - {issue.message}" for issue in issues
        )
        prompt = PROMPT_TEMPLATE.format(issues=formatted)
        response = openai.ChatCompletion.create(
            model=self.model,  # type: ignore[attr-defined]
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
        )
        return response["choices"][0]["message"]["content"]  # type: ignore[index]
