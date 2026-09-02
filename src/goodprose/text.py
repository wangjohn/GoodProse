"""Small deterministic text utilities shared by review, leakage, and proxy metrics."""

from __future__ import annotations

import re
from collections.abc import Sequence
from difflib import SequenceMatcher

WORD = re.compile(r"[\w]+(?:[\'\N{RIGHT SINGLE QUOTATION MARK}-][\w]+)*", re.UNICODE)
URL = re.compile(r"https?://[^\s)>\]]+")


def words(value: str, *, strip_urls: bool = True) -> list[str]:
    source = URL.sub("", value) if strip_urls else value
    return [word.casefold() for word in WORD.findall(source)]


def longest_shared_word_run(left: str, right: str) -> int:
    """Length of the longest run of consecutive words shared by both texts (URLs excluded)."""
    return longest_shared_run(words(left), words(right))


def longest_shared_run(left_words: Sequence[str], right_words: Sequence[str]) -> int:
    previous = [0] * (len(right_words) + 1)
    longest = 0
    for left_word in left_words:
        current = [0] * (len(right_words) + 1)
        for index, right_word in enumerate(right_words, start=1):
            if left_word == right_word:
                current[index] = previous[index - 1] + 1
                longest = max(longest, current[index])
        previous = current
    return longest


def matched_word_share(source: str, target: str) -> float:
    """Share of target words that sit inside blocks also present, in order, in the source."""
    target_words = words(target)
    if not target_words:
        return 0.0
    matcher = SequenceMatcher(None, words(source), target_words, autojunk=False)
    matched = sum(block.size for block in matcher.get_matching_blocks())
    return matched / len(target_words)
