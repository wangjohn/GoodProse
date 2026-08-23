# GoodProse deterministic scorer v1.1 calibration addendum

Status: correction rules frozen at 2026-08-23T03:48:27Z after candidate
generation and before any v1.1 rescoring.

## Trigger and validity status

The v1 scorer marked the sentence “we should not assume the result applies to
enterprise accounts” as an affirmative forbidden claim because the registered
alias `applies to enterprise` appeared literally. This is a demonstrated
construct-validity defect, not a model failure. It affected the same
`b1-011-concise-onboarding-revision` check for all three generated candidates.

The original outputs, timings, token counts, v1 scores, and hashes remain
preserved. The v1 score and aggregate summary artifacts are invalidated for
candidate comparison. The correction is necessarily post-generation
evaluator calibration and must not be described as confirmatory or as part of
the original preregistration.

## Frozen correction

Scorer `goodprose-deterministic-v1.1` changes only forbidden-claim matching:

1. Find every exact normalized occurrence of every registered forbidden alias.
2. Treat an occurrence as negated when an explicit negation marker appears in
   the same punctuation-delimited clause with no more than six intervening word
   tokens.
3. Supported markers are `no`, `not`, `never`, `cannot`, `can't`, `won't`,
   `isn't`, `aren't`, `doesn't`, `don't`, `didn't`, `shouldn't`, `wouldn't`,
   and `couldn't`.
4. `not only` is not treated as negation.
5. Any non-negated occurrence of an alias still fails the forbidden-claim
   check, even if another occurrence is negated.

Required-fact aliases, placeholders, must-preserve spans, format checks,
length rules, score weights, cases, and all candidate output bytes are
unchanged. The v1.1 run must rescore existing outputs without inference.

## Required regression tests

- Explicitly negated `should not assume ... applies to enterprise` passes.
- Affirmative `applies to enterprise` fails.
- A sentence boundary prevents an earlier negation from masking a later
  affirmative claim.
- `not only applies to enterprise` fails.
- Mixed negated and affirmative occurrences fail.

This narrow lexical repair does not make the scorer semantic. Its known
limitations and the requirement for calibrated independent or human
evaluation remain unchanged.
