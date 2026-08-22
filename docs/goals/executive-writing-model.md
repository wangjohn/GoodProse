# GoodProse Executive-Writing Model Goal

Paste the following into Codex as a `/goal` command.

```text
/goal Build GoodProse into a provenance-aware, reproducible system for evaluating, training, and iteratively improving language models that turn authentic rough source material into exceptionally clear executive emails, internal memos, strategy documents, engineering documents, blog posts, and short-form posts.

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

The final primary endpoint is blinded human pairwise preference among candidates that pass the hard gates. Automated metrics and LLM judges are development proxies, not substitutes for the final human comparison.

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

Compare this architecture ladder rather than assuming fine-tuning or one adapter per source is best:

1. Strong prompt-only profile cards.
2. Prompting plus retrieval of approved examples.
3. A unified controllable fine-tune that switches among writing profiles, genres, audiences, and levels of formality.
4. Clustered, composable, or low-rank-basis adapters for groups of compatible writing characteristics.
5. Separate source-specific or profile-specific LoRA/adaptor models when the evidence and approved data support them.
6. A hybrid of retrieval, unified training, and adapters.

Choose the final architecture from evaluation evidence. It may be a unified model, separate adapters, or a hybrid.

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

Preserve experiment coverage for all eleven people, but do not force eleven statistically weak production adapters. Before a standalone source-specific run, define and apply a documented sufficiency threshold based on data quality, diversity, and evaluation power. The default threshold is at least 50,000 clean training-approved author tokens, at least 100 independent examples, coverage across at least three relevant genres or clearly documented genre limitations, and at least 30 independent content-controlled held-out cases. Change these defaults only before seeing comparative results and record the rationale.

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
- Resolve the exact currently available OpenRouter model identifier for Ox Alpha.
- Explicitly configure OpenCode to use Ox Alpha through OpenRouter.
- Do not silently substitute another model.
- Verify the selected model in the task output or metadata.
- Treat Ox Alpha as free only after checking its current price. If it is no longer free, obtain approval before using the project budget for it.

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

Phase 0: feasibility, environment, and rights; target spend $0

- Audit the repository, hardware, model caches, tools, Ori/OpenCode/Ox Alpha access, exact provider pricing, licenses, and source availability.
- Establish provisional rights classifications and identify the authority required for promotion to `training_approved`.
- Produce a data-volume and genre-diversity estimate for every profile.
- Exit when the project has a technically feasible local or approved external path, a rights-safe starter corpus, and a documented zero-cost work plan.
- If fine-tuning is infeasible, continue with prompt, retrieval, evaluation, data, and reproducibility work while documenting the blocker and best alternative.

Phase 1: evaluation validity and baselines; target spend $0 or minimal approved evaluation cost

- Implement the evaluation hierarchy, frozen benchmark schemas, contamination controls, baseline inference, automated development scorecard, and human-evaluation protocol.
- Run untuned, prompt-engineered, and retrieval/example-conditioned baselines.
- Characterize evaluator reliability, position sensitivity, verbosity sensitivity, and disagreement on a fixed reference or previously human-labeled calibration set when one is legally available.
- Exit when there is a reproducible task-aligned development benchmark, an untouched sealed holdout, credible baselines, and enough signal to distinguish meaningful changes.
- Do not request new human ratings merely to pass this phase; prepare the protocol and continue with automated and deterministic evidence.

Phase 2: unified pilot and architecture decision

- Build the three-corpus training pipeline and complete an end-to-end smoke run.
- Train at least one genuine unified profile-conditioned candidate on the smallest base model that can answer the architectural question credibly.
- Compare prompting, retrieval, unified fine-tuning, and at least one justified adapter or composition strategy.
- Exit when the entire training/evaluation path is reproducible and evidence identifies the most promising model families, data mixtures, and architecture branches.
- Do not spend materially or multiply profile adapters if the unified pilot cannot beat or complement the strongest non-training baseline on the preregistered development criteria.

Phase 3: autonomous optimization and profile coverage

- Concentrate compute and agent effort on the best-performing model families while preserving a bounded exploration allocation for credible challengers.
- Run source-specific adapters only above the documented sufficiency threshold; use lower-cost conditioned or ablation experiments for the remaining profiles.
- Continue until high-value affordable hypotheses are exhausted, the plateau rule is met, the approved budget is exhausted, or the finalist-readiness gate is satisfied.

Phase 4: frozen finalists and human confirmation

- Freeze the strongest diverse set of three to five candidates, including the strongest prompt/retrieval baseline whenever it remains competitive.
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
2. Tier B: the GoodProse authentic-task development benchmark used for iteration.
3. Tier C: a sealed, private, time-stamped GoodProse holdout used exactly once per benchmark version after finalist decisions are frozen.
4. Tier D: a final blinded human pairwise evaluation of the strongest frozen candidates.

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

CUSTOM RFCLEAR EVALUATION

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

Keep an immutable final holdout. Use a development split for iteration. Group examples by original document, thread, source, person, publication, topic, and time period so closely related material cannot cross train, development, and test splits.

The sealed final holdout must be newly authored or privately assembled where practical, time-stamped, content-hashed, access-controlled, and withheld from Ox Alpha, teacher models, synthetic-data generators, tuning jobs, retrieval indexes, prompt construction, and development judges. Add canary fingerprints plus exact, n-gram, and embedding-based contamination scans. Public benchmarks are never substitutes for this private holdout.

Open the sealed holdout exactly once per benchmark version, only after finalists and every behavior-affecting configuration are frozen. After inspecting item-level results, retire that holdout version from future model selection. Aggregate results may remain in reports, but examples and rubrics must not flow back into training or prompt development.

Never move an example between splits to improve a score.

HUMAN EVALUATION AND CONTINUED AUTONOMY

Design the final human-evaluation protocol during Phase 1, but do not ask the user or raters to evaluate immature candidates. Request or launch new human ratings only after the finalist-readiness gate is satisfied:

- All safe zero-cost work and all approved, high-value automated experiments relevant to finalist selection are complete.
- The strongest prompt, retrieval, unified fine-tune, and justified adapter candidates have been compared.
- At least two evidence-driven improvement iterations have occurred after the initial baseline.
- No unresolved affordable hypothesis has a higher expected value than freezing the candidate set.
- The candidates pass automated fidelity, privacy, rights, leakage, and deployment hard gates.
- The candidate set is small, diverse, versioned, frozen, and accompanied by a concise evaluation packet.

Use approximately 50 to 100 difficult, representative pairwise cases, adjusted by a documented power analysis. Seek three blinded ratings per comparison where feasible. Permit `preferred A`, `preferred B`, `tie`, and `both unacceptable`; collect a short structured reason and error labels. Randomize and balance answer position. Measure inter-rater agreement, preference rates, confidence intervals, unacceptable-output rates, and subgroup results. Do not tell raters which named source, model, provider, or training method produced an answer.

Human evaluation is the final confirmation and production-selection authority, but it must not make the rest of the agentic loop idle:

- While ratings, approvals, or adjudication are pending, continue all useful non-leaking work that does not alter the frozen candidates or sealed evaluation set.
- Prioritize improvements to the model families that lead the automated scorecard, plus a bounded exploration budget for credible challengers.
- Continue reproducibility work, source audits, rights research, ingestion quality, training efficiency, cost reduction, inference tooling, documentation, failure-taxonomy analysis, and next-version dataset construction.
- Challenger experiments started after the freeze must use a new candidate lineage and may not inspect the current sealed holdout or human results. If a challenger clears the preregistered development margin before ratings arrive, freeze and version it separately; add it to the current human packet only if this does not compromise blinding or invalidate completed ratings, otherwise reserve it for the next confirmation round.
- Never change a frozen finalist in place. Any prompt, decoding, retrieval, data, or checkpoint change creates a new candidate identifier.
- Do not repeatedly ask the user for partial judgments. Submit one compact, decision-ready human-evaluation request containing the best candidates and clear instructions.
- If human results become the sole remaining completion condition and no other evidence-bearing work remains, record that state accurately and wait without fabricating, inferring, or replacing the human result.

Do not make an unqualified final production claim before human confirmation. Automated results may support a clearly labeled provisional leader while human evaluation is pending.

PUBLIC EMAIL AND LITIGATION-EXHIBIT WORKSTREAM

Audit publicly accessible, author-verified emails for every named research source.

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
4. Unified profile-conditioned fine-tune.
5. Source-specific LoRA or adapter experiments where approved data exists.
6. Optional preference optimization after a successful supervised fine-tune.

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
- Model and dataset cards
- Complete run manifests
- Explicit sampling ratios for `task_pairs`, `style_targets`, and `preference_pairs`
- Clustered or composable profile controls where the base model and framework permit them
- Checkpoint selection rules chosen before the final comparison
- Throughput, peak memory, latency, and inference-cost measurement

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

1. Run the full development evaluation suite.
2. Analyze failures by genre, profile, length, source, grader, and error type.
3. Form explicit improvement hypotheses.
4. Rank hypotheses by expected quality gain, cost, and risk.
5. Change one major experimental factor at a time where practical.
6. Train or configure the next candidate.
7. Re-run development evaluations.
8. Compare against all relevant baselines.
9. Record paired effect sizes, stratified confidence intervals, multiple-comparison caveats, wins, regressions, costs, and qualitative examples.
10. Keep or revert the hypothesis based on evidence.
11. Repeat until the stopping conditions are satisfied or a genuine external blocker remains.

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
- Reproducible source and rights manifests
- Data ingestion and sanitization code
- Train/eval contamination checks
- Adapters for the requested external evaluations
- A versioned GoodProse custom benchmark
- Four-tier evaluation handling, including sealed holdout lifecycle and a final human-evaluation protocol
- Baseline configurations and results
- Fine-tuning configurations
- At least one completed real fine-tuning run
- Source-specific run configurations for all eleven named people
- Actual standalone source-specific runs wherever approved data is sufficient, plus real lower-cost experiment coverage for every other profile
- A unified-model training run
- Evaluation reports comparing candidates with paired effect sizes, confidence intervals, judge-bias diagnostics, and explicit confirmatory versus exploratory labels
- A three-corpus training data model covering task pairs, style targets, and preference pairs
- Content-controlled style evaluation, adversarial fidelity cases, and memorization checks
- A frozen finalist set and compact blinded human-evaluation packet
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
- All eleven named research sources have source audits, rights classifications, profile specifications, evaluation coverage, and run configurations.
- Every profile with sufficient training-approved data has received a real standalone training run; every other profile has meaningful lower-cost experiment coverage and an explicit blocker or insufficiency record.
- At least one unified controllable model has completed a real training run.
- Prompt, retrieval, unified fine-tune, and justified adapter alternatives have been compared without assuming the fine-tune must win.
- The selected candidate passes every hard gate and does not achieve its gain through unacceptable regressions in factual fidelity, unsupported claims, intent preservation, privacy, rights, memorization, or train/evaluation leakage.
- At least two evidence-driven improvement iterations have been completed after the first baseline.
- The preregistered statistical analysis, effect sizes, confidence intervals, repeated-comparison caveats, and negative results are reported.
- Relevant tests, lint, formatting, and type checking pass.
- The sealed final holdout has been run exactly once for its benchmark version after the complete finalist configuration and selection procedure were frozen.
- The strongest three to five candidates have been packaged for blinded human evaluation only after the finalist-readiness gate was satisfied.
- Final human evaluation has been completed and used for the production recommendation. If ratings are still pending, the system may publish only a clearly labeled provisional leader and the goal remains active while useful autonomous work continues.
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
```
