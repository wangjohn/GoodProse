# Style references

This collection defines how GoodProse output should read. It is separate from the content-foundation collection because a document can contain excellent reasoning and still be inappropriate for an executive audience or channel.

An approved style reference must pass the rules in [`HOUSE_STYLE.md`](HOUSE_STYLE.md). Approval applies only to the recorded section or human-normalized artifact, not automatically to its complete upstream document.

[`index.json`](index.json) has four groups:

- `approved_examples`: training-side prose that passed the complete house-style review. This list starts empty.
- `ranked_source_exemplars`: unusually clear upstream documents, ranked by mechanical screening and manual review. They are references, not approved gold outputs.
- `rewrite_candidates`: source sections selected for human normalization. These may not enter training until the normalized artifact passes review.
- `held_out_benchmarks`: the clearest public development and test documents. They remain evaluation-only and must not influence prose training or prompt development beyond the permissions of their source split.

The current source ranking predates the GoodProse pivot. It remains useful as a clarity-oriented seed set, but it is not yet representative of executive emails, internal memos, or public essays. Add only permissioned executive-writing examples, and keep held-out documents out of training.

This separation prevents three common errors: treating sentence length as proof of clarity, treating clarity as proof of technical quality, and leaking held-out documents into training because their prose is attractive.
