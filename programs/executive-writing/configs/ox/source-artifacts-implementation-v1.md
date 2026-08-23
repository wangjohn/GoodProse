# Ox Alpha assignment: named-source artifacts implementation v1

## Provenance and boundaries

- Assignment ID: `ox-source-artifacts-implementation-v1`
- Required model: `stealth/ox-alpha`
- Required provider: OpenRouter through Ori/OpenCode
- Intended use: implementation draft for Codex review
- Repository scope: only the executive-writing namespaces listed below
- Data boundary: public metadata only; do not fetch or store corpus bodies
- Evaluation boundary: do not inspect B2, Tier C, hidden answers, grader
  rubrics, private material, or raw model outputs
- Authority boundary: do not mark any source `training_approved`
- Git boundary: do not commit, push, rewrite history, or change branches

## Codex corrections to the preceding discovery result

Use the preceding `ox-source-discovery-v1` response as research leads, with
these binding corrections:

1. Retain only source collections whose canonical routing or authorship was
   independently supported by an official page:
   - Patrick Collison: `https://patrickcollison.com/`
   - Paul Graham: `https://paulgraham.com/articles.html`
   - Sam Altman: `https://blog.samaltman.com/`
   - Joel Spolsky: `https://www.joelonsoftware.com/archives/`
   - Fred Wilson: `https://avc.com/`
   - David Heinemeier Hansson: `https://dhh.dk/` and its official routing to
     `https://world.hey.com/dhh`
   - Jason Fried: `https://37signals.com/thoughts/`, explicitly marked as a
     collective founder archive with individual-attribution limitations
   - Simon Willison: `https://simonwillison.net/`
   - Cory Doctorow: `https://pluralistic.net/` with terms at
     `https://chinwag.pluralistic.net/tos`
   - Jeff Bezos and Andy Jassy: the author-signed annual letters routed by
     `https://ir.aboutamazon.com/annual-reports-proxies-and-shareholder-letters/default.aspx`
2. Exclude Stripe and OpenAI newsrooms, YC Library, the Rails weblog, About
   Amazon news, and SEC routing from evidentiary source collections because
   individual authorship or direct retrieval was not sufficiently verified.
3. Record that no verified authored public-email collection was found for any
   profile. Do not invent email, litigation, docket, or exhibit metadata.
4. Default every voluntarily published source to `permission_required`.
   Pluralistic may be `evaluation_only` because its official terms state CC BY
   4.0 for site text while excluding quotations and images. Nothing may be
   `training_approved`.
5. Use `unknown` for Jason Fried's standalone-threshold outlook because the
   verified archive is collective. Jeff Bezos and Andy Jassy are
   `clearly_unreachable`. Keep conservative, evidence-bounded outlooks for the
   remaining profiles.
6. The model-supplied `generated_at` in the discovery JSON predates the actual
   session start and must not be trusted. Use OpenCode session timestamps only
   in the experiment record.

## Required implementation

Implement a small, deterministic, typed source-artifact system. Prefer
Pydantic at the JSON boundary and pure validation functions. Do not add a new
dependency.

Allowed implementation paths:

- `src/goodprose/executive_writing/sources.py`
- `tests/executive_writing/test_sources.py`
- `data/executive-writing/sources/named-sources-v1.json`
- `data/executive-writing/sources/README.md`
- `evals/executive-writing/source-profiles-v1/manifest.json`
- `evals/executive-writing/source-profiles-v1/README.md`
- `programs/executive-writing/configs/source-profiles/*.json`

The machine-readable source manifest must contain every requested person
exactly once and, for each person, contain all of these explicit objects:

- source audit and evidence routes;
- data-availability report evaluated against the frozen default threshold of
  50,000 effective clean training-approved tokens, 100 independent examples,
  three relevant genres, and 30 independent held-out cases;
- provisional rights assessment, approved uses, evidence URL, reviewer role,
  review date, unresolved questions, and promotion authority;
- abstract, non-identity profile specification with a descriptive production
  profile ID/name, two to five testable traits, and anti-impersonation limits;
- content-controlled evaluation subset referencing a common set of six
  project-authored B1 case IDs, plus topic-swap, leave-topic-out, and
  leave-time-out protocol declarations or explicit current limitations;
- source-specific run configuration.

Choose the same six existing B1 case IDs for every profile so comparisons are
content-controlled. Cover multiple task families and topics. Do not copy case
contents into the new manifest.

Every source-specific run config must:

- be a separate JSON file under the allowed config directory;
- select the profile-card/retrieval coverage architecture, not a standalone
  adapter;
- set standalone eligibility to false;
- state the exact rights and/or statistical blocker;
- use no third-party text for training;
- reference the common evaluation slice and source manifest version;
- label the run as exploratory research, not impersonation or endorsement.

The Pydantic boundary and tests must reject:

- missing or duplicate requested people;
- duplicate source, profile, evaluation-slice, or run-config IDs;
- any `training_approved` classification;
- source evidence that lacks an HTTPS canonical URL;
- a rights record without promotion authority or reviewer metadata;
- a profile that uses the person's identity as its production-facing name;
- a run marked standalone-eligible while any threshold component is unmet or
  rights are not training-approved;
- any profile without exactly six unique evaluation case IDs;
- any config that references unknown manifest/profile/evaluation IDs;
- source bodies, copied passages, or distinctive phrases in metadata fields.

Add a loader and repository-layout validator that can validate the committed
manifest, evaluation manifest, and eleven configs together. Keep CLI changes
out of scope unless required to reuse an existing convention.

## Validation and response

Run only:

```text
uv run pytest tests/executive_writing/test_sources.py
uv run ruff check src/goodprose/executive_writing/sources.py tests/executive_writing/test_sources.py
uv run ruff format --check src/goodprose/executive_writing/sources.py tests/executive_writing/test_sources.py
uv run pyright src/goodprose/executive_writing/sources.py tests/executive_writing/test_sources.py
git diff --check
```

Return a concise summary of files changed, validation results, assumptions,
and anything Codex must correct. Do not include copied source text.
