# Ox Alpha assignment: all-profile source discovery v1

## Provenance and operating boundary

- Assignment ID: `ox-source-discovery-v1`
- Required model: `stealth/ox-alpha`
- Required provider: OpenRouter through Ori/OpenCode
- Intended use: research leads and evidence routing only
- Repository mode: read-only; do not edit, create, delete, or commit files
- Data boundary: public metadata and public web pages only; do not retrieve
  private, hacked, leaked, sealed, paywalled, authenticated, or personal data
- Evaluation boundary: do not inspect B2, Tier C, hidden answers, or raw model
  outputs
- Authority boundary: do not mark any source `training_approved`; rights
  recommendations are provisional evidence for Codex review

## Task

Research these eleven source profiles:

1. Patrick Collison
2. Paul Graham
3. Sam Altman
4. Joel Spolsky
5. Fred Wilson
6. David Heinemeier Hansson
7. Jason Fried
8. Simon Willison
9. Cory Doctorow
10. Jeff Bezos
11. Andy Jassy

For every person, identify up to three strong author-controlled, employer-
controlled, court/government, or otherwise canonical public source collections
that could support abstract writing-characteristic research. Prefer official
archives, personal sites, company communication archives, canonical feeds,
court dockets, and government repositories. Secondary sources may be listed
only as discovery leads and may not support the final evidence fields.

For every source collection, report the canonical URL, publisher/controller,
source type, available genres, approximate availability proxy (document count,
date range, archive pages, or `unknown`), primary rights/terms/license URL when
one exists, and the exact narrow fact that the primary page establishes. Do not
copy article or email bodies and do not quote more than 20 words from any page.

Also report for each person:

- whether a verified authored public-email collection was found;
- the strongest official email lead, if any;
- whether the known default standalone threshold (50,000 effective clean
  tokens, 100 independent examples, three genres, 30 held-out cases) appears
  plausibly reachable, clearly unreachable, or unknown before collection;
- a conservative provisional rights recommendation chosen only from
  `permission_required`, `evaluation_only`, `private_research_only`, or
  `excluded`;
- unresolved authorship, licensing, access, or genre limitations;
- two to five abstract, non-identity writing traits suggested for later human
  verification, with the supporting source IDs and no distinctive phrases.

## Required output

Return exactly one JSON object, with no Markdown fence or commentary:

```json
{
  "version": 1,
  "assignment_id": "ox-source-discovery-v1",
  "generated_at": "RFC3339 UTC date-time",
  "people": [
    {
      "person": "exact requested name",
      "source_collections": [
        {
          "source_id": "stable-kebab-id",
          "title": "collection title",
          "canonical_url": "https URL",
          "controller": "publisher or repository owner",
          "source_type": "official_personal|official_company|court|government|secondary_lead",
          "genres": ["genre"],
          "availability_proxy": "bounded factual description or unknown",
          "rights_or_terms_url": "https URL or null",
          "primary_evidence_fact": "one narrow paraphrased fact",
          "primary": true
        }
      ],
      "public_email": {
        "verified_collection_found": false,
        "strongest_lead_url": null,
        "finding": "concise evidence-backed statement"
      },
      "standalone_threshold_outlook": "plausibly_reachable|clearly_unreachable|unknown",
      "provisional_rights_recommendation": "permission_required|evaluation_only|private_research_only|excluded",
      "abstract_trait_hypotheses": [
        {"trait": "abstract trait", "supporting_source_ids": ["source-id"]}
      ],
      "limitations": ["specific limitation"]
    }
  ],
  "cross_profile_findings": ["finding"],
  "primary_source_failures": ["query or claim that could not be verified"],
  "sources_consulted": [
    {"url": "https URL", "retrieved_at": "RFC3339 UTC date-time", "primary": true}
  ]
}
```

Include every requested person exactly once and keep the result below 30,000
words. If a primary claim cannot be verified, put it in
`primary_source_failures` instead of guessing. Do not make a final architecture,
legal, training-approval, or production decision.
