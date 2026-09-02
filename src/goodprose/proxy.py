"""Cheap automatic proxies for "does this sound like the author", run on every checkpoint.

None of these replace the blind human review. They exist so checkpoints, data mixes, and
model sizes can be ranked in minutes instead of an hour of reading, and so obvious failure
modes (looping, regurgitating training text, copying the input through) are caught before a
human ever sees the outputs. Calibrate the ranking once against a completed blind review.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from goodprose.jsonl import atomic_write_json, load_jsonl
from goodprose.models import BlogPost, EvalCase, ModelOutput, Split, SplitAssignment
from goodprose.text import longest_shared_run, matched_word_share, words

_SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"“(\[])")
_PARAGRAPH = re.compile(r"\n\s*\n")
_HEADING = re.compile(r"^#{1,6}\s", re.MULTILINE)
_LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+\.)\s", re.MULTILINE)
_LINK = re.compile(r"\[[^\]]+\]\([^)]+\)")
_BOLD = re.compile(r"\*\*[^*]+\*\*")
_PAREN = re.compile(r"\(")
_EM_DASH = re.compile(r"—|(?<=\w)--(?=\w)| - ")
_CONTRACTION = re.compile(r"\b\w+[\'\N{RIGHT SINGLE QUOTATION MARK}](?:t|s|re|ve|ll|d|m)\b", re.I)
_HEDGE = re.compile(
    r"\b(?:i think|i suspect|probably|likely|seems?|pretty|generally|roughly|usually|"
    r"tends? to|in my experience|arguably|mostly|somewhat|kind of|sort of)\b",
    re.I,
)
_FIRST_SINGULAR = frozenset({"i", "i'm", "i've", "i'd", "i'll", "me", "my", "mine", "myself"})
_FIRST_PLURAL = frozenset({"we", "we're", "we've", "we'd", "we'll", "us", "our", "ours"})
_SECOND = frozenset({"you", "you're", "you've", "you'd", "you'll", "your", "yours"})
FUNCTION_WORDS: tuple[str, ...] = (
    "the",
    "a",
    "an",
    "and",
    "but",
    "or",
    "so",
    "because",
    "if",
    "when",
    "while",
    "that",
    "which",
    "this",
    "these",
    "those",
    "it",
    "its",
    "of",
    "to",
    "in",
    "on",
    "for",
    "with",
    "at",
    "by",
    "from",
    "as",
    "into",
    "about",
    "than",
    "then",
    "there",
    "here",
    "just",
    "really",
    "very",
    "much",
    "more",
    "most",
    "also",
    "even",
    "still",
    "only",
    "actually",
    "though",
    "although",
    "however",
    "instead",
    "rather",
    "where",
    "how",
    "what",
    "why",
    "not",
    "no",
    "yes",
    "all",
    "some",
    "any",
    "every",
    "both",
    "each",
    "other",
    "same",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "can",
    "could",
    "will",
    "would",
    "should",
    "might",
    "may",
    "get",
    "got",
    "make",
    "like",
)
RATE_FEATURES: tuple[str, ...] = (
    "mean_sentence_words",
    "sentence_words_std",
    "mean_paragraph_words",
    "mattr_200",
    "em_dash_per_1k",
    "parenthetical_per_1k",
    "question_per_1k",
    "colon_per_1k",
    "list_item_per_1k",
    "heading_per_1k",
    "link_per_1k",
    "bold_per_1k",
    "contraction_per_1k",
    "hedge_per_1k",
    "first_singular_per_1k",
    "first_plural_per_1k",
    "second_person_per_1k",
)


class ProxyError(ValueError):
    """Proxy inputs are inconsistent."""


def _sentences(text: str) -> list[str]:
    plain = _HEADING.sub("", text)
    plain = _LIST_ITEM.sub("", plain)
    parts = [part.strip() for part in _SENTENCE_END.split(plain.replace("\n", " "))]
    return [part for part in parts if len(words(part)) > 0]


def _mattr(tokens: Sequence[str], window: int = 200) -> float:
    if not tokens:
        return 0.0
    if len(tokens) <= window:
        return len(set(tokens)) / len(tokens)
    counts: Counter[str] = Counter(tokens[:window])
    total = len(counts)
    for index in range(window, len(tokens)):
        leaving = tokens[index - window]
        counts[leaving] -= 1
        if counts[leaving] == 0:
            del counts[leaving]
        counts[tokens[index]] += 1
        total += len(counts)
    return total / (len(tokens) - window + 1) / window


def _repeated_ngram_share(tokens: Sequence[str], n: int = 4) -> float:
    if len(tokens) < n + 1:
        return 0.0
    grams = [tuple(tokens[index : index + n]) for index in range(len(tokens) - n + 1)]
    return 1 - len(set(grams)) / len(grams)


def style_features(text: str) -> dict[str, float]:
    """Surface statistics of one text; rates are per 1,000 words."""
    tokens = words(text, strip_urls=False)
    word_count = len(tokens)
    per_1k = 1000 / word_count if word_count else 0.0
    sentences = _sentences(text)
    sentence_lengths = [len(words(sentence)) for sentence in sentences] or [0]
    mean_sentence = sum(sentence_lengths) / len(sentence_lengths)
    variance = sum((length - mean_sentence) ** 2 for length in sentence_lengths) / len(
        sentence_lengths
    )
    paragraphs = [part for part in _PARAGRAPH.split(text) if words(part)]
    paragraph_lengths = [len(words(part)) for part in paragraphs] or [0]
    function_counts = Counter(token for token in tokens if token in FUNCTION_WORDS)
    return {
        "words": float(word_count),
        "sentences": float(len(sentences)),
        "paragraphs": float(len(paragraphs)),
        "mean_sentence_words": mean_sentence,
        "sentence_words_std": math.sqrt(variance),
        "mean_paragraph_words": sum(paragraph_lengths) / len(paragraph_lengths),
        "mattr_200": _mattr(tokens),
        "repeated_4gram_share": _repeated_ngram_share(tokens),
        "em_dash_per_1k": len(_EM_DASH.findall(text)) * per_1k,
        "parenthetical_per_1k": len(_PAREN.findall(text)) * per_1k,
        "question_per_1k": text.count("?") * per_1k,
        "colon_per_1k": text.count(":") * per_1k,
        "list_item_per_1k": len(_LIST_ITEM.findall(text)) * per_1k,
        "heading_per_1k": len(_HEADING.findall(text)) * per_1k,
        "link_per_1k": len(_LINK.findall(text)) * per_1k,
        "bold_per_1k": len(_BOLD.findall(text)) * per_1k,
        "contraction_per_1k": len(_CONTRACTION.findall(text)) * per_1k,
        "hedge_per_1k": len(_HEDGE.findall(text)) * per_1k,
        "first_singular_per_1k": sum(token in _FIRST_SINGULAR for token in tokens) * per_1k,
        "first_plural_per_1k": sum(token in _FIRST_PLURAL for token in tokens) * per_1k,
        "second_person_per_1k": sum(token in _SECOND for token in tokens) * per_1k,
        **{f"fw_{word}": function_counts[word] * per_1k for word in FUNCTION_WORDS},
    }


def function_word_distance(left: dict[str, float], right: dict[str, float]) -> float:
    """Cosine distance between the two function-word rate profiles (0 identical, 1 unrelated)."""
    left_vector = [left.get(f"fw_{word}", 0.0) for word in FUNCTION_WORDS]
    right_vector = [right.get(f"fw_{word}", 0.0) for word in FUNCTION_WORDS]
    dot = sum(a * b for a, b in zip(left_vector, right_vector, strict=True))
    left_norm = math.sqrt(sum(a * a for a in left_vector))
    right_norm = math.sqrt(sum(b * b for b in right_vector))
    if left_norm == 0 or right_norm == 0:
        return 1.0
    return max(0.0, 1 - dot / (left_norm * right_norm))


def style_distance(sample: dict[str, float], reference: dict[str, float]) -> float:
    """Mean absolute log-ratio over the surface rate features; 0 means identical rates."""
    deltas = [abs(math.log((sample[name] + 1) / (reference[name] + 1))) for name in RATE_FEATURES]
    return sum(deltas) / len(deltas)


def _reference_posts(posts_path: Path, splits_path: Path) -> list[BlogPost]:
    posts = load_jsonl(posts_path, BlogPost)
    splits = {
        assignment.lineage_id: assignment.split
        for assignment in load_jsonl(splits_path, SplitAssignment)
    }
    reference = [post for post in posts if splits.get(post.lineage_id) is Split.TRAIN]
    if not reference:
        raise ProxyError("no training-split posts found to build the author reference profile")
    return reference


def _outputs(path: Path, case_ids: set[str]) -> dict[str, ModelOutput]:
    outputs = {record.id: record for record in load_jsonl(path, ModelOutput)}
    missing = sorted(case_ids - set(outputs))
    if missing:
        raise ProxyError(f"{path} is missing outputs for {missing}")
    return outputs


def proxy_report(
    cases_path: Path,
    system_outputs: Sequence[tuple[str, Path]],
    posts_path: Path,
    splits_path: Path,
    output_path: Path,
    *,
    memorization_run_threshold: int = 30,
) -> dict[str, Any]:
    """Score one or more output files against the author's published training prose."""
    if not system_outputs:
        raise ProxyError("at least one --outputs LABEL=PATH is required")
    cases = {case.id: case for case in load_jsonl(cases_path, EvalCase)}
    if not cases:
        raise ProxyError("evaluation case file is empty")
    reference_posts = _reference_posts(posts_path, splits_path)
    reference_text = "\n\n".join(post.body_markdown for post in reference_posts)
    reference_profile = style_features(reference_text)
    reference_words = {post.id: words(post.body_markdown) for post in reference_posts}

    systems: list[dict[str, Any]] = []
    for label, path in system_outputs:
        outputs = _outputs(path, set(cases))
        pooled = "\n\n".join(outputs[case_id].output for case_id in sorted(cases))
        profile = style_features(pooled)
        per_case: list[dict[str, Any]] = []
        for case_id in sorted(cases):
            case = cases[case_id]
            output = outputs[case_id].output
            output_words = words(output)
            reference_words_count = len(words(case.reference_output))
            longest_training_run = max(
                (
                    longest_shared_run(output_words, post_words)
                    for post_id, post_words in reference_words.items()
                    if post_id != case_id
                ),
                default=0,
            )
            features = style_features(output)
            per_case.append(
                {
                    "id": case_id,
                    "lineage_id": case.lineage_id,
                    "output_words": len(output_words),
                    "reference_words": reference_words_count,
                    "length_ratio": (
                        len(output_words) / reference_words_count if reference_words_count else 0
                    ),
                    "input_copy_share": matched_word_share(case.input, output),
                    "longest_input_run": longest_shared_run(words(case.input), output_words),
                    "longest_training_post_run": longest_training_run,
                    "memorization_flag": longest_training_run >= memorization_run_threshold,
                    "repeated_4gram_share": features["repeated_4gram_share"],
                    "style_distance": style_distance(features, reference_profile),
                    "function_word_distance": function_word_distance(features, reference_profile),
                }
            )
        systems.append(
            {
                "label": label,
                "outputs": str(path),
                "style_distance": style_distance(profile, reference_profile),
                "function_word_distance": function_word_distance(profile, reference_profile),
                "repeated_4gram_share": profile["repeated_4gram_share"],
                "memorization_flags": sum(row["memorization_flag"] for row in per_case),
                "mean_length_ratio": sum(row["length_ratio"] for row in per_case) / len(per_case),
                "profile": {name: profile[name] for name in ("words", *RATE_FEATURES)},
                "per_case": per_case,
            }
        )
    systems.sort(key=lambda system: system["style_distance"])
    report = {
        "version": 1,
        "cases": len(cases),
        "reference_posts": [post.id for post in reference_posts],
        "reference_profile": {name: reference_profile[name] for name in ("words", *RATE_FEATURES)},
        "memorization_run_threshold": memorization_run_threshold,
        "ranking": [system["label"] for system in systems],
        "systems": systems,
        "note": (
            "Lower style_distance and function_word_distance are closer to the author's "
            "published prose. This ranks checkpoints; it does not replace the blind review."
        ),
    }
    atomic_write_json(output_path, report)
    return report
