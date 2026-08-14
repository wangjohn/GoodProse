# Data directory

This directory distinguishes source material from actual model-training examples.

## `raw/`

Exact copies of upstream technical specifications at the revisions pinned in [`sources.json`](sources.json). These files are fetched with `make corpus`, checksum-verified, and committed so a dataset build can be reproduced even if an upstream branch changes.

Do not edit raw files. Change a source revision or selection in `sources.json`, update its checksum, and run the fetcher. Each source's license is stored beside its documents.

The manifest assigns one of four roles:

- `train_reference`: may be used by humans to learn the desired qualities and to build paired examples.
- `dev_eval`: public holdout for developing prompts and the rubric; never fit on it.
- `test_eval`: protected source-family holdout; never fit or tune prompts on it.
- `candidate`: metadata only until its review gate is cleared.

## `derived/`

Generated, provider-neutral JSONL records conforming to [`schemas/training-example.schema.json`](schemas/training-example.schema.json). The directory is ignored except for its README because real agent transcripts may contain proprietary code, credentials, personal data, or other material that must be reviewed before publication.

Raw RFC text is not a training example. The intended pair is:

```text
user request + relevant context + coding-agent output  ->  human-approved technical spec
```

Every derived record should identify its creation method, lineage group, source documents, license information, and reviewer status.

## Before adding a source

1. Confirm that the document is technically strong and that its acceptance/implementation state is known.
2. Record an immutable commit, exact path, checksum, license identifier, and selection rationale.
3. Decide whether it belongs to training references, public development evals, or a source-family test holdout before reading it into any generation pipeline.
4. Group related RFC versions, issues, PRs, and implementations under one lineage so they cannot cross splits.
5. Run `make validate`.
