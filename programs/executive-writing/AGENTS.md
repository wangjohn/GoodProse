# Executive-Writing Program Rules

Read `docs/goals/executive-writing-model.md` before beginning program work.

Keep program-specific configurations, source manifests, experiment records,
and reports inside this directory. Use the dedicated code, data, evaluation,
and test namespaces documented in this directory's README.

Do not put reusable Python implementation directly under `programs/`; place it
under `src/goodprose/executive_writing/` with deterministic tests. Do not change
shared GoodProse infrastructure merely for organizational convenience. When a
shared contract must change, explain the dependency and commit it separately
from program-specific experiments.

Never commit credentials, private source material, unsanitized email, hidden
evaluation answers, model weights, checkpoints, or provider caches. Record
artifact paths, immutable identifiers, hashes, configurations, and retrieval
instructions instead.

Every experiment must identify the hypothesis, candidate and baseline IDs,
dataset and evaluation versions, prompt and decoding configuration, code
revision, hardware/provider, cost, results, and disposition.
