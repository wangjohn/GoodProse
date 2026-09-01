# Repository Guide

## Purpose

GoodProse builds a small supervised fine-tuning dataset from the owner's blog writing.
The only supported transformation is:

```text
rough draft, outline, or factual brief -> finished blog post
```

Do not expand the project to other authors, channels, or model-research programs without an
explicit user request.

## Python

- Use Python 3.12+ and `uv`.
- Use type hints for non-trivial functions.
- Prefer Pydantic models at file and command boundaries.
- Keep transformations deterministic and implementation direct.
- Do not add a dependency when the standard library or an existing dependency is sufficient.

## Data

- Every supervised target must be the user's own unchanged writing.
- Inputs may be authentic drafts/outlines or reviewed derived briefs; record which.
- Split by blog post lineage. Related posts and sections must not cross splits.
- Never use a test target to construct a training input.
- Canonical inputs are hand-reviewed. Generated SFT files are derived artifacts.
- Follow `data/AGENTS.md` and `evals/AGENTS.md` in those directories.

## Commands

- Install: `uv sync`
- Test: `uv run pytest`
- Lint: `uv run ruff check .`
- Format: `uv run ruff format .`
- Typecheck: `uv run pyright`
- Full check: `make check`

Run the full check before completing code changes.
