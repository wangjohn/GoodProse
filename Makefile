PYTHON ?= python3

.PHONY: corpus validate

corpus:
	$(PYTHON) scripts/fetch_corpus.py

validate:
	$(PYTHON) scripts/validate_corpus.py
