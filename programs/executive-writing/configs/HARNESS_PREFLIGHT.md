# Ori, OpenCode, and Ox Alpha capability gate

Run this gate before the first Ox Alpha assignment and whenever Ori, OpenCode,
the model identifier, authentication, or provider behavior changes. This gate
authorizes validation only; it does not authorize paid usage.

## Recorded setup snapshot

Observed on 2026-08-22 in `/Users/wangjohn/GoodProse`:

- Ori resolves to `/Users/wangjohn/.local/bin/ori`.
- Ori reports `0.8.0+3511459`; it also reports that `0.9.0+4eff9d5` is
  available. Do not upgrade merely because an update exists.
- `ori opencode --help` exposes OpenRouter model and reasoning flags.
- `opencode` does not currently resolve on `PATH`. Ori's wrapper help is not
  proof that the downstream OpenCode executable is installed or runnable.
- The OpenRouter Models API reported `stealth/ox-alpha` as Ox Alpha with zero
  prompt and completion prices and a 1,048,576-token context window at the
  time of inspection. Reverify every field at runtime; model inventory,
  capabilities, limits, and prices can change.
- Settled and approved spend for this gate is $0.

This snapshot is evidence for where to begin, not permission to skip a check.

## Required gate

1. Record the repository revision and confirm the worktree state.
2. Resolve and record the Ori path and version.
3. Resolve and record the official OpenCode path and version. If it is absent,
   install an Ori-compatible release only from OpenCode's official source,
   record the installation source and resolved version, and do not change Ori
   at the same time.
4. Query `https://openrouter.ai/api/v1/models` without printing authentication
   data. Resolve Ox Alpha by current model metadata rather than a guessed alias.
5. Record the exact model ID, provider, context length, supported parameters,
   and every applicable pricing field. Zero prompt and completion prices alone
   are insufficient if request, image, tool, or other charges apply.
6. Configure Ori/OpenCode explicitly with the resolved model ID. Never accept a
   silent fallback or router-selected substitute.
7. Run a read-only smoke task that asks the harness to inspect a harmless
   repository file, report one fact, and identify the tool used. Confirm that:
   - output metadata names the exact Ox Alpha model and OpenRouter;
   - at least one repository-read tool call succeeded;
   - no file, git, network, credential, or external state was changed; and
   - the task terminates within a bounded time.
8. Run the artifact-contract task below and validate all required fields.
9. Save only sanitized versions, hashes, timestamps, results, and failure
   reasons in the experiment record. Never save tokens or raw auth output.

## Artifact-contract task

Give Ox Alpha a small sanitized input and require a machine-readable response
with these fields:

```json
{
  "assignment_id": "preflight-artifact-contract-v1",
  "model_id": "exact runtime model identifier",
  "provider": "openrouter",
  "prompt_hash": "sha256",
  "input_classification": "sanitized_public",
  "intended_use": "harness_validation_only",
  "findings": [],
  "sources": [],
  "validation_performed": [],
  "uncertainties": [],
  "timestamp": "RFC 3339"
}
```

Reject the response if required fields are missing, the reported model differs
from the configured model, provenance is ambiguous, or free text appears
outside the expected envelope when strict JSON was requested.

## Failure and change policy

- Allow one bounded retry for a transient rate limit, timeout, or provider
  outage. Then record the failure and have Codex perform the assignment.
- If the model is absent, no longer free, or pricing is ambiguous, do not call
  it until the contract's budget approval process is complete. Codex continues
  directly in the meantime.
- Do not auto-upgrade Ori or OpenCode during an experiment. Upgrade only for a
  recorded compatibility or security reason, pin the resulting versions, and
  rerun this entire gate.
- A failed gate disables delegation; it never pauses the GoodProse goal while
  safe direct work remains.
