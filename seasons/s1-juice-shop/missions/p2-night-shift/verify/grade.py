#!/usr/bin/env python3
"""Grader for S1-P2 Night Shift.

Usage: control verify p2
Env:   ANTHROPIC_API_KEY (your own key; required: the batch must belong to your account)

Reads your batch ID from safehouse/p2/batch_id.txt, fetches the batch and its results
with your key, and grades the batch itself: 5,000 succeeded requests (one per event,
custom_id = event id), cache reads above zero, F1 of at least 0.90 on the attack class,
and an estimated cost under the budget. safehouse/p2/labels.jsonl must match the results.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO / "platform" / "grader"))
import fa_api  # noqa: E402
import fa_grader as fa  # noqa: E402

MISSION = "S1-P2"
WORK = REPO / "safehouse" / "p2"
LABELS = Path(__file__).with_name("labels.jsonl")
F1_MARK = 0.90
BUDGET_USD = 0.28  # 1.5x the reference run ($0.1816 on Nov 23, 2026), rounded up to the cent
FENCE = re.compile(r"^```(?:json)?\s*(.*?)\s*```$", re.S)


def label_of(text: str):
    text = text.strip()
    m = FENCE.match(text)
    if m:
        text = m.group(1)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    return data.get("label") if isinstance(data, dict) and data.get("label") in ("attack", "normal") else None


def main() -> int:
    report = fa.Report("Field Agents | S1-P2 Night Shift")
    id_file = WORK / "batch_id.txt"
    batch_id = id_file.read_text().strip() if id_file.exists() else ""
    report.check(batch_id.startswith("msgbatch_"), "safehouse/p2/batch_id.txt holds a Message Batch ID",
                 "Save the ID that messages.batches.create returns (it starts with msgbatch_) to safehouse/p2/batch_id.txt.")
    if not batch_id.startswith("msgbatch_"):
        return report.finish(MISSION)
    try:
        client = fa_api.client()
    except fa_api.ApiKeyMissing as e:
        report.check(False, "ANTHROPIC_API_KEY is set", str(e))
        return report.finish(MISSION)

    import anthropic
    try:
        batch = client.messages.batches.retrieve(batch_id)
    except anthropic.NotFoundError:
        report.check(False, "The batch belongs to your account",
                     "Your key can't see that batch. Use the key you created it with, and check the ID.")
        return report.finish(MISSION)
    except anthropic.APIError as e:
        report.check(False, "The API answered", f"The API returned {e.__class__.__name__}. Check your key and try again.")
        return report.finish(MISSION)
    report.check(batch.processing_status == "ended", f"The batch has finished ({batch.processing_status})",
                 "Batches usually finish within an hour. Poll messages.batches.retrieve until processing_status is ended.")
    if batch.processing_status != "ended":
        return report.finish(MISSION)

    truth = {r["id"]: r["label"] for r in map(json.loads, LABELS.read_text().splitlines()) if r}
    predicted, usage_by_model, ok = {}, {}, 0
    print(f"  Downloading {batch.request_counts.succeeded:,} results...")
    for item in client.messages.batches.results(batch_id):
        if item.result.type != "succeeded" or item.custom_id not in truth:
            continue
        ok += 1
        msg = item.result.message
        usage_by_model.setdefault(msg.model, fa_api.Usage(msg.model)).add(msg.usage)
        predicted[item.custom_id] = label_of(fa_api.text_of(msg))

    report.check(ok == len(truth) and len(predicted) == len(truth),
                 f"One succeeded request per event ({len(predicted):,} of {len(truth):,})",
                 "Send every event in data/events.jsonl as its own request in one batch, with custom_id set to the "
                 "event's id. Check request_counts for errored or expired requests.")
    cache_reads = sum(u.totals["cache_read_input_tokens"] for u in usage_by_model.values())
    report.check(cache_reads > 0, f"Prompt caching worked ({cache_reads:,} cache read tokens)",
                 "No request read from the cache. Put the long, unchanging guide in the system prompt with "
                 "cache_control, keep it byte-for-byte identical in every request, and make it long enough to cache. "
                 "In a batch, a 1-hour cache (ttl 1h) gets more hits.")

    tp = sum(1 for k, v in truth.items() if v == "attack" and predicted.get(k) == "attack")
    fp = sum(1 for k, v in truth.items() if v == "normal" and predicted.get(k) == "attack")
    fn = sum(1 for k, v in truth.items() if v == "attack" and predicted.get(k) != "attack")
    f1 = 2 * tp / (2 * tp + fp + fn) if tp else 0.0
    unparsed = sum(1 for v in predicted.values() if v is None)
    report.check(f1 >= F1_MARK, f"F1 on the attack class is at least {F1_MARK:.2f} ({f1:.3f})",
                 f"{fp} normal events labeled attack, {fn} attacks missed"
                 + (f", {unparsed} replies weren't valid JSON" if unparsed else "")
                 + ". Tune the prompt on a small sample with the Messages API before you spend a batch on it.")

    costs = [u.cost(batch=True) for u in usage_by_model.values()]
    known = all(c is not None for c in costs) and costs
    total = sum(costs) if known else None
    for u in usage_by_model.values():
        print(f"  Usage: {u.summary(batch=True)}")
    report.check(bool(known) and total <= BUDGET_USD,
                 f"Estimated cost is under the ${BUDGET_USD:.2f} budget"
                 + (f" (${total:.4f})" if total is not None else ""),
                 "The grader only knows prices for " + ", ".join(fa_api.PRICES) + "." if not known else
                 "Too expensive. Use a small model, keep replies short, and make sure the guide is read from the cache.")

    labels_file = WORK / "labels.jsonl"
    mine = {}
    if labels_file.exists():
        for line in labels_file.read_text().splitlines():
            try:
                row = json.loads(line)
                mine[row["id"]] = row["label"]
            except (json.JSONDecodeError, KeyError, TypeError):
                pass
    agree = sum(1 for k, v in predicted.items() if v and mine.get(k) == v)
    usable = sum(1 for v in predicted.values() if v)
    report.check(usable and agree == usable, f"safehouse/p2/labels.jsonl matches the batch results ({agree:,}/{usable:,})",
                 'Write one line per event: {"id": "e00001", "label": "attack"}, taken from the batch results.')
    return report.finish(MISSION, "Night shift covered.")


if __name__ == "__main__":
    sys.exit(main())
