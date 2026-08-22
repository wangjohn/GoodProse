# GoodProse dataset strategy

## Learn the transformation, not a corpus continuation

The target behavior is:

```text
source material + audience + channel + objective + constraints + voice profile
    -> faithful, effective executive communication
```

Standalone finished essays mostly teach continuation and surface style. They do not reliably teach fact selection, uncertainty preservation, audience adaptation, or the conversion of rough thinking into a useful artifact. Prioritize paired revisions.

## Collection priority

Build examples in this order:

1. Real rough notes or drafts paired with their final executive-approved artifact.
2. Revision history that shows a rejected draft and the accepted replacement.
3. One factual source intentionally adapted into two or more channels.
4. Human-created degradations of approved outputs for controlled experiments.
5. Synthetic degradations only as a minority supplement.

The first useful milestone is approximately 50 deeply reviewed pairs across all three channels. Expand only after a fixed eval shows that the additional data improves a meaningful metric.

## Explicit conditioning

Every input records:

- `source_material`: the facts, notes, or draft to transform;
- `channel`: `email`, `internal_memo`, or `blog_post`;
- `audience`: the intended readers and their assumed context;
- `objective`: what the communication must achieve;
- `constraints`: length, confidentiality, commitments, required calls to action, or exclusions;
- `voice_profile_id`: a versioned original voice definition;
- optional supporting context such as policy, evidence, or reference material.

Do not collapse channel and audience into style. The same house voice should behave differently in a short leadership email and a public essay.

## Provenance and rights

Preserve source IDs, revisions, URLs, licenses or permissions, creation method, and lineage. Public availability does not by itself grant the right to redistribute a corpus or trained weights. Prefer company-owned or explicitly permissioned examples.

Use named writers only as research inspiration for abstract traits. Do not label training behavior as imitation, copy distinctive phrases, or make named-person resemblance the product objective.

## Splitting

Split by communication lineage, not individual files. Rough notes, intermediate drafts, the final email, follow-up memo, and derived variants from one event must stay together. When possible, create holdouts by topic, executive, organization, and time so the model cannot win through near-duplicate phrasing.

Keep three evaluation layers:

1. Public development cases for deterministic harness work.
2. Private, human-reviewed cases for prompt and model comparison.
3. A sealed final holdout that is not used for prompt iteration, judge calibration, or synthetic generation.

## Baseline before fine-tuning

Run every case through a strong prompted baseline with the same voice profile and a few approved examples. Record editing effort and pairwise human preference in addition to rubric scores. Fine-tune only if the dataset produces a repeatable improvement over that baseline.

## Useful dataset reports

For every snapshot, retain:

- examples and tokens by channel, audience class, and creation method;
- source and style-reference composition;
- lineage and split counts;
- privacy-report hash and dataset hash;
- duplicate and near-duplicate findings;
- voice-profile version;
- reviewer coverage and rejection reasons.
