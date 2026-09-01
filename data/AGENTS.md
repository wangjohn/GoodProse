# Data Rules

- Supervised outputs must be exact text written by the repository owner.
- Preserve the URL, publication date, and source path for every imported post when available.
- Do not silently rewrite imported posts. Re-import them from the source export.
- Mark each input as an original outline, original draft, or reviewed derived brief.
- Assign splits before fine-tuning and never move examples to improve a score.
- Every section or variant from one post uses the same `lineage_id` and split.
- Keep unpublished, confidential, or unreviewed material under ignored `data/private/`.
