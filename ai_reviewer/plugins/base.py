"""Plugin interface for language-specific analysis."""

from __future__ import annotations

from typing import Iterable, Protocol

from ai_reviewer.reporting import Issue


class Plugin(Protocol):
    """Plugin protocol for static analysis."""

    def analyze(self, paths: Iterable[str]) -> Iterable[Issue]:
        """Analyze the provided paths and yield issues."""

