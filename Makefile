UV ?= uv

.PHONY: sync sync-tools corpus validate test lint format typecheck check argilla-init argilla-up argilla-down

sync:
	$(UV) sync

sync-tools:
	$(UV) sync --extra privacy --extra tokenizers

corpus:
	$(UV) run python scripts/fetch_corpus.py

validate:
	$(UV) run python scripts/validate_corpus.py

test:
	$(UV) run pytest

lint:
	$(UV) run ruff check .

format:
	$(UV) run ruff format .

typecheck:
	$(UV) run pyright

check: validate test lint typecheck

argilla-init:
	@test -f infra/argilla/.env || $(UV) run goodprose annotation init-env

argilla-up: argilla-init
	docker compose --env-file infra/argilla/.env -f infra/argilla/docker-compose.yml up -d

argilla-down:
	docker compose --env-file infra/argilla/.env -f infra/argilla/docker-compose.yml down
