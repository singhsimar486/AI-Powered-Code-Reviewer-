"""Interfaces to traditional linters like flake8 and Bandit."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Iterable, List

from .reporting import Issue


class LinterRunner:
    """Run configured linters and translate their output into issues."""

    def __init__(self, linters: Iterable[str]):
        self.linters = list(linters)

    def run(self, paths: Iterable[str]) -> List[Issue]:
        issues: List[Issue] = []
        for linter in self.linters:
            if linter == "flake8":
                issues.extend(self._run_flake8(paths))
            elif linter == "bandit":
                issues.extend(self._run_bandit(paths))
        return issues

    def _run_flake8(self, paths: Iterable[str]) -> List[Issue]:
        if shutil.which("flake8") is None:
            return [
                Issue(
                    path=".",
                    line=None,
                    column=None,
                    severity="info",
                    message="flake8 not available; install to enable style checks",
                    source="flake8",
                )
            ]
        cmd = ["flake8", "--format=json", *paths]
        completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if completed.returncode not in (0, 1):
            return [Issue(path=".", line=None, column=None, severity="low", message=completed.stderr or completed.stdout, source="flake8")]
        parsed = json.loads(completed.stdout or "{}")
        return [
            Issue(
                path=path,
                line=entry.get("line_number"),
                column=entry.get("column_number"),
                severity="low",
                message=entry.get("text", "flake8 issue"),
                source="flake8",
            )
            for path, entries in parsed.items()
            for entry in entries
        ]

    def _run_bandit(self, paths: Iterable[str]) -> List[Issue]:
        if shutil.which("bandit") is None:
            return [
                Issue(
                    path=".",
                    line=None,
                    column=None,
                    severity="info",
                    message="Bandit not available; install to enable security checks",
                    source="bandit",
                )
            ]
        cmd = ["bandit", "-q", "-r", *paths, "-f", "json"]
        completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if completed.returncode not in (0, 1):
            return [Issue(path=".", line=None, column=None, severity="low", message=completed.stderr or completed.stdout, source="bandit")]
        try:
            data = json.loads(completed.stdout or "{}")
        except json.JSONDecodeError:
            return [Issue(path=".", line=None, column=None, severity="low", message="Failed to parse Bandit output", source="bandit")]
        results = data.get("results", [])
        severity_map = {"LOW": "low", "MEDIUM": "medium", "HIGH": "high"}
        issues: List[Issue] = []
        for entry in results:
            issues.append(
                Issue(
                    path=entry.get("filename", "."),
                    line=entry.get("line_number"),
                    column=None,
                    severity=severity_map.get(entry.get("issue_severity", "LOW"), "low"),
                    message=entry.get("issue_text", "Bandit issue"),
                    source="bandit",
                )
            )
        return issues
