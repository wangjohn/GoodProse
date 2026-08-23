# Batched data-rights decision packet

## Decision requested

No named-source corpus is approved for training. The conservative default is
to keep all eleven sources out of training until the user or qualified counsel
records a source-specific decision supported by the evidence below. Public
availability alone is not permission.

This packet asks for decisions in one batch; it does not ask Codex or Ox Alpha
to promote material. Until a decision is returned, source-text-free descriptive
profile cards and project-owned evaluation cases remain the only permitted
coverage path.

The standalone eligibility threshold is fixed independently of rights:
50,000 effective clean approved author tokens, 100 independent examples, at
least three relevant genres or a documented limitation, and 30 independent
content-controlled held-out cases. A rights approval does not waive these
statistical gates.

## Source summary

| Research source | Current class | Availability outlook | Decisive unresolved issue | Evidence route |
| --- | --- | --- | --- | --- |
| Patrick Collison | `permission_required` | unknown | No personal-site license or verified authorship continuity | `https://patrickcollison.com/` |
| Paul Graham | `permission_required` | plausibly reachable | No training or redistribution license; default copyright | `https://paulgraham.com/articles.html` |
| Sam Altman | `permission_required` | unknown | No blog license; company-channel authorship excluded | `https://blog.samaltman.com/` |
| Joel Spolsky | `permission_required` | plausibly reachable | No visible archive reuse/training license | `https://www.joelonsoftware.com/archives/` |
| Fred Wilson | `permission_required` | plausibly reachable | No license covering model training or redistribution | `https://avc.com/` |
| David Heinemeier Hansson | `permission_required` | plausibly reachable | Hosting terms are not a content-training license; books excluded | `https://world.hey.com/dhh` |
| Jason Fried | `permission_required` | unknown | Collective archive attribution unresolved; books excluded | `https://37signals.com/thoughts/` |
| Simon Willison | `permission_required` | plausibly reachable | No weblog-text training license; many items are too short | `https://simonwillison.net/` |
| Cory Doctorow | `evaluation_only` | plausibly reachable | Site terms state CC BY 4.0 for site text but exclude quotations/images; training and adapter obligations require counsel | `https://chinwag.pluralistic.net/tos` |
| Jeff Bezos | `permission_required` | clearly unreachable | Corporate copyright plus decisive token/example/genre/holdout insufficiency | `https://ir.aboutamazon.com/annual-reports-proxies-and-shareholder-letters/default.aspx` |
| Andy Jassy | `permission_required` | clearly unreachable | Corporate/staff authorship plus decisive statistical insufficiency | `https://ir.aboutamazon.com/annual-reports-proxies-and-shareholder-letters/default.aspx` |

The complete route-level facts, terms URLs, provisional approved uses, review
date, thresholds, and blockers are in
`data/executive-writing/sources/named-sources-v1.json`. The human-readable audit
is `SOURCE_AUDIT.md`. This table paraphrases those records and adds no new
rights claim.

## Counsel/user questions

For any source proposed for training, record all of the following:

1. Exact source route and included document/item IDs.
2. Rights holder and permission or license evidence.
3. Whether collection, local storage, transformation, model training,
   evaluation, adapter/checkpoint storage, internal use, external deployment,
   and redistribution are each allowed.
4. Attribution, notice, share-alike, deletion, geographic, term, or downstream
   model-output obligations.
5. Whether quoted third-party text, images, guest posts, coauthored works,
   corporate/staff-drafted text, book excerpts, and comments must be excluded.
6. Whether individual authorship is sufficiently verified.
7. The approving user/counsel identity, role, date, and scope.

For Cory Doctorow specifically, counsel should determine whether the official
CC BY 4.0 notice covers the exact selected site-text items and permits the
planned training and adapter use, what attribution must accompany datasets or
models, and how excluded quotations/images will be detected. Until then the
source remains `evaluation_only`, not `training_approved`.

For Jeff Bezos and Andy Jassy, a rights answer alone cannot authorize a
standalone run because all four sufficiency components are currently unmet.
For Jason Fried, a decision must also resolve individual versus collective
authorship. For every other source, all four threshold components remain
unverified or the 30-case holdout component is unmet.

## Authentic task-pair decision

The highest-value data decision is not a named-style corpus. It is a rights-
cleared collection of authentic rough-material-to-final executive-writing
pairs. A proposed collection should include:

- source owner, author, provenance, and collection method;
- explicit permission for training and internal model artifacts;
- privacy review and a ban on secrets, personal data, litigation material, and
  raw customer/email dumps unless separately authorized and safely redacted;
- task/genre/audience distribution and independent lineage IDs;
- immutable train/validation/test split before training;
- exclusion from B1, B2, Tier C, and human-evaluation cases;
- exact/fuzzy/n-gram contamination results;
- retention, deletion, and access rules.

Recommended first approval, if available: a small user-contributed or company-
owned corpus with explicit internal training permission and at least enough
independent lineages for a new unified with/without-synthetic ablation. Do not
approve a public named corpus merely to unblock the program.

## Decision form

Return one record per approved corpus using this structure:

```text
Corpus/source:
Exact included routes or item IDs:
Rights classification:
Approved uses:
Required exclusions:
Attribution/notice obligations:
Retention/deletion obligations:
Approver name or role:
Decision date:
Evidence location:
```

An answer of “no named-source training approval” is valid and leaves all
profile cards operational. Any approval will still undergo privacy,
provenance, deduplication, sufficiency, and train/eval isolation checks before a
training config can become eligible.
