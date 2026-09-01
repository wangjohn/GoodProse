UV ?= uv

.PHONY: sync test lint format typecheck check

sync:
	$(UV) sync

test:
	$(UV) run pytest

lint:
	$(UV) run ruff check .

format:
	$(UV) run ruff format .

typecheck:
	$(UV) run pyright

check: test lint typecheck
