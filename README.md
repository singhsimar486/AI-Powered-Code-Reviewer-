# AI-Powered Code Reviewer

This repository provides a prototype of an AI-assisted static analysis tool that combines traditional linters with AST-based rules and optional OpenAI-backed summarization.

## Features
- **Traditional linters**: Runs `flake8` and `bandit` (configurable) to surface style and security concerns.
- **AST rules**: Detects Python-specific logic issues like mutable default arguments, bare `except` blocks, and lingering `print` statements.
- **AI summarization**: Optionally summarizes findings using the OpenAI API for concise reviewer-ready feedback.
- **GitHub Actions integration**: Workflow posts JSON reports on pull requests and attaches a sticky comment.
- **Configuration**: `.ai-reviewer.yml` lets you toggle features, set limits, and pick models.
- **Plugin-friendly**: Clean plugin interface to extend language coverage over time.

## Getting started
1. Install dependencies:

   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. Run the reviewer locally (defaults to current directory):

   ```bash
   python -m ai_reviewer.cli
   ```

3. Enable AI summaries by setting `openai.enabled: true` in `.ai-reviewer.yml` and exporting `OPENAI_API_KEY`.

4. To see JSON output (used by CI):

   ```bash
   python -m ai_reviewer.cli --json > review.json

   The JSON payload includes sorted `issues` and, when OpenAI is enabled, an `ai_summary` field.
   ```

## GitHub Actions
The workflow in `.github/workflows/ai-reviewer.yml` installs dependencies, runs the reviewer on pull requests, uploads a `review.json` artifact, and posts a sticky comment with the findings. Add your `OPENAI_API_KEY` as a repository secret to enable AI summaries.

## Configuration
`.ai-reviewer.yml` controls defaults such as enabled linters, AST checks, OpenAI model, and issue limits. The file included here is a sensible starting point for Python projects.

## Extensibility
Add new plugins under `ai_reviewer/plugins/` implementing the `Plugin` protocol to support other languages or heuristics while keeping the core reporting pipeline unchanged.
