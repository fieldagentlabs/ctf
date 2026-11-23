#!/usr/bin/env python3
"""Grader for S1-K5 Catch Yourself.

Usage: control verify k5   (or: python3 grade.py [path/to/detections/])
Loads every Sigma rule in safehouse/k5/detections/*.yml with pySigma, replays a
labeled web log (a breach shaped like the canonical one, plus 50,000+ benign lines)
through pySigma's matcher, and scores each required behavior.

Log fields available to rules (logsource category: webserver):
  c-ip  cs-method  cs-uri-stem  cs-uri-query  sc-status (number)  sc-bytes (number)
  cs-referer  cs-user-agent  cs-body (request body, JSON escapes removed)
Base rules referenced by a correlation don't count on their own unless the
correlation sets `generate: true` (Sigma's rule).
"""
from __future__ import annotations

import gzip
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO / "platform" / "grader"))
import fa_grader as fa  # noqa: E402

MISSION = "S1-K5"
REPLAY = Path(__file__).resolve().parent / "replay"
BEHAVIORS = {  # label phase -> what players see
    "initial_access": "Login SQL injection",
    "collection": "UNION injection in search",
    "traversal": "Null byte or path traversal",
    "recon": "Wordlist scanning (404 bursts)",
}
NEEDED, MAX_FP = 0.90, 0.005
LINE = re.compile(r'^(\S+) - - \[([^\]]+)\] "(\S+) (\S+) HTTP/1\.1" (\d{3}) (\d+) "([^"]*)" "([^"]*)" "((?:[^"\\]|\\.)*)"$')


def load_events(Event, EventLogSource):
    lines = gzip.decompress((REPLAY / "access.log.gz").read_bytes()).decode().splitlines()
    labels = [json.loads(l) for l in gzip.decompress((REPLAY / "labels.jsonl.gz").read_bytes()).decode().splitlines()]
    events = []
    src = EventLogSource(category="webserver")
    for raw in lines:
        ip, ts, method, path, status, size, referer, ua, body = LINE.match(raw).groups()
        stem, _, query = path.partition("?")
        body = "" if body == "-" else body.replace('\\"', '"').replace("\\\\", "\\")
        data = {"c-ip": ip, "cs-method": method, "cs-uri-stem": stem, "cs-uri-query": query,
                "sc-status": int(status), "sc-bytes": int(size), "cs-referer": referer,
                "cs-user-agent": ua, "cs-body": body}
        events.append(Event(timestamp=datetime.strptime(ts, "%d/%b/%Y:%H:%M:%S %z"), logsource=src, data=data, raw=raw))
    return events, labels


def main() -> int:
    rules_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "safehouse" / "k5" / "detections"
    report = fa.Report("Field Agents | S1-K5 Catch Yourself")
    files = sorted(rules_dir.glob("*.yml")) + sorted(rules_dir.glob("*.yaml"))
    report.check(files, f"Sigma rules found in {rules_dir}", "Put your Sigma rules in safehouse/k5/detections/, one or more .yml files.")

    try:
        from sigma.collection import SigmaCollection
        from sigma.correlations import SigmaCorrelationRule
        from sigma.matching import Event, EventLogSource, SigmaMatcher
        from sigma.rule import SigmaRule
    except ImportError:
        report.check(False, "pySigma is installed", "Run this in the Season 1 Codespace, which has the pinned pySigma.")
        return report.finish(MISSION)

    errors = []
    for f in files:
        try:
            SigmaCollection.from_yaml(f.read_text(encoding="utf-8"))
        except Exception as e:  # pySigma raises its own error types
            errors.append(f"{f.name}: {str(e).splitlines()[0][:160]}")
    collection = None
    if files and not errors:
        try:
            collection = SigmaCollection.from_yaml("\n---\n".join(f.read_text(encoding="utf-8") for f in files))
        except Exception as e:
            errors.append(f"combined: {str(e).splitlines()[0][:160]}")
    report.check(files and not errors, "Every rule parses with pySigma",
                 "Fix: " + "; ".join(errors[:3]) if errors else "Add at least one rule.")
    if collection is None:
        return report.finish(MISSION)

    base = [r for r in collection.rules if isinstance(r, SigmaRule)]
    correlations = [r for r in collection.rules if isinstance(r, SigmaCorrelationRule)]
    wrong_source = [r.title for r in base if r.logsource.category != "webserver"]
    report.check(base and not wrong_source, "Every detection rule uses logsource category webserver",
                 f"Set `logsource: category: webserver` in: {', '.join(wrong_source[:3])}." if wrong_source else "Add a detection rule.")

    hidden = {ref.reference for c in correlations if not c.generate for ref in (c.rules or [])}
    events, labels = load_events(Event, EventLogSource)
    index = {id(e): i for i, e in enumerate(events)}
    flagged = set()
    with SigmaMatcher(collection, max_events_per_match=None) as matcher:
        for e in events:
            for m in matcher.match(e):
                if isinstance(m.rule, SigmaRule) and getattr(m.rule, "name", None) in hidden:
                    continue
                flagged.update(index[id(ev)] for ev in m.events)

    for phase, label in BEHAVIORS.items():
        want = [i for i, l in enumerate(labels) if l.get("phase") == phase and (phase != "recon" or events[i].data["sc-status"] == 404)]
        got = sum(1 for i in want if i in flagged)
        rate = got / len(want) if want else 0
        report.check(rate >= NEEDED, f"{label}: {got}/{len(want)} detected ({rate:.0%}, need 90%)",
                     f"Look at the attack lines for this behavior in your own logs (/var/log/shop/access.log) and ask "
                     f"Claude which fields and values set them apart from normal traffic.")

    normal = [i for i, l in enumerate(labels) if l["label"] == "normal"]
    fp = sum(1 for i in normal if i in flagged)
    report.check(fp / len(normal) <= MAX_FP, f"False positives: {fp} of {len(normal)} normal lines ({fp / len(normal):.2%}, max 0.5%)",
                 "Your rules flag too much normal traffic. Make the matches more specific.")
    decoys = Counter(labels[i].get("decoy") for i in flagged if labels[i].get("decoy"))
    report.check(not decoys.get("crawler"), "The SEO crawler (404-heavy, under the scanning threshold) isn't flagged",
                 f"{decoys.get('crawler', 0)} crawler lines flagged. A burst of 404s isn't an attack by itself: "
                 "tune the scanning rule's threshold and window.")
    report.check(not decoys.get("employee"), "The employee's mistyped logins aren't flagged",
                 f"{decoys.get('employee', 0)} employee lines flagged. Three failed logins then a success is a person, not an attack.")
    return report.finish(MISSION, "Detections tuned.")


if __name__ == "__main__":
    sys.exit(main())
