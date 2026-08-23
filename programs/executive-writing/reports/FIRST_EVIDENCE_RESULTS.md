# First-evidence results

Status: complete first closed loop; visible exploratory evidence, not a
production recommendation.

## Outcome

The first-evidence milestone now includes 24 project-owned B1 cases, three
matched initial baselines, two evidence-driven inference iterations, one real
MLX LoRA smoke fine-tune, matched base-versus-adapter inference, case-level
evaluation, a shared results table, and failure analysis. Every provider charge
was $0.

The directional B1 leader remains the untuned Ollama compact-ledger/draft
candidate at 87.1981 mean score and 50.00% hard-gate pass. Its +2.3698-point
gain over retrieval v1 has a 95% paired-bootstrap interval of -2.0211 to
+6.7390, so it is promising visible search evidence rather than confirmation.

The genuine smoke adapter is rejected for quality use. Under exact matched MLX
profile inference it regressed 3.4870 points (95% interval -11.5720 to +4.8613)
and hard gates fell from 16.67% to 0%. Under exact matched ledger/draft it
regressed 13.6092 points (95% interval -21.1011 to -6.3146) and hard gates fell
from 29.17% to 4.17%.

## Shared B1 table

All rows use the same 24 B1 cases and deterministic scorer v1.1. MLX rows are
the causal base-versus-adapter comparison. Ollama rows use a different runtime
package and are architecture references, not exact weight controls.

| Candidate | Runtime / strategy | Trained | Score | Hard gates | Mean latency | Output tokens | Cost | Decision |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Minimal v1 | Ollama / minimal | no | 67.5522 | 25.00% | 1,293.9 ms | 2,937 | $0 | baseline |
| Profile v1 | Ollama / profile | no | 84.2839 | 20.83% | 2,114.1 ms | 5,862 | $0 | baseline |
| Retrieval v1 | Ollama / retrieval | no | 84.8283 | 37.50% | 1,703.0 ms | 4,200 | $0 | improvement baseline |
| Four-stage structured v1 | Ollama / ledger-draft-verify-revise | no | 81.3694 | 33.33% | 7,239.6 ms | 16,861 | $0 | reject |
| Compact ledger/draft v2 | Ollama / ledger-draft | no | **87.1981** | **50.00%** | 2,850.5 ms | 6,362 | $0 | directional leader |
| MLX base profile | MLX / profile | no | 71.3900 | 16.67% | 1,839.2 ms | 9,784 | $0 | tune control |
| MLX base ledger/draft | MLX / ledger-draft | no | 73.8629 | 29.17% | 2,629.2 ms | 12,780 | $0 | tune control |
| MLX smoke LoRA profile | MLX / profile | yes | 67.9030 | 0.00% | 807.3 ms | 3,218 | $0 | reject for quality |
| MLX smoke LoRA ledger/draft | MLX / ledger-draft | yes | 60.2537 | 4.17% | 1,227.9 ms | 4,189 | $0 | reject for quality |

## Genuine training evidence

The frozen MLX run updated the last four layers of the 4-bit Qwen 2.5 0.5B
base for 40 iterations and 4,198 trained tokens. It completed in 20.862 seconds
excluding download, peaked at 1.075 GB, and produced a 2,938,645-byte adapter
whose 56 tensors were all nonzero. Validation loss fell from 1.891 to 0.168;
synthetic test loss was 0.190. Those values prove the plumbing and rapid fit to
the small templated corpus; they do not demonstrate writing quality.

## Failure analysis and decision

The smoke targets taught surface structure faster than content grounding. The
tuned profile candidate increased omission cases from 16 to 23, placeholder
losses from two to three, and poor-actionability cases from eight to 15. Under
ledger/draft, omissions increased from 10 to 23, placeholder losses from one to
three, and poor-actionability cases from six to 18.

Reviewed outputs show four recurring patterns:

- repeated generic headings or caveat phrases;
- omission of source facts and requested actions;
- substitution of template shape for task-specific reasoning;
- leakage of procurement-example facts into an unrelated budget memo, a
  semantic fabrication that the lexical scorer does not fully capture.

The adapter is retained only as genuine pipeline evidence. Another synthetic
template run is not justified. The next training hypothesis requires more
diverse, task-aligned, rights-safe rough-to-final pairs plus explicit negative
fidelity controls. Until then, evaluation validity, authentic-pair acquisition,
and the untuned compact-ledger/draft branch have higher expected value.

## Limitations

B1 is visible, small, project-authored, and lexically scored. It cannot
establish semantic correctness, authentic-task generalization, publishability,
or intended-audience preference. The directional leader still fails half of
the hard gates. B2, sealed Tier C, calibrated semantic evaluation, and final
human confirmation remain future gates.
