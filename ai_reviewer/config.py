"""Configuration handling for the AI-powered reviewer."""

from __future__ import annotations

import dataclasses
import pathlib
from typing import Any, Dict, List

try:  # Optional dependency to keep the tool runnable without PyYAML
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - executed when PyYAML is missing
    yaml = None

DEFAULT_CONFIG = {
    "python": {
        "enable_ast_rules": True,
        "linters": ["flake8", "bandit"],
    },
    "openai": {
        "model": "gpt-4.1-mini",
        "enabled": False,
        "max_context_messages": 10,
    },
    "report": {
        "max_issues": 100,
    },
}


@dataclasses.dataclass
class Config:
    """Typed configuration loaded from `.ai-reviewer.yml`."""

    python_linters: List[str]
    python_ast_rules: bool
    openai_model: str
    openai_enabled: bool
    openai_max_messages: int
    report_max_issues: int

    @classmethod
    def from_file(cls, path: pathlib.Path | None = None) -> "Config":
        config_path = path or pathlib.Path(".ai-reviewer.yml")
        merged = DEFAULT_CONFIG.copy()
        if config_path.exists() and yaml is None:
            # PyYAML is optional; gracefully fall back to defaults when missing
            return cls.from_dict(merged)
        if config_path.exists() and yaml is not None:
            with config_path.open("r", encoding="utf-8") as f:
                user_cfg: Dict[str, Any] = yaml.safe_load(f) or {}
            merged = _deep_merge(merged, user_cfg)
        return cls.from_dict(merged)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        python_cfg = data.get("python", {})
        openai_cfg = data.get("openai", {})
        report_cfg = data.get("report", {})
        return cls(
            python_linters=list(python_cfg.get("linters", [])),
            python_ast_rules=bool(python_cfg.get("enable_ast_rules", True)),
            openai_model=str(openai_cfg.get("model", "gpt-4.1-mini")),
            openai_enabled=bool(openai_cfg.get("enabled", False)),
            openai_max_messages=int(openai_cfg.get("max_context_messages", 10)),
            report_max_issues=int(report_cfg.get("max_issues", 100)),
        )


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result: Dict[str, Any] = {**base}
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            result[key] = _deep_merge(base[key], value)  # type: ignore[index]
        else:
            result[key] = value
    return result
