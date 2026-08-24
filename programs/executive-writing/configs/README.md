# Configurations

Store versioned baseline, training, inference, retrieval, and judge
configurations here. A configuration must use stable candidate, dataset,
benchmark, and prompt identifiers and must not contain credentials or local
machine secrets.

Run [`HARNESS_PREFLIGHT.md`](HARNESS_PREFLIGHT.md) before the first Ox Alpha
assignment and after any relevant harness, model, provider, or authentication
change. Its setup snapshot is informational; runtime verification is required.

`data/business-prose-human-review-v1.json` pins the licensed sources, selected
documents, revision candidates, and extraction boundaries for the private,
user-only first business-prose review packet. It contains provenance metadata,
not corpus bodies, and does not grant training approval.
