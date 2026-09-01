# Evaluation

`cases.jsonl` is generated from the `test` split by `goodprose build-sft`. It contains the held-out
input and the owner's published reference, but the CLI never exports the reference as model input.

Put base and fine-tuned model outputs under `results/`, then use `goodprose eval prepare` to create
a randomized blind packet. After filling its review fields, use `goodprose eval summarize`.
