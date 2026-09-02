# Generated SFT data

Run `goodprose build-sft` to create `train.jsonl`, `dev.jsonl`, and `manifest.json` here. These
files are ignored and reproducible from `data/private/pairs.jsonl`. With `--raw-completions`,
`train.jsonl` also carries one title-conditioned completion per distinct training target, a
cheap continued-pretraining view of the same approved text; the manifest counts pairs and raw
completions separately and `counts.train` is the total number of records. With
`--train-cases-output`, the training inputs are also written in the evaluation case format so the
current adapter can be sampled on them to build `preference.jsonl` for DPO.

The manifest pins the system prompt and the SHA-256 hash of every generated artifact. Validate
the dataset and a starter configuration without loading a model:

```bash
uv run goodprose train-lora-plus \
  --config configs/qwen3-8b-lora.json \
  --validate-only
```
