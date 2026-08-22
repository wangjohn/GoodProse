# Executive-writing model program

This directory is the control plane for GoodProse's long-running model research
program. The durable objective and completion contract live in
[`../../docs/goals/executive-writing-model.md`](../../docs/goals/executive-writing-model.md).
Start it with the concise command in
[`../../docs/goals/launch-executive-writing-model.md`](../../docs/goals/launch-executive-writing-model.md)
after reviewing the contract and the harness preflight.

## Ownership boundary

Program-specific work belongs in these namespaces:

| Concern | Owned path |
| --- | --- |
| Plans, configs, manifests, experiments, reports | `programs/executive-writing/` |
| Training, evaluation, retrieval, and inference code | `src/goodprose/executive_writing/` |
| Unit and integration tests | `tests/executive_writing/` |
| Public data metadata and profile specifications | `data/executive-writing/` |
| Development, sealed, and human eval definitions | `evals/executive-writing/` |

The modules directly under `src/goodprose/`, the provider-neutral schemas under
`data/schemas/`, and the Argilla workflow are shared infrastructure. Modify them
only for a demonstrated cross-cutting requirement and keep the change in a
separate coherent commit.

## Directory map

- `configs/`: versioned baseline, training, inference, and judge configurations.
- `manifests/`: source-audit, rights, profile, and model-candidate manifests.
- `experiments/`: committed hypotheses, run manifests, compact metrics, and
  decisions. Large run artifacts and checkpoints are ignored.
- `reports/`: human-readable phase-gate and finalist reports.

Every committed result must be reproducible from a configuration and immutable
manifest. Generated weights, private inputs, credentials, and raw provider
responses do not belong in Git.
