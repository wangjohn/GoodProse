"""One prompt renderer shared by training, generation, scoring, and preference building.

The adapter must see exactly the prefix at training time that it is conditioned on at
inference time. Qwen3 makes this easy to get wrong: with ``enable_thinking=False`` the
generation prompt ends in an empty ``<think>`` block that the default training render
omits. Every code path therefore renders through :func:`render_prompt` with the same
``chat_template_kwargs`` and records a hash of the resulting assistant prefix.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from typing import Any

from goodprose.jsonl import canonical_json

ChatTemplateKwargs = Mapping[str, bool | int | str]
DEFAULT_CHAT_TEMPLATE_KWARGS: dict[str, bool | int | str] = {"enable_thinking": False}


class ChatTemplateError(ValueError):
    """The chat template cannot produce a training/inference-consistent prompt."""


def render_prompt(
    tokenizer: Any,
    messages: Sequence[Mapping[str, str]],
    chat_template_kwargs: ChatTemplateKwargs,
) -> str:
    """Render system and user turns plus the assistant header as plain text."""
    rendered = tokenizer.apply_chat_template(
        list(messages),
        tokenize=False,
        add_generation_prompt=True,
        **dict(chat_template_kwargs),
    )
    if not isinstance(rendered, str) or not rendered:
        raise ChatTemplateError("chat template did not render a non-empty prompt string")
    return rendered


def prompt_strategy(chat_template_kwargs: ChatTemplateKwargs) -> str:
    """A stable label for the prompt render, compared across baseline and candidate runs."""
    return "matched-system-prompt:" + canonical_json(dict(chat_template_kwargs))


def assistant_prefix(rendered_prompt: str, user_content: str) -> str:
    """The text the model is conditioned on after the last user turn."""
    index = rendered_prompt.rfind(user_content)
    if index < 0:
        raise ChatTemplateError("rendered prompt does not contain the user turn verbatim")
    return rendered_prompt[index + len(user_content) :]


def assistant_prefix_sha256(rendered_prompt: str, user_content: str) -> str:
    return hashlib.sha256(assistant_prefix(rendered_prompt, user_content).encode()).hexdigest()


def verify_template_parity(
    tokenizer: Any,
    messages: Sequence[Mapping[str, str]],
    chat_template_kwargs: ChatTemplateKwargs,
) -> str:
    """Check the render is usable for training and return the assistant prefix hash.

    The training set stores the rendered prompt as text, so the prefix must be a plain
    string suffix. When thinking is explicitly disabled on a template that supports it,
    the prefix must actually carry the empty think block; otherwise a fine-tune would
    learn a prefix it never sees at inference time.
    """
    rendered = render_prompt(tokenizer, messages, chat_template_kwargs)
    prefix = assistant_prefix(rendered, messages[-1]["content"])
    if not prefix.strip():
        raise ChatTemplateError("chat template adds no assistant header after the user turn")
    template = getattr(tokenizer, "chat_template", "") or ""
    thinking_disabled = chat_template_kwargs.get("enable_thinking") is False
    if thinking_disabled and "enable_thinking" in template and "<think>" not in prefix:
        raise ChatTemplateError(
            "enable_thinking=False did not add the empty think block to the assistant prefix; "
            "training and inference prompts would differ"
        )
    return hashlib.sha256(prefix.encode()).hexdigest()
