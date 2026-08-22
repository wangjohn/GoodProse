# GoodProse Executive-Writing Research Contract

This is the versioned execution and completion contract for
[`launch-executive-writing-model.md`](launch-executive-writing-model.md). Keep
the `/goal` launcher short; make substantive scope, scientific-method, safety,
or stopping-condition changes here and commit them before a run relies on them.

OBJECTIVE

Build GoodProse into a provenance-aware, reproducible system for evaluating,
training, and iteratively improving language models that turn authentic rough
source material into exceptionally clear executive emails, internal memos,
strategy documents, engineering documents, blog posts, and short-form posts.

Work autonomously and persistently in /Users/wangjohn/GoodProse. Do not stop after producing a plan or prototype. Continue through implementation, data preparation, baseline evaluation, real training runs, evaluation, failure analysis, and multiple improvement iterations.

Operate this as one durable objective with gated experimental phases, explicit evidence artifacts, and a verifiable stopping condition. Do not treat it as a loose backlog. The goal is complete only when the repository contains a tested and documented end-to-end system, real benchmark results, reproducible training configurations, at least one genuinely fine-tuned candidate model, source-specific experiment coverage wherever permitted, and a defensible human-confirmed recommendation about the best production architecture. A provisional recommendation is a progress artifact, not completion.

PRIMARY OBJECTIVE

Maximize blinded preference on authentic rough-material-to-executive-writing tasks, subject to hard constraints on source fidelity, factual correctness, privacy, data rights, train/evaluation isolation, concision without information loss, deployment practicality, and the approved project budget.

The production objective is excellent business-writing behavior, not identity imitation. Style resemblance is a secondary research diagnostic. Do not reward a model merely for using recognizable phrases, discussing topics associated with a named person, or triggering an authorship classifier.

Use this automated development scorecard unless a preregistered GoodProse benchmark version justifies a change before results are observed:

- 35% source fidelity and factual correctness
- 20% clarity and coherence
- 15% concision without loss of necessary information
- 15% organization, decision usefulness, and actionability
- 10% audience, genre, and format control
- 5% controllable abstract writing characteristics

Treat the following as hard gates rather than compensating score components:

- No practically important regression in factual fidelity, unsupported claims, intent preservation, privacy, or safety.
- No rights violation, train/evaluation leakage, or unacceptable memorization.
- The candidate fits the documented latency, memory, inference-cost, and deployment envelope.

The final primary human endpoint is publish-ready acceptance: the proportion of outputs judged `publishable` or requiring only `minor_edits`, together with the complementary `substantive_edits` and `unacceptable` rates. A critical factual error is a veto regardless of writing quality. Blinded pairwise preference is a secondary discriminative endpoint among candidates that pass the hard gates. Automated metrics and LLM judges are development proxies, not substitutes for this human endpoint.

The system must support:

- Executive and internal emails
- Internal memos
- Strategy and decision documents
- Business and engineering documents
- Company updates
- Blog posts
- Tweets, short posts, and threads
- Revision of existing drafts for clarity, coherence, and concision
- Transformation of rough notes, transcripts, bullet points, or source documents into polished writing

Compare this architecture ladder rather than assuming fine-tuning, direct generation, or one adapter per source is best:

1. Strong prompt-only profile cards.
2. Prompting plus retrieval of approved examples.
3. A unified controllable fine-tune that switches among writing profiles, genres, audiences, and levels of formality.
4. Clustered, composable, or low-rank-basis adapters for groups of compatible writing characteristics.
5. Separate source-specific or profile-specific LoRA/adaptor models when the evidence and approved data support them.
6. A structured `plan -> write -> verify/revise` system that extracts a claims and decision ledger, creates an audience-aware outline, renders under the selected profile, verifies every fact, number, attribution, caveat, and action against the ledger, and makes the smallest revision needed to fix failures.
7. A hybrid of retrieval, structured generation, unified training, and adapters.

Compare structured generation directly with single-pass generation so any quality gain is attributable rather than assumed. Choose the final architecture from evaluation evidence. It may be a unified model, separate adapters, structured multi-pass system, or a hybrid.

NAMED RESEARCH SOURCES

Research, create manifests for, and support experiment configurations for:

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

These names describe source corpora and research hypotheses. Do not market the resulting models as replicas, impersonations, or endorsements by these people.

Extract reusable, abstract writing characteristics such as:

- Density and information compression
- Sentence and paragraph structure
- Directness
- Technical precision
- Explanatory depth
- Use of examples
- Epistemic calibration
- Decision orientation
- Actionability
- Warmth or formality
- Narrative structure
- Opening and closing patterns
- Use of questions
- Degree of qualification
- Formatting and information hierarchy

Production-facing profiles should preferably have descriptive names such as “concise founder memo,” “technical explanatory,” or “direct decision email.” Source-specific names may remain in research manifests, training configurations, and evaluation reports.

For every named person, create a source audit, profile specification, data-availability report, provisional rights assessment, content-controlled evaluation subset, and training configuration.

Preserve experiment coverage for all eleven people, but do not force eleven statistically weak production adapters. Before a standalone source-specific run, define and apply a documented sufficiency threshold based on data quality, diversity, task fit, and evaluation power. The default threshold is at least 50,000 effective clean training-approved author tokens after deduplication and boilerplate removal, at least 100 genuinely independent examples, coverage across at least three relevant genres or clearly documented genre limitations, and at least 30 independent content-controlled held-out cases. Raw token volume alone does not satisfy the threshold. Change these defaults only before seeing comparative results and record the rationale.

When a source does not meet the standalone threshold, still run the best scientifically valid low-cost coverage experiment available, such as a conditioned unified-model run, leave-one-source-in or leave-one-source-out ablation, mixture-weight ablation, profile-card baseline, or retrieval baseline. Mark a standalone adapter as blocked by rights or statistical insufficiency rather than manufacturing permission, data, or confidence.

CODEX AND OX ALPHA ORCHESTRATION

Codex is the primary orchestrator and final decision-maker.

Use Ox Alpha through OpenCode, accessed through Ori, for high-volume but bounded work such as:

- Research and source discovery
- Repository exploration
- Dataset and benchmark reconnaissance
- Drafting adapters and ingestion code
- Generating implementation alternatives
- Reviewing experiment failures
- Suggesting new hypotheses
- Writing test candidates
- Documentation drafts
- Repetitive mechanical changes
- Corpus statistics and deduplication
- OCR or extraction tooling on already-sanitized material

The installed Ori binary is:

/Users/wangjohn/.local/bin/ori

The OpenRouter authentication used by Ori is already configured. Do not display, log, copy, or commit credentials.

Before the first Ox Alpha task:

- Inspect `ori --help`, `ori opencode --help`, and relevant OpenCode help.
- Read and execute `programs/executive-writing/configs/HARNESS_PREFLIGHT.md`.
- Verify that the official, Ori-compatible OpenCode executable is installed and record its resolved path and version. Do not infer that `ori opencode --help` proves the downstream harness is installed.
- Query the current OpenRouter Models API and resolve the exact currently available model identifier for Ox Alpha. The verified identifier at contract revision time is `stealth/ox-alpha`, but this is a discovery hint rather than a permanent alias, availability, or pricing guarantee.
- Explicitly configure OpenCode to use Ox Alpha through OpenRouter.
- Do not silently substitute another model.
- Record the Ori and OpenCode versions and run a harmless, read-only repository tool-use smoke task. Verify the selected model, provider, successful tool call, and no file changes in its output or metadata before delegating substantive work.
- Run a small artifact-contract test that checks required output fields and provenance metadata. If either test fails, Codex takes over the work directly and continues the goal.
- Treat Ox Alpha as free only after checking its current prompt, completion, request, and related prices. If any applicable price is nonzero or ambiguous, obtain approval before using the project budget for it.
- Do not auto-upgrade Ori or OpenCode during an active experiment. Upgrade only for a recorded compatibility or security reason, pin the new versions, and rerun both tests before resuming delegation.

Give Ox Alpha concrete, scoped assignments with expected artifacts and validation requirements. Do not delegate the entire project in one vague prompt.

Treat Ox Alpha primarily as a research and implementation worker. Do not use the same Ox Alpha output as unreviewed training data and as its own evaluation evidence. Tag every Ox-generated artifact with the exact model identifier, provider, prompt hash, timestamp, and intended use so it can be isolated and ablated. Ox Alpha must not be the sole teacher, candidate generator, and judge for the same example or experiment.

Codex must:

- Maintain the overall plan and progress log.
- Review all Ox Alpha findings and patches.
- Verify sources and factual claims.
- Collect data-rights and privacy evidence and assign conservative provisional classifications.
- Run tests and evaluations.
- Resolve conflicts and integration failures.
- Own all git commits.
- Decide what technically eligible material enters evaluation datasets and what user- or counsel-approved material enters training datasets.
- Directly implement any work that Ox Alpha cannot reliably complete.

Ox Alpha must not independently:

- Approve data for training.
- See hidden evaluation answers or grader rubrics.
- Receive unredacted litigation documents or personal data.
- Commit secrets, raw email dumps, or model weights.
- Push branches or publish artifacts.
- Make final architecture or model-selection decisions.

Only the user or qualified counsel may promote material to `training_approved`. Codex and Ox Alpha may collect evidence, identify licenses, recommend a classification, and exclude risky material, but neither may convert an unresolved or provisional source to `training_approved`. Existing explicit approvals may be applied exactly as documented. A rights question blocks only the affected source, not other useful work.

Batch rights questions into concise, evidence-backed decision packets after exhausting primary-source research. Do not interrupt the user for source-by-source preliminary questions, and continue every unaffected workstream while a rights decision is pending.

If Ox Alpha returns a rate-limit response, repeated timeout, provider outage, or explicit quota error, make at most one bounded retry. Then Codex must immediately take over the relevant research, coding, or analysis directly. Do not pause the whole goal waiting for Ox Alpha to become available.

The harness capability gate is an optimization gate, not a project gate. Missing OpenCode, changed model identifiers, failed authentication, changed pricing, contract-test failures, or incompatible versions never justify idling the goal when Codex can perform the same safe work directly.

REPOSITORY AND ENGINEERING RULES

Work only within /Users/wangjohn/GoodProse, except for ignored temporary files, local model caches, and external training output directories.

Keep program-specific work inside the repository ownership boundaries:

- Control-plane configs, manifests, experiments, and reports: `programs/executive-writing/`
- Python implementation: `src/goodprose/executive_writing/`
- Tests: `tests/executive_writing/`
- Program data metadata: `data/executive-writing/`
- Program evaluations: `evals/executive-writing/`

Treat the modules directly under `src/goodprose/`, provider-neutral schemas, annotation infrastructure, root build files, and general documentation as shared infrastructure. Modify them only for a demonstrated cross-cutting requirement, explain the dependency, and isolate the shared change in a coherent commit.

Before making changes:

- Read all applicable AGENTS.md files.
- Inspect the current git status and preserve unrelated user changes.
- Inspect the existing repository architecture, dependencies, tests, data conventions, and evaluation structure.
- Record the starting revision.
- Create a scoped working branch using the `codex/` prefix if doing so is safe and does not disrupt existing work.
- Do not push unless explicitly authorized.

Follow the repository requirements:

- Python 3.12+
- `uv` for dependencies and execution
- Type hints for non-trivial functions
- Pydantic at system boundaries
- Small, testable data transformations
- Deterministic unit tests
- No live LLM calls in unit tests
- Behavioral evaluations under `evals/`
- Reproducible derived datasets
- Strict train/evaluation isolation
- Complete provenance metadata
- No unnecessary frameworks or dependencies

Use these checks throughout:

- `uv sync`
- `uv run pytest`
- `uv run ruff check .`
- `uv run ruff format .`
- `uv run pyright`

Run relevant focused checks before each commit and the complete appropriate suite at major milestones.

GATED EXPERIMENTAL PROGRAM

Execute the work in the following phases. Maintain a short phase ledger in `programs/executive-writing/reports/PROGRESS.md` with hypotheses, evidence produced, exit criteria, decisions, next actions, and unresolved risks. Phase gates constrain expensive or validity-sensitive work; they do not require the user to steer routine implementation.

FIRST-EVIDENCE MILESTONE

Produce a complete, inexpensive vertical slice before exhaustive benchmark integration, corpus expansion, or public-email research becomes a critical path:

1. Create 20 to 50 rights-safe, task-aligned search-development cases spanning the highest-value email, memo, document, and revision tasks. Prefer authentic permissioned or project-authored material. Clearly labeled synthetic cases may validate plumbing but cannot establish model quality.
2. Run an untuned baseline, the strongest practical prompt baseline, and a retrieval/example-conditioned baseline on the same cases.
3. Complete one end-to-end smoke fine-tune through dataset compilation, training, inference, evaluation, and run-manifest generation. A small model and a small rights-safe synthetic or project-authored corpus are acceptable for this plumbing test; label the result as a smoke test rather than a quality claim.
4. Publish one shared machine-readable and human-readable results table containing quality, hard-gate, latency, and cost fields.
5. Publish one failure analysis using the registered error taxonomy and select the next hypothesis from evidence.

Begin this milestone in Phase 0 and complete it as early as technical feasibility and rights-safe starter data permit. Work on imported benchmarks, full source audits, and litigation emails in parallel only when it cannot delay this first closed loop. Do not wait for an exhaustive survey to learn whether the training and evaluation plumbing works.

OPERATING CONSTRAINTS

- Keep at most two active research workstreams and one active training run unless the progress ledger records a clear expected-value case for more parallelism.
- Never leave paid compute or storage idle or orphaned. Use automatic shutdowns, bounded jobs, resumable checkpoints, and post-run resource checks.
- Use a two-fidelity selection loop: run deterministic hard gates and a cheap stratified screen for every candidate; run the full development suite only for candidates that pass the screen or for scheduled calibration checks.
- Use successive halving for sweeps. Allocate full-suite evaluation and longer training only to candidates that remain competitive on paired evidence.
- Maintain bounded exploration, but do not keep dominated branches alive solely for symmetry.

Phase 0: feasibility, environment, and rights; target spend $0

- Audit the repository, hardware, model caches, tools, Ori/OpenCode/Ox Alpha access, exact provider pricing, licenses, and source availability. Run the harness capability gate before the first Ox delegation; if it fails, record the reason and continue directly with Codex.
- Establish provisional rights classifications and identify the authority required for promotion to `training_approved`.
- Produce a data-volume and genre-diversity estimate for every profile.
- Start the first-evidence milestone immediately rather than waiting for exhaustive rights and source surveys.
- Exit when the project has a technically feasible local or approved external path, a rights-safe starter corpus, a documented zero-cost work plan, and either a completed first-evidence milestone or a precise external blocker that does not prevent other useful work.
- If fine-tuning is infeasible, continue with prompt, retrieval, evaluation, data, and reproducibility work while documenting the blocker and best alternative.

Phase 1: evaluation validity and baselines; target spend $0 or minimal approved evaluation cost

- Implement the evaluation hierarchy, frozen benchmark schemas, contamination controls, baseline inference, automated development scorecard, and human-evaluation protocol.
- Run untuned, prompt-engineered, and retrieval/example-conditioned baselines.
- Establish a strong accessible frontier-model teacher or quality-ceiling baseline when it is free or covered by an approved budget envelope. Treat it as an upper-bound comparison and potential independent teacher, not automatically as a deployable candidate.
- Characterize evaluator reliability, position sensitivity, verbosity sensitivity, and disagreement on a fixed reference or previously human-labeled calibration set when one is legally available.
- Exit when the first-evidence milestone is complete, there is a reproducible task-aligned development benchmark, a genuinely separated sealed holdout or honestly labeled procedurally held-out set, credible baselines, and enough signal to distinguish meaningful changes.
- Do not request new human ratings merely to pass this phase; prepare the protocol and continue with automated and deterministic evidence.

Phase 2: unified pilot and architecture decision

- Harden the three-corpus training pipeline proven by the first-evidence smoke run.
- Train at least one genuine unified profile-conditioned candidate on the smallest base model that can answer the architectural question credibly.
- Compare prompting, retrieval, direct single-pass generation, structured plan-write-verify/revise generation, unified fine-tuning, and at least one justified adapter or composition strategy.
- Exit when the entire training/evaluation path is reproducible and evidence identifies the most promising model families, data mixtures, and architecture branches.
- Do not spend materially or multiply profile adapters if the unified pilot cannot beat or complement the strongest non-training baseline on the preregistered development criteria.

Phase 3: autonomous optimization and profile coverage

- Concentrate compute and agent effort on the best-performing model families while preserving a bounded exploration allocation for credible challengers.
- Run source-specific adapters only above the documented sufficiency threshold; use lower-cost conditioned or ablation experiments for the remaining profiles.
- Continue until high-value affordable hypotheses are exhausted, the plateau rule is met, the approved budget is exhausted, or the finalist-readiness gate is satisfied.

Phase 4: frozen finalists and human confirmation

- Freeze the strongest diverse set of three to five candidates, including the strongest prompt/retrieval baseline whenever it remains competitive.
- Select the best two or three of those frozen candidates for the human packet using only preregistered automated evidence and diversity constraints.
- Run the sealed automated holdout exactly once for that benchmark version after all candidate, prompt, data, decoding, and selection decisions are frozen.
- Only then request the final blinded human evaluation.
- Human evaluation determines the final production recommendation among hard-gate-passing candidates. Continue autonomous, non-leaking work while ratings are pending as specified below.

EXISTING EVALUATIONS

Research the primary sources, licenses, canonical repositories, schemas, and reference implementations for:

- WritingBench Business
- WritingBench Engineering
- IteraTeR
- EditEval clarity
- EditEval coherence
- Revision for Concision
- YapBench

Pin every imported evaluation to an exact version, commit, release, or dataset revision.

Pin all behavior-affecting components, not only the dataset: task instances, instance-specific criteria, evaluation prompt, judge model and exact version, decoding configuration, metric implementation, and code revision. Audit the license of every underlying component separately; a repository license does not automatically grant the same rights for every bundled dataset.

Do not blindly copy datasets. Create adapters that fit GoodProse’s evaluation structure. If redistribution is not permitted, provide reproducible download/build instructions and keep restricted inputs out of git.

Use the public suites according to their demonstrated scope:

- WritingBench Business and Engineering are broad legacy comparisons with long outputs and model-based criteria. Use a fixed stratified development subset for frequent iteration and reserve the complete pinned suite for finalists or major milestones. Never compare scores across judge or benchmark versions without labeling the version change.
- IteraTeR and EditEval are editing diagnostics. Do not use the IteraTeR intent classifier as an authoritative long-form coherence or style grader; its published performance is materially weaker for those labels than for clarity. Use paired examples and deterministic or independently judged diagnostics.
- Revision for Concision is a small sentence-level academic-writing benchmark. Use it as a narrow concision diagnostic, not the primary evidence for email or memo quality.
- YapBench tests excess verbosity on short-answer tasks. Use it as an anti-verbosity guardrail, not as an executive-writing quality score.
- Treat every public benchmark as a compatibility or regression measure that may have appeared in model pretraining. It cannot by itself establish generalization.

Organize evaluation evidence into four tiers:

1. Tier A: pinned public legacy benchmarks for compatibility and regression tracking.
2. Tier B: the GoodProse authentic-task development benchmark, divided before experimentation into:
   - Tier B1 search-development: frequent item-level feedback for hypothesis formation and candidate screening.
   - Tier B2 shadow-development: periodic aggregate-only feedback, with no item-level outputs, rationales, or per-slice optimization until the benchmark version is retired.
3. Tier C: a sealed, private, time-stamped GoodProse holdout used exactly once per benchmark version after finalist decisions are frozen.
4. Tier D: a final blinded intended-audience human evaluation of the strongest frozen candidates.

Do not run Tier B2 on every iteration. Establish a preregistered cadence or promotion rule from Tier B1, use B2 only to detect search overfitting, and preserve aggregate-only access. A candidate that improves B1 but repeatedly regresses B2 should not advance without a documented explanation.

Every evaluation result must record:

- Model and exact model version
- Base model and adapter/checkpoint
- Prompt version
- Inference configuration
- Dataset and split version
- Grader and grader version
- Random seed
- Code revision
- Timestamp
- Hardware or provider
- Cost and token usage where available

Prefer deterministic grading whenever possible. Use LLM judges only where necessary, calibrate them against human judgments or strong reference examples, and make judged comparisons blinded and position-balanced.

For important LLM-judge comparisons:

- Hide candidate identity, provider, profile label, and training method.
- Randomize answer position and repeat a balanced subset with positions swapped.
- Record position-flip rate, tie rate, parse failures, verbosity sensitivity, and disagreement.
- Use two independent judge families when affordable for finalist comparisons.
- Avoid using the same model family as candidate, teacher, and sole judge when practical.
- Normalize presentation so superficial formatting or length cues do not determine preference.
- Calibrate the final judge analysis against the final human results and report judge-human agreement; do not retroactively tune the frozen candidate set to those results.

Before material experimentation, preregister the primary metric, hard gates, minimum practically important effect, comparison set, and statistical method for each benchmark version. Default to paired example-level analysis, stratified paired bootstrap confidence intervals, effect sizes, and correction or explicit caveats for repeated model and hyperparameter comparisons. The default minimum effect is two absolute points on the 100-point automated development score or a human win rate of at least 55% excluding ties with a confidence interval above chance when the study is adequately powered. If power is insufficient, report the comparison as inconclusive rather than as a win.

Never expose reference answers, target continuations, hidden test cases, or grader rubrics to the model under evaluation or to Ox Alpha.

CUSTOM GOODPROSE EVALUATION

Create a versioned GoodProse custom benchmark that fits cleanly into the repository’s existing evaluation abstractions.

The benchmark must cover:

- Rough notes to executive email
- Rough notes to internal memo
- Meeting transcript to decision memo
- Technical source material to engineering document
- Long draft to concise revision
- Disorganized draft to coherent revision
- Source documents to strategy update
- Announcement or launch memo
- Sensitive or difficult internal communication
- Short-form post or thread
- Blog post or explanatory essay
- Audience adaptation for executives, engineers, customers, and a broad public audience
- Minimal-edit revision where unnecessary change is penalized
- Content-controlled profile rendering in which every profile receives the same neutral source material
- Topic swaps and leave-topic-out cases that separate writing characteristics from subject matter
- Adversarial fidelity cases involving numbers, dates, names, attribution, negation, uncertainty, caveats, and confidential placeholders

Evaluate at least:

- Source fidelity
- Factual correctness
- Clarity
- Coherence
- Concision
- Information density
- Organization
- Actionability
- Audience fit
- Tone control
- Technical precision
- Appropriate uncertainty
- Non-redundancy
- Absence of unsupported claims
- Avoidance of empty verbosity or “yapping”
- Preservation of important caveats
- Quality of subject lines, openings, headings, and conclusions where applicable
- Edit minimality and preservation of already-good source text where applicable
- Topic leakage, lexical mimicry, memorized phrase overlap, and identity-signaling shortcuts

Build source-informed evaluation slices for all eleven named research sources. These slices must test abstract traits and genre competence, not ask the model to impersonate a person. Include neutral shared-content tasks, adversarial topic swaps, leave-topic-out evaluation, and leave-time-out evaluation. Treat an authorship classifier only as a diagnostic. Run exact- and fuzzy-match checks for copied phrases and long n-gram overlap against all training and style-reference material.

Create an explicit error taxonomy and report errors by type, including fabrication, numerical mutation, omission, caveat loss, intent reversal, overcompression, unnecessary expansion, poor actionability, audience mismatch, tone failure, structural failure, topic leakage, profile overfitting, and excessive rewriting.

Keep an immutable final holdout. Use the B1 search-development split for frequent iteration and the B2 shadow-development split for periodic aggregate-only checks. Group examples by original document, thread, source, person, publication, topic, and time period so closely related material cannot cross train, development, and test splits.

The sealed final holdout must be newly authored or privately assembled where practical, time-stamped, content-hashed, access-controlled, and withheld from Ox Alpha, teacher models, synthetic-data generators, tuning jobs, retrieval indexes, prompt construction, and development judges. Add canary fingerprints plus exact, n-gram, and embedding-based contamination scans. Public benchmarks are never substitutes for this private holdout.

Codex may implement and test the Tier C schema, one-shot runner, cryptographic receipt, and synthetic fixtures, but after benchmark registration or finalist-selection work begins it must not author, inspect, transform, or retrieve the true Tier C content or rubrics. The user or a separately quarantined process must supply and retain the holdout outside the agent-readable repository, or behind encryption and an access boundary unavailable to the training and orchestration agents.

The one-shot Tier C runner must return only preregistered aggregate results, content and configuration hashes, execution timestamp, and an immutable run receipt. It must not return item-level inputs, outputs, rationales, slice values that reveal examples, or grader rubrics until the holdout version is formally retired. Open the holdout exactly once per benchmark version, only after finalists and every behavior-affecting configuration are frozen.

If genuine access separation cannot be established, label the set `procedurally_held_out`, never `sealed`, state that limitation prominently, and do not treat its result as equivalent evidence. After authorized item-level inspection, retire that holdout version from future model selection. Aggregate results may remain in reports, but examples and rubrics must not flow back into training or prompt development.

Never move an example between splits to improve a score.

HUMAN EVALUATION AND CONTINUED AUTONOMY

Design the final human-evaluation protocol during Phase 1, but do not ask the user or raters to evaluate immature candidates. Request or launch new human ratings only after the finalist-readiness gate is satisfied:

- All safe zero-cost work and all approved, high-value automated experiments relevant to finalist selection are complete.
- The strongest prompt, retrieval, unified fine-tune, and justified adapter candidates have been compared.
- At least two evidence-driven improvement iterations have occurred after the initial baseline.
- No unresolved affordable hypothesis has a higher expected value than freezing the candidate set.
- The candidates pass automated fidelity, privacy, rights, leakage, and deployment hard gates.
- The candidate set is small, diverse, versioned, frozen, and accompanied by a concise evaluation packet.

Recruit intended-audience raters rather than a generic undifferentiated crowd: founders or executives for decision communications, technical leaders for engineering documents, and experienced business editors across the task mix. Record rater qualification and analyze material subgroup differences without revealing candidate identity.

Use approximately 50 to 100 difficult, representative cases, adjusted by a documented power analysis. Show raters the source material, intended audience, communication objective, and constraints. For each output, require one operational label: `publishable`, `minor_edits`, `substantive_edits`, or `unacceptable`; collect a critical-factual-error veto, structured error labels, and estimated editing burden or editing time. The primary endpoint is publish-ready acceptance and substantive-edit burden among hard-gate-passing outputs.

Use blinded pairwise preference as a secondary discriminative endpoint, permitting `preferred A`, `preferred B`, `tie`, and `both unacceptable`. Freeze three to five diverse finalists, then select two or three for the human packet using the preregistered automated selection rule. Use a balanced incomplete-block design rather than all-pairs comparison when scale requires it. Seek three blinded ratings per assigned case or comparison where feasible, randomize and balance answer position, and measure inter-rater agreement, preference rates, confidence intervals, unacceptable-output rates, critical-error rates, editing burden, and subgroup results. Do not tell raters which named source, model, provider, or training method produced an answer.

Human evaluation is the final confirmation and production-selection authority, but it must not make the rest of the agentic loop idle:

- While ratings, approvals, or adjudication are pending, continue all useful non-leaking work that does not alter the frozen candidates or sealed evaluation set.
- Prioritize improvements to the model families that lead the automated scorecard, plus a bounded exploration budget for credible challengers.
- Continue reproducibility work, source audits, rights research, ingestion quality, training efficiency, cost reduction, inference tooling, documentation, failure-taxonomy analysis, and next-version dataset construction.
- Challenger experiments started after the freeze must use a new candidate lineage and may not inspect the current sealed holdout or human results. If a challenger clears the preregistered development margin before ratings arrive, freeze and version it separately; add it to the current human packet only if this does not compromise blinding or invalidate completed ratings, otherwise reserve it for the next confirmation round.
- Never change a frozen finalist in place. Any prompt, decoding, retrieval, data, or checkpoint change creates a new candidate identifier.
- Do not repeatedly ask the user for partial judgments. Submit one compact, decision-ready human-evaluation request containing the best candidates and clear instructions.
- Do not block autonomous work while recruiting qualified raters or collecting results. Continue the highest-value non-leaking work and next-version challenger program without modifying the frozen evaluation packet.
- If human results become the sole remaining completion condition and no other evidence-bearing work remains, record that state accurately and wait without fabricating, inferring, or replacing the human result.

Do not make an unqualified final production claim before human confirmation. Automated results may support a clearly labeled provisional leader while human evaluation is pending.

PUBLIC EMAIL AND LITIGATION-EXHIBIT WORKSTREAM

Audit publicly accessible, author-verified emails for every named research source.

This is a bounded supporting workstream, not the critical path. Until the first-evidence milestone is complete, allocate no more than 15% of active agent effort to public-email and litigation-exhibit discovery, and do not let it delay the initial baselines, smoke fine-tune, shared results table, or failure analysis. After the first complete loop, expand this work only when expected information value exceeds the next model or dataset experiment. Litigation email remains a supplemental genre even when plentiful.

For each candidate email source, record:

- Person
- Source type
- Case or investigation name
- Court and jurisdiction
- Docket number
- Filing number
- Exhibit number
- Page number
- Primary source URL
- Archival URL when appropriate
- Retrieval date
- Current public, sealed, restricted, or stricken status
- Source content hash
- Verified sender
- Date and thread identifier
- Authorship confidence and evidence
- PII and redaction status
- Rights classification
- Approved uses
- Reviewer and review date

Use these source types:

- `voluntarily_published`
- `court_exhibit`
- `government_investigation`
- `hacked_or_leaked`
- `secondary_republication`
- `unverified`

Use these rights classifications:

- `training_approved`
- `private_research_only`
- `evaluation_only`
- `permission_required`
- `excluded`

Default rules:

- Hacked or leaked material is `excluded`.
- Sealed, restricted, accidentally exposed, or unverifiable material is `excluded`.
- Do not evade paywalls, authentication, sealing, robots controls, or access restrictions.
- Unsealed litigation and government-investigation exhibits are `private_research_only` or `evaluation_only` until explicitly approved for training.
- Voluntary publication does not automatically grant model-training or redistribution rights. Mark it `permission_required` until its permitted use is documented.
- Public accessibility is not the same as public-domain status.
- Do not assume a privately authored email became a US-government work merely because it was attached to a government filing.
- A rights question blocks only that source’s inclusion in training, not the rest of the project.

Initial leads to verify from primary sources:

Sam Altman:
- Musk v. Altman, N.D. Cal. case 4:24-cv-04722
- OpenAI’s “OpenAI and Elon Musk”
- OpenAI’s “Elon Musk wanted an OpenAI for-profit”
- CourtListener or PACER as the docket source of truth
- Secondary indexes may be used for discovery but not as final provenance

Jeff Bezos:
- Intentionally published About Amazon employee emails
- House Judiciary digital-markets investigation
- Amazon internal materials cited in the investigation, including the referenced Bezos-to-Dave Limp Ring communication
- FTC filings only where authorship can be verified at the individual-message level

Andy Jassy:
- Intentionally published Amazon and AWS employee communications
- The official AWS next-CEO employee email
- FTC and congressional materials, but only retain messages demonstrably authored by Jassy

Fred Wilson:
- Record that he acknowledged his emails appeared in the hacked Sony archive
- Classify the hacked archive as `excluded`
- Do not retrieve or train on it without explicit legal authorization that supersedes the default exclusion

For Patrick Collison, Paul Graham, Joel Spolsky, David Heinemeier Hansson, Jason Fried, Simon Willison, and Cory Doctorow:
- Record the current absence of a verified authored litigation-email corpus if the search still produces none
- Prefer voluntarily published writing and company communications
- Do not fill gaps with data-broker records, contact databases, scraped inboxes, dubious mirrors, or unrelated emails that merely mention the person

Before retaining any email content:

- Verify the document remains publicly accessible and has not been sealed or stricken.
- Remove email addresses, recipients, phone numbers, signatures, home addresses, account information, credentials, and third-party personal data.
- Remove family, health, financial, and unrelated personal material.
- Retain only the named author’s own message body.
- Strip quoted replies, forwarded messages, headers, footers, attachments, and text written by other people.
- Reject uncertain, assistant-written, ghostwritten, or misattributed messages.
- Preserve thread-level grouping for split isolation.
- Deduplicate normalized message bodies.
- Do not commit raw exhibits, raw inbox exports, or raw email dumps.
- Keep unsanitized litigation documents local and ignored.
- Do not send unsanitized litigation documents to Ox Alpha, OpenRouter, or any external model provider.

Treat litigation email as its own genre and distribution. It is likely to be unusually terse, defensive, adversarial, and transactional. It should be a small supplement or held-out realism evaluation, not the foundation of the general business-writing model.

DATASET PIPELINE

Build a reproducible, provenance-aware pipeline that separates:

- Raw source discovery manifests
- Locally cached raw source data
- Sanitized and normalized documents
- Training examples
- Development examples
- Evaluation examples
- Preference pairs
- Synthetic examples
- Rejected or excluded examples

Model the training corpus as three explicitly weighted and independently ablatable collections:

1. `task_pairs`: authentic rough source material paired with a final or professionally revised business artifact. This is the primary corpus because it matches the deployed transformation task.
2. `style_targets`: training-approved polished writing used at lower weight to teach abstract target characteristics without pretending that target-only text demonstrates revision ability.
3. `preference_pairs`: competing revisions with a preference, structured reason, and error labels, used only with a justified preference objective.

Record the loss weight or sampling ratio of each collection for every run. Do not merge them into an undifferentiated text corpus.

Prioritize authentic rough-to-final pairs from public revision histories with compatible licenses, deliberately contributed or user-authored before/after examples, and other genuinely paired records. When authentic pairs are scarce, keep synthetic rough drafts in a separate `synthetic_roughening` lane with their generation history and an explicit ablation. Deterministically corrupting a polished final document creates an artificial inverse problem and must not become the core evidence that the model handles real rough material.

Prefer a smaller high-quality, task-aligned corpus over a larger noisy scrape. Measure data value through source- and genre-level ablations rather than assuming more tokens improve the system.

Never silently modify raw data.

For every derived example, preserve:

- Source and canonical URL
- Author or organization
- Publication date
- Retrieval date
- Document type and genre
- Transformation history
- Extractor and extractor version
- Sanitization status
- Rights classification
- Split assignment
- Content hash
- Parent document and thread identifiers
- Whether the example is original, synthetic, or transformed

Build deterministic tools for:

- Normalization
- Boilerplate removal
- Quoted-thread removal
- PII detection and redaction
- Near-duplicate detection
- Document segmentation
- Genre labeling
- Profile labeling
- Train/eval contamination checks
- Dataset versioning
- Manifest validation

Synthetic data must be labeled as synthetic, traceable to its generating prompt and model, and tested for contamination and collapse. Do not allow generated examples to masquerade as writing by a named person.

Any data, rubric, rewrite, preference, or annotation generated by Ox Alpha or another model must be labeled with generator provenance and isolated so experiments can measure performance with and without it. A generator must not have access to sealed evaluation material.

When using Ox Alpha or another model for best-of-N distillation or rejection sampling:

1. Use only sanitized, rights-safe inputs that are permitted for the selected external provider. Never send private, unsanitized, B2 item-level, or Tier C material.
2. Generate multiple candidates with the exact generator, prompt, decoding, and seed provenance recorded.
3. Reject candidates that fail deterministic fidelity, privacy, placeholder, numerical, attribution, or format checks before model judging.
4. Rank survivors with independent judges or rubrics. Ox Alpha must not be the sole generator and sole judge for the same example.
5. Preserve every acceptance or rejection reason, candidate hash, generator identifier, judge identifier, and intended dataset use.
6. Distill only accepted outputs into an explicitly synthetic student-training collection.
7. Run an ablation with and without the synthetic teacher data and report whether gains survive the authentic-task development benchmark.

Do not treat synthetic volume as independent evidence. Measure effective sample size after near-duplicate, prompt-template, and semantic-cluster analysis.

TRAINING PROGRAM

Begin with environment discovery:

- Identify available CPU, RAM, disk, Apple Silicon/GPU capability, CUDA availability, and existing model caches.
- Identify available local training frameworks already compatible with the environment.
- Prefer existing dependencies and lightweight tooling.
- Evaluate MLX, PEFT/TRL, LoRA/QLoRA, or equivalent approaches based on the actual hardware.
- Select open-weight base models only after reviewing model quality, context length, fine-tuning support, license, redistribution terms, memory requirements, and likely training cost.

Establish at least these baselines:

1. Untuned base-model baseline.
2. Strong prompt-engineered baseline.
3. Retrieval or example-conditioned baseline if appropriate.
4. Strong accessible frontier-model teacher or quality-ceiling baseline when free or approved.
5. Direct single-pass and structured plan-write-verify/revise inference variants.
6. Unified profile-conditioned fine-tune.
7. Source-specific LoRA or adapter experiments where approved data exists.
8. Optional best-of-N distillation, rejection sampling, or preference optimization after a successful supervised fine-tune.

Do not assume fine-tuning will beat prompting. Measure it.

Training should support:

- Supervised fine-tuning
- LoRA or QLoRA
- Resumable checkpoints
- Deterministic seeds where feasible
- Config-driven runs
- Per-profile sampling controls
- Genre balancing
- Length balancing
- Data ablations
- Hyperparameter sweeps within budget
- Optional DPO or another justified preference method
- Provenance-aware best-of-N distillation and rejection-sampling datasets
- Model and dataset cards
- Complete run manifests
- Explicit sampling ratios for `task_pairs`, `style_targets`, and `preference_pairs`
- Clustered or composable profile controls where the base model and framework permit them
- Checkpoint selection rules chosen before the final comparison
- Throughput, peak memory, latency, and inference-cost measurement

Implement the structured generation candidate with explicit, inspectable boundaries:

1. Extract a claims and decision ledger from the source, preserving uncertainty, attribution, numbers, caveats, and requested actions.
2. Build an audience-aware outline that contains only ledger-supported content.
3. Render the draft under the selected descriptive profile and channel constraints.
4. Verify each factual claim, number, date, name, attribution, caveat, and action against the ledger with deterministic checks wherever possible.
5. Revise only the failed spans, then rerun the verifier.

Record intermediate artifact hashes and verifier outcomes without exposing private content in committed logs. Compare quality, factual-gate rate, latency, and cost against matched direct single-pass generation.

Do not commit large model weights to git. Store paths, hashes, configurations, metrics, and reproducible retrieval instructions.

Perform a real standalone training run for each named profile that satisfies both the documented sufficiency threshold and `training_approved` status. For every other profile, perform at least one real conditioned, retrieval, mixture, or ablation experiment that creates meaningful training coverage without representing a statistically weak run as a production adapter. Also train at least one unified controllable model.

Allocate most training compute to the model families on the current quality/fidelity Pareto frontier. Preserve a small, documented exploration allocation for alternatives so an early noisy result does not permanently lock the program into the wrong base model or architecture.

If the full intended model is too expensive initially:

- Run an end-to-end smoke fine-tune on a small model and small approved dataset.
- Prove the complete pipeline works.
- Continue improving datasets, evals, prompts, and configurations.
- Produce a precise estimate for the recommended full run.
- Do not represent a smoke-test model as the final candidate.

AUTONOMOUS IMPROVEMENT LOOP

After establishing baselines:

1. Run deterministic hard gates and the cheap stratified Tier B1 screen.
2. Analyze failures by genre, profile, length, source, grader, and error type.
3. Form explicit improvement hypotheses.
4. Rank hypotheses by expected quality gain, cost, risk, and information value.
5. Change one major experimental factor at a time where practical.
6. Train or configure the next candidate with bounded resources and early stopping.
7. Rerun hard gates and the same B1 screen; prune failing or clearly dominated candidates.
8. Promote only passing, competitive candidates to the full Tier B1 development suite, and query aggregate-only Tier B2 at its preregistered cadence.
9. Compare against all relevant baselines, including the strongest non-training and quality-ceiling baselines.
10. Record paired effect sizes, stratified confidence intervals, selection and multiple-comparison caveats, wins, regressions, costs, and qualitative examples from permitted splits.
11. Keep or revert the hypothesis based on evidence.
12. Repeat until the stopping conditions are satisfied or a genuine external blocker remains.

Maintain a hypothesis registry so unsuccessful ideas are not unknowingly repeated. Prefer one major causal change at a time, but allow clearly labeled multi-factor engineering changes when isolation would be prohibitively expensive. Do not select winners from a broad sweep and report them as confirmatory evidence without accounting for the selection process.

Use a best-arm-with-exploration policy: direct most autonomous effort toward candidates on the quality/fidelity Pareto frontier while reserving a bounded portion for credible alternative base models, data mixtures, and architectures. Prune branches that repeatedly fail hard gates or remain dominated after an adequately powered comparison.

Potential iteration levers include:

- Data cleaning
- Data mix
- Genre balance
- Profile conditioning
- Training objective
- Base-model choice
- Learning rate
- Adapter rank
- Context length
- Prompt construction
- Preference pairs
- Negative examples
- Concision-specific training
- Fidelity training
- Inference decoding
- Output-length control
- Structured claims-ledger extraction and verification
- Best-of-N candidate generation and rejection thresholds
- Synthetic-teacher data inclusion and mixture weight

Do not optimize against the final holdout. Open it exactly once per benchmark version only after the candidate set, architecture, data mixture, prompt, retrieval corpus, checkpoint, decoding, and main hyperparameters are frozen. Viewing item-level final-holdout results retires that benchmark version from future selection.

Track both aggregate performance and the Pareto frontier between:

- Writing quality
- Source fidelity
- Concision
- Latency
- Model size
- Inference cost
- Training cost

Apply a plateau rule to prevent indefinite optimization or manufactured wins. By default, Phase 3 is saturated after three independent, credible hypotheses fail to improve the preregistered automated development score by at least two absolute points or a smaller statistically credible and practically valuable margin, provided the leading candidate still passes every hard gate. Revisit the default only before the relevant results are observed and record the reason.

COST, CREDIT, AND PAYMENT POLICY

The maximum total settled project budget is USD $100.

This $100 ceiling is authorization to propose paid work, not authorization to charge anything automatically. The unapproved spending limit remains USD $0.

Complete Phase 0 and as much of Phase 1 as possible for $0. Do not request paid training until the benchmark, approved starter data, strongest free baselines, expected-value argument, and costed experimental design are ready. A small paid evaluation expense may be proposed earlier only when it is necessary to validate the benchmark and no credible free substitute exists.

Before the first paid action, Codex must stop at a budget checkpoint and ask the user for explicit approval of a narrowly scoped spending envelope. The user intends to provide an agent credit card only after approving that request. The request must state:

- Allowed provider or vendors
- Allowed products, models, GPUs, or services
- Allowed experimental purposes and experiment identifiers
- Expected quality, information, or speed benefit
- Estimated total charge and per-category sublimits
- Maximum possible settled charge under the envelope
- Expected duration
- How much of the $100 project budget will remain
- Whether a free or local alternative exists
- Provider-side hard-limit and shutdown plan

The user intends to provide an agent credit card after approving a proposed expense. Request payment access only through an authorized, secure agent-card or checkout mechanism. Never ask the user to paste a full card number, CVV, PIN, bank credential, or other raw payment credential into chat. Never write payment data to files, environment files, logs, shell history, source code, screenshots, model prompts, experiment trackers, or git. Never send payment data to Ox Alpha, OpenCode, OpenRouter, or another model.

After the user approves the envelope and securely provides the agent card, Codex may autonomously perform the listed experiments within the named providers, purposes, category sublimits, and total maximum without asking for each minor run. A different provider, new purpose, subscription, automatic renewal, higher total limit, or purchase outside the envelope requires new approval. This delegated envelope is intended to preserve autonomy without broadening financial authority.

Use the following planning allocation as a default, not as permission to spend and not as a reason to waste remaining budget:

- 0-10% for smoke tests and infrastructure
- Up to 20% for evaluation and judge calibration
- Up to 50% for the most promising training family or configuration
- Up to 20% for final confirmation
- At least 10% held in reserve until the final decision point

Reallocate within an approved envelope only when evidence shows a higher expected value and the envelope permits it. Prefer early stopping, successive halving, stratified evaluation subsets, and one high-quality confirmation run over repeated full benchmark or training runs. Repeated full WritingBench runs and eleven independent large fine-tunes are not presumed feasible within $100.

Maintain an auditable budget ledger in `programs/executive-writing/reports/COSTS.md` containing proposed, approved, attempted, settled, refunded, and remaining amounts, but never payment credentials. Include timestamps, provider, purpose, experiment identifier, and supporting receipt or transaction reference when available.

Do not exceed $100 total settled project spend. Include taxes, fees, storage, data transfer, idle compute, API evaluation, and recurring charges in the ceiling. Configure provider-side hard spending limits wherever possible. Disable auto-recharge and automatic renewal. Shut down paid compute immediately after the approved experiment. Verify afterward that no paid resources remain running.

Do not purchase or pay for:

- Data whose training rights are unclear
- Scraped personal information
- Access to sealed, hacked, leaked, or restricted documents
- A subscription when a one-time purchase suffices
- Paid Ox Alpha/OpenRouter usage if Codex can take over directly at comparable quality
- Repeated training runs without evidence from the preceding run
- Anything outside the GoodProse objective

Continue all useful zero-cost work before and while waiting for a budget decision.

Create `programs/executive-writing/reports/COSTS.md` with at least:

- What can be completed for $0
- Expected local-training feasibility
- Ox Alpha/OpenRouter pricing and rate-limit status
- Disk and compute requirements
- A low-cost experiment tier
- A recommended experiment tier
- An ambitious experiment tier capped at the remaining project budget
- Estimated training cost per model or adapter
- Estimated evaluation cost
- Expected number of runs
- Expected wall-clock time
- Which purchases materially improve likely quality
- Which purchases are optional convenience
- Approved, settled, refunded, and remaining budget totals

DELIVERABLES

The repository must contain, at minimum:

- A documented architecture
- A completed first-evidence vertical slice with 20 to 50 task-aligned cases, three baselines, a smoke fine-tune, a shared results table, and a failure analysis
- Reproducible source and rights manifests
- Data ingestion and sanitization code
- Train/eval contamination checks
- Adapters for the requested external evaluations
- A versioned GoodProse custom benchmark
- Four-tier evaluation handling, including B1 search-development, B2 aggregate-only shadow-development, a one-shot Tier C holdout lifecycle, and an intended-audience human-evaluation protocol
- Baseline configurations and results
- Fine-tuning configurations
- At least one completed real fine-tuning run
- Source-specific run configurations for all eleven named people
- Actual standalone source-specific runs wherever approved data is sufficient, plus real lower-cost experiment coverage for every other profile
- A unified-model training run
- A matched direct-generation versus structured plan-write-verify/revise comparison
- A provenance-aware best-of-N distillation or rejection-sampling experiment when rights-safe teacher access is available, including a with/without-synthetic-data ablation
- Evaluation reports comparing candidates with paired effect sizes, confidence intervals, judge-bias diagnostics, and explicit confirmatory versus exploratory labels
- A three-corpus training data model covering task pairs, style targets, and preference pairs
- Content-controlled style evaluation, adversarial fidelity cases, and memorization checks
- A frozen set of three to five finalists and an automatically selected, compact two- or three-candidate blinded human-evaluation packet
- Final human results and judge-human calibration when ratings are returned; until then, a clearly labeled provisional report and active continuation plan
- Experiment history
- Cost and hardware analysis
- Model cards
- Dataset cards
- A recommended production architecture
- A CLI or similarly simple interface for applying the selected model/profile to rough source material
- Clear instructions for reproducing ingestion, training, evaluation, and inference

Maintain:

- `programs/executive-writing/reports/PROGRESS.md`
- `programs/executive-writing/reports/EXPERIMENTS.md`
- `programs/executive-writing/reports/COSTS.md`
- `programs/executive-writing/reports/SOURCE_AUDIT.md`
- A machine-readable experiment registry
- A machine-readable latest-results artifact
- A human-readable final report

Adapt names and locations to the existing repository structure rather than duplicating an established convention.

GIT CHECKPOINTS

Commit small, coherent, reviewed milestones as work progresses. Use the following milestone groups as guidance rather than manufacturing empty or arbitrary commits:

1. Architecture, environment audit, and experiment plan
2. External evaluation adapters
3. Source manifests and rights system
4. Custom GoodProse benchmark
5. Dataset ingestion, sanitization, and contamination checks
6. Baseline inference and results
7. Training pipeline
8. Initial fine-tuned models and run manifests
9. Source-specific and unified-model experiments
10. Iterative improvements
11. Frozen automated evaluation, human-evaluation packet, and final or provisional recommendation

Commit messages must explain the completed outcome. Do not bundle unrelated user changes. Do not commit secrets, credentials, payment details, unsanitized litigation material, restricted datasets, raw email dumps, provider caches, or large model weights.

STOPPING CONDITIONS

Do not mark this goal complete merely because the pipeline exists.

Completion requires all of the following:

- The requested external evaluations are integrated or have documented, tested adapters and reproducible acquisition steps where licensing prevents inclusion.
- The four-tier GoodProse evaluation program is implemented, versioned, documented, and split safely.
- The first-evidence vertical slice is complete and its shared results and failure analysis are committed.
- All eleven named research sources have source audits, rights classifications, profile specifications, evaluation coverage, and run configurations.
- Every profile with sufficient training-approved data has received a real standalone training run; every other profile has meaningful lower-cost experiment coverage and an explicit blocker or insufficiency record.
- At least one unified controllable model has completed a real training run.
- Prompt, retrieval, direct and structured generation, unified fine-tune, and justified adapter alternatives have been compared without assuming the fine-tune must win.
- The selected candidate passes every hard gate and does not achieve its gain through unacceptable regressions in factual fidelity, unsupported claims, intent preservation, privacy, rights, memorization, or train/evaluation leakage.
- At least two evidence-driven improvement iterations have been completed after the first baseline.
- The preregistered statistical analysis, effect sizes, confidence intervals, repeated-comparison caveats, and negative results are reported.
- Relevant tests, lint, formatting, and type checking pass.
- A genuinely access-separated Tier C holdout has been run exactly once for its benchmark version after the complete finalist configuration and selection procedure were frozen, with only aggregate results and an immutable receipt returned. A merely procedurally held-out result must be reported but does not satisfy this sealed-evidence condition.
- Three to five strong, diverse candidates have been frozen and the preregistered rule has selected the best two or three for blinded human evaluation only after the finalist-readiness gate was satisfied.
- Final intended-audience human evaluation has been completed, including publish-readiness, critical-error veto, editing burden, and pairwise results, and has been used for the production recommendation. If ratings are still pending, the system may publish only a clearly labeled provisional leader and the goal remains active while useful autonomous work continues.
- Results are reproducible from committed code and manifests.
- Costs, unresolved rights issues, limitations, and blocked profile runs are reported honestly.
- All paid resources have been shut down, settled project spend is at or below $100, and the remaining budget is documented.
- The final report recommends the best architecture and gives exact commands for using and reproducing it.

Any of these scientifically valid outcomes may satisfy the model-selection portion of the goal once the other completion conditions, including final human confirmation, are met:

1. A fine-tuned candidate wins and is recommended.
2. A prompt-only or retrieval-conditioned system remains superior and is recommended, with the fine-tuning result reported honestly.
3. No candidate achieves the preregistered minimum effect within the data, rights, hardware, and budget constraints; recommend the strongest hard-gate-passing baseline and publish a rigorous negative or inconclusive result.

Do not continue indefinitely merely to force a fine-tuning win. It is valid to stop model optimization after the plateau rule, budget limit, or exhaustion of preregistered high-value hypotheses, provided the best available system and evidence are complete. A negative result is not a failed goal.

If a paid training run is the only remaining high-value path, finish every safe prerequisite, produce the scoped budget-envelope request, and continue any useful zero-cost work while waiting for approval and secure agent-card access. Do not falsely mark the goal complete.

If a source lacks training permission, that source’s run may remain explicitly blocked, but the system, evaluation profile, configuration, and permission requirements must still be complete and documented.

Keep working through recoverable errors, failed experiments, rate limits, suboptimal results, pending approvals, and pending human ratings. Preserve evidence from failed runs. Prefer the best-performing model families while maintaining bounded exploration. Ask the user only when new authority or uniquely human judgment is genuinely required, including approving a scoped spending envelope, securely providing the agent credit card, promoting data to `training_approved`, obtaining restricted data, accepting a material scope change, resolving an unavoidable legal-rights decision, or performing the final blinded human evaluation.

When asking for the final human evaluation, present only the best frozen, hard-gate-passing candidate set after automated optimization has saturated. Do not use human attention for routine iteration that deterministic metrics, LLM judges, ablations, or failure analysis can resolve. After asking, do not idle: follow the continued-autonomy rules until human results are the sole remaining condition and no other evidence-bearing work remains.
