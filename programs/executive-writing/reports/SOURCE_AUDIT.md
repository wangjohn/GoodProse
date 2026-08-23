# Named-source audit

All eleven required research sources now have a versioned source audit,
data-availability assessment, provisional rights record, abstract descriptive
profile, common content-controlled evaluation slice, and source-specific run
configuration. No source has been approved for training and no source body is
committed.

The frozen standalone threshold remains 50,000 effective clean
training-approved tokens, 100 independent examples, three relevant genres,
and 30 independent held-out cases. Every standalone adapter is currently
blocked: nine sources lack training approval and have unmeasured statistical
sufficiency; Jeff Bezos and Andy Jassy are also clearly statistically
insufficient. The eleven lower-cost configs therefore use source-text-free
profile-card coverage on the same six project-authored B1 cases.

| Research source | Verified primary route | Descriptive profile | Threshold outlook | Provisional rights | Standalone status |
| --- | --- | --- | --- | --- | --- |
| Patrick Collison | `patrickcollison.com` | Concise Curated Brief | Unknown | `permission_required` | Blocked by rights and unmeasured volume |
| Paul Graham | `paulgraham.com/articles.html` | Conversational Essay Memo | Plausibly reachable | `permission_required` | Blocked by rights; statistics unmeasured |
| Sam Altman | `blog.samaltman.com` | Declarative Trajectory Update | Unknown | `permission_required` | Blocked by rights and possible insufficiency |
| Joel Spolsky | `joelonsoftware.com/archives` | Narrative Anecdote Advisory | Plausibly reachable | `permission_required` | Blocked by rights; statistics unmeasured |
| Fred Wilson | `avc.com` | Daily Cadence Note | Plausibly reachable | `permission_required` | Blocked by rights; statistics unmeasured |
| David Heinemeier Hansson | `dhh.dk` → `world.hey.com/dhh` | Polemical Product Philosophy Note | Plausibly reachable | `permission_required` | Blocked by rights; statistics unmeasured |
| Jason Fried | `37signals.com/thoughts` | Principle-Driven Manifesto Memo | Unknown | `permission_required` | Blocked by rights and collective attribution |
| Simon Willison | `simonwillison.net` | Technical Link Commentary | Plausibly reachable | `permission_required` | Blocked by rights; statistics unmeasured |
| Cory Doctorow | `pluralistic.net` and official terms | Policy Polemical Analysis | Plausibly reachable | `evaluation_only` | Blocked from training pending user/counsel promotion |
| Jeff Bezos | Amazon investor-relations shareholder-letter archive | Institutional Narrative Letter | Clearly unreachable | `permission_required` | Blocked by rights and all four statistical components |
| Andy Jassy | Amazon investor-relations shareholder-letter archive | Operational Executive Update | Clearly unreachable | `permission_required` | Blocked by rights and all four statistical components |

## Rights boundary

`permission_required` authorizes only public-source metadata audit and abstract
profile-card evaluation without source text. It does not authorize collection,
training, redistribution, or source-text evaluation. Pluralistic is recorded
as `evaluation_only` because its official terms apply CC BY 4.0 to site text
while excluding quotations and images; this remains deliberately below
`training_approved` because only the user or qualified counsel may promote it.

No verified authored public-email collection was found for any of the eleven
profiles. No court exhibit, government-investigation email, leaked material,
or unverified correspondence is included. The bounded public-email workstream
therefore closes at metadata-only negative findings for v1 and can reopen only
for a strong official lead.

## Evaluation and run coverage

Each profile references the same six project-authored B1 cases across email,
memo, decision, revision, strategy, and blog tasks. This defines a neutral
content-controlled comparison. Topic-swap variants and leave-time-out cases
remain explicit limitations; leave-topic-out reporting is declared. The
profile-card runs are configured but not yet executed, so this audit establishes
reproducible coverage definitions rather than model-quality evidence.

Machine artifacts:

- `data/executive-writing/sources/named-sources-v1.json`
- `evals/executive-writing/source-profiles-v1/manifest.json`
- `programs/executive-writing/configs/source-profiles/`
- `programs/executive-writing/experiments/ox-source-discovery-v1.json`
- `programs/executive-writing/experiments/ox-source-artifacts-implementation-v1.json`

Ox Alpha supplied public research leads and a mechanical implementation draft
at $0. Codex independently verified canonical routes, removed unsupported or
weakly attributed claims, narrowed approved uses, strengthened cross-artifact
validation, and owns the final provisional classifications. Ox output is not
training data, evaluation evidence, legal advice, or a production decision.
