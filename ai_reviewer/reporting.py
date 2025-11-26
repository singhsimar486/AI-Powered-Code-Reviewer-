"""Reporting utilities for the AI reviewer."""

from __future__ import annotations

import dataclasses
import json
from typing import Iterable, List, Optional


@dataclasses.dataclass
class Issue:
    path: str
    line: Optional[int]
    column: Optional[int]
    severity: str
    message: str
    source: str

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class Report:
    issues: List[Issue]

    def add_issue(self, issue: Issue) -> None:
        self.issues.append(issue)

    def extend(self, issues: Iterable[Issue]) -> None:
        self.issues.extend(issues)

    def sorted_by_severity(self) -> List[Issue]:
        order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        return sorted(self.issues, key=lambda i: (order.get(i.severity, 5), i.path, i.line or 0))

    def to_dict(self, ai_summary: str | None = None) -> dict:
        payload: dict = {"issues": [issue.to_dict() for issue in self.sorted_by_severity()]}
        if ai_summary:
            payload["ai_summary"] = ai_summary
        return payload

    def to_json(self, ai_summary: str | None = None) -> str:
        return json.dumps(self.to_dict(ai_summary), indent=2)

    def summary(self, limit: int = 20) -> str:
        lines = []
        for issue in self.sorted_by_severity()[:limit]:
            location = f"{issue.path}:{issue.line}" if issue.line else issue.path
            lines.append(f"[{issue.severity.upper()}] {location} - {issue.message} ({issue.source})")
        if len(self.issues) > limit:
            lines.append(f"...and {len(self.issues) - limit} more issues")
        return "\n".join(lines)
