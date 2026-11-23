#!/usr/bin/env python3
"""Grader for S1-P3 Desk Officer.

Usage: control verify p3
Env:   ANTHROPIC_API_KEY (your own key; required), FA_MODEL (passed through to your script)

Asks your assistant (safehouse/p3/ask.py) 10 questions about the breach, one at a time:
    python3 safehouse/p3/ask.py "<question>"
The last line your script prints must be JSON:
    {"answer": "...", "tool_calls": [{"name": "search_logs", "input": {...}}, ...]}
At least 9 answers must be right, and every right answer must be backed by at least one
call to search_logs, count_events, or get_timeline. Answers are checked against salted
hashes, so this file doesn't give them away.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO / "platform" / "grader"))
import fa_api  # noqa: E402
import fa_grader as fa  # noqa: E402

MISSION = "S1-P3"
ASK = REPO / "safehouse" / "p3" / "ask.py"
LOG = REPO / "seasons/s1-juice-shop/missions/c1-morning-briefing/data/access.log.gz"
TOOLS = {"search_logs", "count_events", "get_timeline"}
SALT = "fa-s1-p3"
PASS_MARK = 9
MAX_ANSWER = 400
YES = re.compile(r"\b(yes|malicious|hostile|the attacker)\b", re.I)
NO = re.compile(r"\b(no|not (an? )?(attack|malicious)|benign|legitimate|harmless|innocent)\b", re.I)
# (question, kind of value to look for, salted hash of the right value, extra check)
QUESTIONS = [
    ("Which IP address compromised the shop?", "ip", "acc13a4495441630", None),
    ("At what time (UTC, HH:MM:SS) did the attacker first get in successfully?", "time", "b364f22f1acafbd1", None),
    ("How many failed logins did the attacker make before the successful exploit?", "int", "1d58646be146ce16", None),
    ("Which file did the attacker read from /ftp?", "file", "5e7d2d9c066278e5", None),
    ("Which endpoint leaked the Users table through SQL injection?", "path", "a4b57e9321e157ff", None),
    ("Which IP address had the most 404 responses, and was it malicious?", "ip", "acc13a4495441630", YES),
    ("How many requests did the attacker's IP make in total?", "int", "ea006764cf01c31c", None),
    ("Which account email did the attacker try to brute force?", "email", "8414cf4863c96c52", None),
    ("How many bytes did the attacker's final bulk download of user records return?", "int", "b07e4c8293c5eeb6", None),
    ("Which staff account had failed logins on the morning of 14 October, and was that an attack?", "email",
     "930edca8a27f52b7", NO),
]
EXTRACT = {
    "ip": lambda t: re.findall(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", t),
    "time": lambda t: re.findall(r"\b\d{2}:\d{2}:\d{2}\b", t),
    "int": lambda t: [m.replace(",", "") for m in re.findall(r"(?<![\w.:/-])\d{1,3}(?:,\d{3})+(?![\w.])|(?<![\w.:/-])\d+(?![\w.:])", t)],
    "file": lambda t: [m.lower() for m in re.findall(r"\b[\w-]+\.[A-Za-z]{1,5}\b", t)],
    "path": lambda t: [m.split("?")[0].rstrip("/.,;:") for m in re.findall(r"/[\w./?=-]+", t)],
    "email": lambda t: [m.lower() for m in re.findall(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", t)],
}


def hashed(kind: str, value: str) -> str:
    return hashlib.sha256(f"{SALT}:{kind}:{value}".encode()).hexdigest()[:16]


def ask(question: str):
    try:
        r = subprocess.run([sys.executable, str(ASK), question], capture_output=True, text=True, timeout=300,
                           cwd=ASK.parent, env={**os.environ, "FA_LOG": str(LOG)})
    except subprocess.TimeoutExpired:
        return None, "timed out after 300 s"
    for line in reversed(r.stdout.strip().splitlines()):
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and isinstance(data.get("answer"), str) and isinstance(data.get("tool_calls"), list):
            return data, ""
    return None, (r.stderr.strip().splitlines() or ["no JSON on the last line"])[-1][:200]


def main() -> int:
    report = fa.Report("Field Agents | S1-P3 Desk Officer")
    report.check(ASK.exists(), "safehouse/p3/ask.py exists",
                 'Write safehouse/p3/ask.py: it takes a question as its argument and prints one JSON line, '
                 '{"answer": ..., "tool_calls": [...]}, last.')
    if not ASK.exists():
        return report.finish(MISSION)
    try:
        fa_api.client()
    except fa_api.ApiKeyMissing as e:
        report.check(False, "ANTHROPIC_API_KEY is set", str(e))
        return report.finish(MISSION)

    print(f"  Asking {len(QUESTIONS)} questions (up to 5 minutes each, 3 at a time)...")
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(lambda q: ask(q[0]), QUESTIONS))

    right, unbacked, broken = 0, 0, 0
    for (question, kind, want, extra), (data, err) in zip(QUESTIONS, results):
        if data is None:
            broken += 1
            print(f"  ?     {question}\n        no answer: {err}")
            continue
        answer = data["answer"].strip()
        used = [c.get("name") for c in data["tool_calls"] if isinstance(c, dict)]
        backed = any(name in TOOLS for name in used)
        correct = (len(answer) <= MAX_ANSWER and any(hashed(kind, v) == want for v in EXTRACT[kind](answer))
                   and (extra is None or bool(extra.search(answer))))
        right += correct and backed
        unbacked += correct and not backed
        mark = "ok" if correct and backed else ("no tools" if correct else "wrong")
        print(f"  {mark:<6}{question}\n        {answer[:160]}  [tools: {', '.join(used) or 'none'}]")

    report.check(broken == 0, f"Your script answered every question ({len(QUESTIONS) - broken}/{len(QUESTIONS)})",
                 "Some runs crashed, timed out, or didn't end with the JSON line. Run python3 safehouse/p3/ask.py "
                 '"Which IP address compromised the shop?" yourself and check the last line.')
    report.check(right >= PASS_MARK, f"At least {PASS_MARK} answers are right and backed by a tool call ({right})",
                 (f"{unbacked} right answers had no tool call in tool_calls; the answer must come from the logs, "
                  "not memory. " if unbacked else "")
                 + f"Keep answers short and specific (an IP, a time, a count; under {MAX_ANSWER} characters), and start "
                   "yes/no verdicts with Yes or No. If an answer is wrong, look at what "
                   "your tools returned: give Claude counts and timelines, not just matching lines.")
    return report.finish(MISSION, "Desk officer on duty.")


if __name__ == "__main__":
    sys.exit(main())
