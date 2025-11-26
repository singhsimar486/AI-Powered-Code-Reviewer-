"""Command-line interface for the AI-powered reviewer."""

from __future__ import annotations

import argparse
import pathlib
from typing import List

from ai_reviewer.config import Config
from ai_reviewer.linters import LinterRunner
from ai_reviewer.openai_client import OpenAIClient
from ai_reviewer.plugins.python_ast import PythonAstAnalyzer
from ai_reviewer.reporting import Issue, Report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI-powered static analysis")
    parser.add_argument("paths", nargs="*", default=["."], help="Paths to analyze")
    parser.add_argument("--config", "-c", type=pathlib.Path, help="Path to .ai-reviewer.yml")
    parser.add_argument("--max-issues", type=int, help="Limit number of reported issues")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of text summary")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = Config.from_file(args.config)
    report_limit = args.max_issues or config.report_max_issues

    report = Report(issues=[])

    # Traditional linters
    linter_runner = LinterRunner(config.python_linters)
    report.extend(linter_runner.run(args.paths))

    # AST-based analysis
    if config.python_ast_rules:
        ast_analyzer = PythonAstAnalyzer()
        report.extend(ast_analyzer.analyze(args.paths))

    # Trim report if necessary
    if len(report.issues) > report_limit:
        report.issues = report.sorted_by_severity()[:report_limit]

    # Optional AI summarization
    openai_client = OpenAIClient(model=config.openai_model, enabled=config.openai_enabled)
    ai_summary = openai_client.summarize(report.issues)

    if args.json:
        print(report.to_json(ai_summary))
    else:
        print(report.summary())
        if ai_summary:
            print("\nAI summary:\n" + ai_summary)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
