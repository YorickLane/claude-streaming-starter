"""Per-request token cost calculator for Anthropic API.

Prices in USD per million tokens. Cache write costs 1.25x input (5min TTL),
cache read costs 0.10x input.

For 1h TTL: cache write is 2x instead of 1.25x. Adjust the formula if you
opt into ttl='1h' on cache_control blocks.
"""
from __future__ import annotations

PRICE_PER_M = {
    "claude-opus-4-7":   {"in": 5.0,  "out": 25.0},
    "claude-opus-4-6":   {"in": 5.0,  "out": 25.0},
    "claude-sonnet-4-6": {"in": 3.0,  "out": 15.0},
    "claude-haiku-4-5":  {"in": 1.0,  "out": 5.0},
}


def calc_cost(model: str, usage) -> dict:
    """Return a structured cost dict from an Anthropic `usage` object."""
    p = PRICE_PER_M.get(model, PRICE_PER_M["claude-opus-4-7"])
    cache_write = usage.cache_creation_input_tokens or 0
    cache_read = usage.cache_read_input_tokens or 0
    uncached_in = usage.input_tokens or 0
    out = usage.output_tokens or 0
    cost = (
        uncached_in * p["in"] / 1_000_000
        + cache_write * p["in"] * 1.25 / 1_000_000  # 5min TTL
        + cache_read * p["in"] * 0.10 / 1_000_000
        + out * p["out"] / 1_000_000
    )
    return {
        "model": model,
        "uncached_input_tokens": uncached_in,
        "cache_write_tokens": cache_write,
        "cache_read_tokens": cache_read,
        "output_tokens": out,
        "cost_usd": round(cost, 6),
    }
