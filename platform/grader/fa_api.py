"""Claude API helpers for the Console mission graders (P1 to P5).

Graders call the API with the player's own key from ANTHROPIC_API_KEY and never store it.
The model is configurable: set FA_MODEL to override the default.
Needs the anthropic SDK (pinned in the Season 1 lab image); it's imported only when used,
so the rest of the grader toolkit stays stdlib-only.
"""
from __future__ import annotations

import os

# Approved Nov 23, 2026 (open-questions D20). Override with FA_MODEL.
DEFAULT_MODEL = "claude-haiku-5-5"
# USD per million tokens, for prompts of 100K tokens or fewer. Message Batches cost half.
# Cache rates follow the usual multipliers (reads 0.1x input, 5-minute writes 1.25x input).
PRICES = {
    "claude-haiku-5-5": {"input": 0.10, "output": 0.50, "cache_read": 0.01, "cache_write": 0.125},
}
KEY_HINT = ("Set ANTHROPIC_API_KEY to your own Claude Console API key (with a spending limit): add it as a "
            "Codespaces secret named ANTHROPIC_API_KEY and rebuild, or run export ANTHROPIC_API_KEY=... in this terminal.")


class ApiKeyMissing(Exception):
    pass


def model() -> str:
    return os.environ.get("FA_MODEL") or DEFAULT_MODEL


def client():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise ApiKeyMissing(KEY_HINT)
    import anthropic
    return anthropic.Anthropic(max_retries=4)


def text_of(message) -> str:
    return "".join(block.text for block in message.content if block.type == "text")


class Usage:
    """Adds up token use across calls and estimates the cost."""

    FIELDS = ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")

    def __init__(self, model_id: str):
        self.model = model_id
        self.calls = 0
        self.totals = dict.fromkeys(self.FIELDS, 0)

    def add(self, usage) -> None:
        self.calls += 1
        for f in self.FIELDS:
            self.totals[f] += getattr(usage, f, None) or 0

    def cost(self, batch: bool = False):
        p = PRICES.get(self.model)
        if p is None:
            return None
        t = self.totals
        usd = (t["input_tokens"] * p["input"] + t["output_tokens"] * p["output"]
               + t["cache_read_input_tokens"] * p["cache_read"]
               + t["cache_creation_input_tokens"] * p["cache_write"]) / 1_000_000
        return usd / 2 if batch else usd

    def summary(self, batch: bool = False) -> str:
        t = self.totals
        cost = self.cost(batch)
        price = f"about ${cost:.4f}" if cost is not None else "cost unknown for this model"
        return (f"{self.calls} calls to {self.model}: {t['input_tokens']:,} input, {t['output_tokens']:,} output, "
                f"{t['cache_read_input_tokens']:,} cache read, {t['cache_creation_input_tokens']:,} cache write tokens; "
                f"{price}")
