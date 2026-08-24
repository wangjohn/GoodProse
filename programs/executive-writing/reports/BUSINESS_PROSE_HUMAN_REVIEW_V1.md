# Business prose human review v1

## Outcome

A private, user-only first review batch is ready. It contains eight finished
business-writing pieces and six before/after revision candidates selected from
the pinned PostHog, Sourcegraph, and Clef histories. The private bodies and
rating sheet remain Git-ignored; this report contains metadata only.

No item is `training_approved`. The packet exists to collect the user's direct
quality judgment before any corpus compilation or model use.

## Review batch

| ID | Type | Title | Source | Review focus |
| --- | --- | --- | --- | --- |
| `style-01` | finished piece | Why does PostHog exist? Mission and strategy | PostHog | mission and company strategy |
| `style-02` | finished piece | PostHog marketing values | PostHog | marketing principles |
| `style-03` | finished piece | Part-time managers and setting context | PostHog | management guidance |
| `style-04` | finished piece | A lightweight annual planning system | PostHog | operating process |
| `style-05` | finished piece | Sourcegraph values | Sourcegraph | company values |
| `style-06` | finished piece | Sourcegraph company strategy | Sourcegraph | company strategy |
| `style-07` | finished piece | Clef product manifesto | Clef | product strategy |
| `style-08` | finished piece | Clef one-on-one guidance | Clef | management guidance |
| `pair-01` | revision pair | Make pricing principles more readable | PostHog | substantial restructuring; verify same intent |
| `pair-02` | revision pair | Edit down a communication policy | PostHog | ambitious compression; known scope-change risk |
| `pair-03` | revision pair | Clarify an executive business review guide | Sourcegraph | customer-facing process wording |
| `pair-04` | revision pair | Tighten status-update instructions | Sourcegraph | grammar and concision |
| `pair-05` | revision pair | Make a strategy rationale more direct | Sourcegraph | direct parallel statements |
| `pair-06` | revision pair | Clarify the purpose of an open company handbook | Clef | concrete motivation and action |

## Human decision rule

Rate finished pieces on overall quality, executive relevance, clarity,
concision, and decision usefulness. A finished piece becomes a keep candidate
only when overall quality and executive relevance are both at least 4/5.

For revision pairs, first decide whether the after version preserves the same
facts, policy, strategy, intended decision, and audience. Reject the pair if
that hard gate fails. A pair becomes a keep candidate only when
`same_intent=yes`, factual change is `none`, and `after_better` is at least
4/5. These thresholds do not grant training approval.

## Controls and next action

The builder checks exact source revisions, origins, clean source worktrees,
license hashes, allowlisted paths, and parent/target revisions. It strips
frontmatter, transport markup, links, URLs, email addresses, and contributor
identity metadata before producing the packet. Generated directories are mode
`0700`, files are mode `0600`, and a post-build privacy scan passed.

The user should fill the private `ratings.csv`. The next checkpoint will
validate those ratings and present only the kept/rejected decision summary;
it will not automatically compile a dataset, train a model, or change any
`training_approved` field.

Build provenance is recorded in
`../experiments/business-prose-human-review-v1-build.json`.
