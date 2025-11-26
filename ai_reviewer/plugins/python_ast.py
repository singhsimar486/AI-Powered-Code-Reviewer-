"""AST-based rules for Python code."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Iterable, List

from ai_reviewer.reporting import Issue


class PythonAstAnalyzer:
    """Inspect Python files for semantic issues that linters may miss."""

    def __init__(self) -> None:
        self.rules = [
            self._detect_mutable_defaults,
            self._detect_bare_except,
            self._detect_print_statements,
        ]

    def analyze(self, paths: Iterable[str]) -> List[Issue]:
        issues: List[Issue] = []
        for path_str in paths:
            path = Path(path_str)
            if path.is_dir():
                for file in path.rglob("*.py"):
                    issues.extend(self._analyze_file(file))
            elif path.suffix == ".py":
                issues.extend(self._analyze_file(path))
        return issues

    def _analyze_file(self, file_path: Path) -> List[Issue]:
        issues: List[Issue] = []
        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(file_path))
        except (SyntaxError, OSError) as exc:
            issues.append(
                Issue(
                    path=str(file_path),
                    line=getattr(exc, "lineno", None),
                    column=getattr(exc, "offset", None),
                    severity="medium",
                    message=f"Failed to parse file: {exc}",
                    source="python-ast",
                )
            )
            return issues

        for rule in self.rules:
            issues.extend(rule(tree, file_path))
        return issues

    def _detect_mutable_defaults(self, tree: ast.AST, file_path: Path) -> List[Issue]:
        issues: List[Issue] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        issues.append(
                            Issue(
                                path=str(file_path),
                                line=node.lineno,
                                column=node.col_offset,
                                severity="medium",
                                message="Mutable default argument detected; use None and assign inside function",
                                source="python-ast",
                            )
                        )
        return issues

    def _detect_bare_except(self, tree: ast.AST, file_path: Path) -> List[Issue]:
        issues: List[Issue] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                issues.append(
                    Issue(
                        path=str(file_path),
                        line=node.lineno,
                        column=node.col_offset,
                        severity="high",
                        message="Bare except detected; catch specific exceptions",
                        source="python-ast",
                    )
                )
        return issues

    def _detect_print_statements(self, tree: ast.AST, file_path: Path) -> List[Issue]:
        issues: List[Issue] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "print":
                issues.append(
                    Issue(
                        path=str(file_path),
                        line=node.lineno,
                        column=node.col_offset,
                        severity="low",
                        message="print statement found; consider structured logging",
                        source="python-ast",
                    )
                )
        return issues
