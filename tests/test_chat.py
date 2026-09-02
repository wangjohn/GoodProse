from __future__ import annotations

from typing import Any

import pytest

from goodprose.chat import (
    ChatTemplateError,
    assistant_prefix,
    prompt_strategy,
    render_prompt,
    verify_template_parity,
)


class _QwenLikeTokenizer:
    """Mimics the Qwen3 template: the empty think block appears only when thinking is off."""

    chat_template = "{% if enable_thinking is defined and enable_thinking is false %}<think>..."
    eos_token = "<|im_end|>"

    def __init__(self, *, honors_flag: bool = True) -> None:
        self.honors_flag = honors_flag

    def apply_chat_template(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        rendered = "".join(
            f"<|im_start|>{message['role']}\n{message['content']}<|im_end|>\n"
            for message in messages
        )
        assert kwargs["tokenize"] is False and kwargs["add_generation_prompt"] is True
        rendered += "<|im_start|>assistant\n"
        if self.honors_flag and kwargs.get("enable_thinking") is False:
            rendered += "<think>\n\n</think>\n\n"
        return rendered


MESSAGES = [
    {"role": "system", "content": "System."},
    {"role": "user", "content": "Notes about a thing."},
]


def test_render_prompt_passes_chat_template_kwargs_and_exposes_assistant_prefix() -> None:
    rendered = render_prompt(_QwenLikeTokenizer(), MESSAGES, {"enable_thinking": False})

    assert rendered.endswith("<|im_start|>assistant\n<think>\n\n</think>\n\n")
    assert assistant_prefix(rendered, MESSAGES[-1]["content"]) == (
        "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
    )


def test_verify_template_parity_accepts_a_template_that_honors_the_flag() -> None:
    digest = verify_template_parity(_QwenLikeTokenizer(), MESSAGES, {"enable_thinking": False})

    assert len(digest) == 64


def test_verify_template_parity_rejects_a_missing_think_block() -> None:
    with pytest.raises(ChatTemplateError, match="did not add the empty think block"):
        verify_template_parity(
            _QwenLikeTokenizer(honors_flag=False), MESSAGES, {"enable_thinking": False}
        )


def test_prompt_strategy_is_stable_for_equal_kwargs() -> None:
    assert prompt_strategy({"enable_thinking": False}) == prompt_strategy(
        {"enable_thinking": False}
    )
    assert prompt_strategy({}) != prompt_strategy({"enable_thinking": False})
