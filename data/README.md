# Data

The canonical data flow is:

```text
Markdown blog export -> posts/posts.jsonl
reviewed briefs      -> briefs.jsonl
joined records       -> pairs.jsonl
SFT build            -> sft/train.jsonl and sft/dev.jsonl
test split           -> ../evals/cases.jsonl
```

Canonical posts, briefs, and pairs may be committed when they are safe to publish. Generated SFT
files are ignored because they can be rebuilt byte-for-byte from the canonical pairs.
