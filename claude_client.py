"""Thin async Anthropic SDK wrapper with prompt caching enabled.

`cache_control: {type: "ephemeral"}` on the system block caches the system
prompt across requests. The SDK retries 429/5xx automatically (max_retries=2);
override per-call via .with_options(max_retries=N).

NOTE: Prompt caching only activates when the cached prefix is at least
the model's minimum cache size:
  - Opus 4.7 / 4.6 / Haiku 4.5: 4096 tokens minimum
  - Sonnet 4.6:                  2048 tokens minimum
The demo system prompt below is short; cache_read_input_tokens will be 0
until you grow the system prompt above the threshold. Try pasting a long
docs page or onboarding guide as the system prompt to see caching activate.
"""
from __future__ import annotations

import os
from typing import AsyncIterator

import anthropic
from anthropic import AsyncAnthropic

MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-4-7")

SYSTEM_PROMPT = """You are a friendly demo assistant for the Claude Streaming Starter.
Answer concisely. Prefer Python in code examples unless the user asks otherwise.
If asked to summarise a long document, give 3-5 bullet points then a 1-line takeaway."""

_client: AsyncAnthropic | None = None


def _get_client() -> AsyncAnthropic:
    """Lazy-init so the module imports cleanly without ANTHROPIC_API_KEY set
    (useful for type-checking / CI without secrets)."""
    global _client
    if _client is None:
        _client = AsyncAnthropic()  # reads ANTHROPIC_API_KEY from env
    return _client


async def stream_chat(
    user_message: str,
    history: list[dict[str, str]],
) -> AsyncIterator[tuple[str, anthropic.types.Message | None]]:
    """Stream a chat turn. Yields (text_delta, final_message) tuples.

    `final_message` is None for delta chunks and populated on the final yield
    with the complete Message object (carrying usage stats for cost calc).
    """
    messages = [*history, {"role": "user", "content": user_message}]

    async with _get_client().messages.stream(
        model=MODEL,
        max_tokens=4096,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=messages,
    ) as stream:
        async for text in stream.text_stream:
            yield text, None
        final = await stream.get_final_message()
        yield "", final
