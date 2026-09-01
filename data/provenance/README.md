# Provenance inventory

`inventory.jsonl` records whether an authentic authoring history and its required context have
been found for every imported post. It deliberately contains no raw conversation text.

Unreviewed prompt extracts and absolute source locations live in
`data/private/provenance/history_candidates.jsonl`. That directory is ignored because authoring
histories may contain unpublished context. A candidate must be reviewed before it becomes a
canonical SFT input.

`not_found` means that no match appeared in the accessible Codex task logs or recent ChatGPT task
listing. It does not prove that an older conversation does not exist.
