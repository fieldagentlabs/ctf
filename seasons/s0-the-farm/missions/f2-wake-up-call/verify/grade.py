#!/usr/bin/env python3
"""Grader for S0-F2 Wake Up Call.

Usage: control verify f2   (or: python3 grade.py [path/to/CLAUDE.md])
Default path: safehouse/CLAUDE.md at the repo root, from any working directory.
Env:   CTF_KEY (set in the Codespace), SHOP_URL (default http://localhost:3000)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO / "platform" / "grader"))
import fa_grader as fa  # noqa: E402

MISSION = "S0-F2"
TARGETS = ("shop.fieldagents.test", "localhost:3000")
REQUIRED = {
    "identity": ("identity", "who you are", "role"),
    "mission": ("mission", "objective", "objectives"),
    "scope": ("scope", "in scope", "targets"),
    "rules of engagement": ("rules of engagement", "rules", "roe", "guardrails"),
    "reporting": ("reporting", "report", "output", "deliverables"),
}


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "safehouse" / "CLAUDE.md"
    report = fa.Report("Field Agents | S0-F2 Wake Up Call")

    report.check(path.exists(), f"CLAUDE.md found at {path}", "cd safehouse, run claude, then /init, and shape the file into your agent's standing orders.")
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    secs = fa.sections(text)

    found = {name: fa.find_section(secs, aliases) for name, aliases in REQUIRED.items()}
    for name, body in found.items():
        report.check(body is not None and body.strip(), f"Section: {name.title()}",
                     f"Add a '## {name.title()}' section (two #s) with real content.")

    scope = found["scope"] or ""
    report.check(any(t in scope for t in TARGETS), "Scope names the target (shop.fieldagents.test or localhost:3000)",
                 "Tell your agent exactly which host it may touch.")
    report.check(re.search(r"out of scope|out-of-scope|off limits|off-limits|never touch|do not (touch|access|scan)|only\b", scope, re.I),
                 "Scope says what is off limits", "An agent needs to know where the fence is, not just the target.")

    roe = found["rules of engagement"] or ""
    rules = fa.bullets(roe)
    report.check(len(rules) >= 3, f"At least 3 rules of engagement ({len(rules)} found)", "List them as bullets.")
    report.check(re.search(r"\b(never|do not|don't|must not)\b", roe, re.I),
                 "Rules include at least one hard 'never'", "Example: never run destructive commands or touch real systems.")

    lines = len(text.splitlines())
    report.check(0 < lines <= 200, f"Concise: {lines} lines (200 max)", "CLAUDE.md loads every session. Keep it tight.")
    report.check(not fa.find_secrets(text), "No secrets in CLAUDE.md",
                 "Never put keys or tokens in agent memory. Use environment variables.")

    report.check_solved("scoreBoardChallenge", "Juice Shop Score Board challenge solved",
                        "Find the hidden score board in the shop. Your agent can help you look. "
                        "Restarting Juice Shop clears solves, so solve it again if you restarted.")

    return report.finish(MISSION, "Agent awake and briefed.")


if __name__ == "__main__":
    sys.exit(main())
