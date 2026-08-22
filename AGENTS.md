# Repository Guide

## Purpose

This project builds provenance-aware data and evaluations for models that turn rough source material into clear executive emails, internal memos, and blog posts.

## Python

- Use Python 3.12+.
- Use `uv` for dependency management and command execution.
- Use type hints for all non-trivial functions.
- Prefer Pydantic models at system boundaries.
- Prefer small pure functions for data transformations.
- Do not introduce abstractions unless they simplify an existing concrete use case.

## Commands

- Install/sync: `uv sync`
- Tests: `uv run pytest`
- Lint: `uv run ruff check .`
- Format: `uv run ruff format .`
- Typecheck: `uv run pyright`

Before completing a code change, run the relevant tests plus lint/typecheck.

## Testing

- Tests must be deterministic.
- Never make live LLM API calls in unit tests.
- Record or mock model responses for unit tests.
- Behavioral/model evals belong under `evals/`, not `tests/`.
- Every bug fix should include a regression test when practical.

## Data

- Never silently mutate raw data.
- Every derived dataset must be reproducible from code.
- Preserve source/provenance metadata.
- Never move an example between train and eval simply to improve a metric.
- Keep training and evaluation data isolated.
- See `data/AGENTS.md` for dataset-specific rules.

## Evals

- Treat eval results as experiments: record model, model version,
  prompt/config, dataset version, grader version, and code revision.
- Prefer deterministic checks over LLM judges where possible.
- Never expose reference answers or grader rubrics to the model under evaluation.
- Do not change an eval and compare its score directly with historical runs
  without explicitly marking the eval version change.
- See `evals/AGENTS.md`.

## Dependencies

Prefer a small dependency set. Before adding a framework, determine whether
the required behavior can be implemented with the standard library or an
existing dependency.
