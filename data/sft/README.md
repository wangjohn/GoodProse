# Generated SFT data

Run `goodprose build-sft` to create `train.jsonl`, `dev.jsonl`, and `manifest.json` here. These
files are ignored and reproducible from `data/private/pairs.jsonl`. The current approved build has
68 training examples, 3 development examples, and 4 frozen test cases. The manifest pins the
system prompt and the SHA-256 hash of every generated artifact.

Validate the dataset and starter LoRA+ configuration without loading a model:

```bash
uv run goodprose train-lora-plus \
  --config configs/qwen3-8b-lora-plus.json \
  --validate-only
```
