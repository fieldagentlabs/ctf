#!/usr/bin/env python3
"""Grader for S1-P1 Workbench.

Usage: control verify p1
Env:   ANTHROPIC_API_KEY (your own key; required), FA_MODEL (default claude-haiku-5-5)

Runs your exported system prompt (safehouse/p1/prompt.txt) on 50 held-out log lines,
one line per request, and checks that every reply is valid JSON with a label of
"attack" or "normal", and that at least 45 labels are right. Costs well under a cent
on the default model.
"""
from __future__ import annotations

import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO / "platform" / "grader"))
import fa_api  # noqa: E402
import fa_grader as fa  # noqa: E402

MISSION = "S1-P1"
PROMPT = REPO / "safehouse" / "p1" / "prompt.txt"
HELDOUT = Path(__file__).with_name("heldout.jsonl")
PASS_MARK = 45
FENCE = re.compile(r"^```(?:json)?\s*(.*?)\s*```$", re.S)


def parse(text: str):
    """The reply as {label, reason}, or None if it isn't the required JSON."""
    text = text.strip()
    m = FENCE.match(text)
    if m:
        text = m.group(1)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict) or data.get("label") not in ("attack", "normal") \
            or not isinstance(data.get("reason"), str):
        return None
    return data


def classify(client, model: str, prompt: str, line: str):
    msg = client.messages.create(model=model, max_tokens=2048, system=prompt,
                                 output_config={"effort": "low"},
                                 messages=[{"role": "user", "content": line}])
    return msg, (parse(fa_api.text_of(msg)) if msg.stop_reason == "end_turn" else None)


def main() -> int:
    report = fa.Report("Field Agents | S1-P1 Workbench")
    prompt = PROMPT.read_text(encoding="utf-8").strip() if PROMPT.exists() else ""
    report.check(bool(prompt), "Your prompt is exported to safehouse/p1/prompt.txt",
                 "In the Console Workbench, use Get code (or copy the system prompt) and save the system prompt "
                 "as safehouse/p1/prompt.txt. Only the system prompt: the grader sends each log line as the user message.")
    if not prompt:
        return report.finish(MISSION)
    try:
        client = fa_api.client()
    except fa_api.ApiKeyMissing as e:
        report.check(False, "ANTHROPIC_API_KEY is set", str(e))
        return report.finish(MISSION)

    import anthropic
    model = fa_api.model()
    usage = fa_api.Usage(model)
    cases = [json.loads(line) for line in HELDOUT.read_text().splitlines() if line.strip()]
    print(f"  Classifying {len(cases)} held-out lines with {model}...")
    try:
        with ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(lambda c: classify(client, model, prompt, c["line"]), cases))
    except anthropic.AuthenticationError:
        report.check(False, "Your API key works", "The API rejected ANTHROPIC_API_KEY. Check it in the Console.")
        return report.finish(MISSION)
    except anthropic.NotFoundError:
        report.check(False, f"Model {model} is available", "Unset FA_MODEL, or set it to a model your key can use.")
        return report.finish(MISSION)
    except anthropic.APIError as e:
        report.check(False, "The API answered every request", f"The API returned an error ({e.__class__.__name__}). "
                     "Try again in a minute; if it keeps failing, check your Console usage limits.")
        return report.finish(MISSION)

    for msg, _ in results:
        usage.add(msg.usage)
    invalid = sum(1 for _, data in results if data is None)
    right = sum(1 for (_, data), c in zip(results, cases) if data and data["label"] == c["label"])
    decoy_misses = sum(1 for (_, data), c in zip(results, cases)
                       if c["kind"] in ("crawler", "employee") and data and data["label"] == "attack")
    missed_attacks = sum(1 for (_, data), c in zip(results, cases)
                         if c["label"] == "attack" and data and data["label"] == "normal")

    report.check(invalid == 0, f"Every reply is valid JSON with a label and a reason ({len(cases) - invalid}/{len(cases)})",
                 'Every reply must be only a JSON object like {"label": "attack", "reason": "..."}, with label '
                 '"attack" or "normal". Say so in the prompt and show the format in your examples.')
    hint = []
    if decoy_misses:
        hint.append(f"{decoy_misses} harmless lines were called attacks: a 404 or a failed login isn't an attack on its own")
    if missed_attacks:
        hint.append(f"{missed_attacks} attack lines were called normal: what makes a request hostile, not just unusual?")
    report.check(right >= PASS_MARK, f"At least {PASS_MARK} of {len(cases)} labels are right ({right})",
                 " ".join(h + "." for h in hint) + " Add examples of both kinds to the prompt and compare versions "
                 "in the Workbench.")
    print(f"  Usage: {usage.summary()}")
    return report.finish(MISSION, "Workbench prompt holds up.")


if __name__ == "__main__":
    sys.exit(main())
