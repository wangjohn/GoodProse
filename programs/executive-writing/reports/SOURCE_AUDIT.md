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
profile-card matrix completed at revision `c472575` with exactly 72 local calls,
retrieval disabled, no third-party source text, and $0 settled cost. The table
below is exploratory coverage on six visible cases, not model-quality or
standalone-adapter evidence.

| Descriptive profile | Mean score | Hard gates | Paired mean vs house |
| --- | ---: | ---: | ---: |
| Concise Curated Brief | 79.7846 | 16.67% | -5.5535 |
| Conversational Essay Memo | 90.9160 | 33.33% | +5.5779 |
| Declarative Trajectory Update | 85.5653 | 16.67% | +0.2272 |
| Narrative Anecdote Advisory | 80.1660 | 33.33% | -5.1721 |
| Daily Cadence Note | 84.6350 | 0.00% | -0.7031 |
| Polemical Product Philosophy Note | 81.4635 | 16.67% | -3.8746 |
| Principle-Driven Manifesto Memo | 76.7911 | 16.67% | -8.5470 |
| Technical Link Commentary | 93.5057 | 66.67% | +8.1677 |
| Policy Polemical Analysis | 90.2607 | 50.00% | +4.9226 |
| Institutional Narrative Letter | 89.1630 | 33.33% | +3.8249 |
| Operational Executive Update | 88.0631 | 16.67% | +2.7250 |

The house-profile control scored 85.3381 with 33.33% hard gates. All eleven
profiles remain in the program regardless of these estimates. The independent
publisher rebuilt every prompt, verified prompt/output/artifact hashes,
rescored every output under v1.1, and emitted no raw generated text.

Machine artifacts:

- `data/executive-writing/sources/named-sources-v1.json`
- `evals/executive-writing/source-profiles-v1/manifest.json`
- `programs/executive-writing/configs/source-profiles/`
- `programs/executive-writing/experiments/ox-source-discovery-v1.json`
- `programs/executive-writing/experiments/ox-source-artifacts-implementation-v1.json`
- `programs/executive-writing/experiments/ox-profile-coverage-runner-v1.json`
- `programs/executive-writing/experiments/source-profile-coverage-v1-results.json`
- `programs/executive-writing/experiments/source-profile-coverage-v1-case-results.json`

Ox Alpha supplied public research leads and a mechanical implementation draft
at $0. Codex independently verified canonical routes, removed unsupported or
weakly attributed claims, narrowed approved uses, strengthened cross-artifact
validation, and owns the final provisional classifications. Ox output is not
training data, evaluation evidence, legal advice, or a production decision.
