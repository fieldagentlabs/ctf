#!/usr/bin/env python3
"""Grader for S0-F2 Wake Up Call.

Usage: ctf verify f2   (or: python3 grade.py [path/to/CLAUDE.md])
Env:   CTF_KEY (set in the Codespace), SHOP_URL (default http://localhost:3000)
"""
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[5] / "platform" / "grader"))
import fa_grader as fa  # noqa: E402

MISSION = "S0-F2"
SHOP_URL = os.environ.get("SHOP_URL", "http://localhost:3000")
TARGETS = ("shop.fieldagents.test", "localhost:3000")
REQUIRED = {
    "identity": ("identity", "who you are", "role"),
    "mission": ("mission", "objective"),
    "scope": ("scope", "in scope", "targets"),
    "rules of engagement": ("rules of engagement", "rules", "roe", "guardrails"),
    "reporting": ("reporting", "report", "output", "deliverables"),
}
SECRET_PATTERNS = (r"sk-ant-[A-Za-z0-9_-]{10,}", r"ghp_[A-Za-z0-9]{20,}", r"CTF_KEY\s*=\s*\S+")


def find_section(secs: dict, aliases) -> str | None:
    for heading, body in secs.items():
        if any(alias in heading for alias in aliases):
            return body
    return None


def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "CLAUDE.md")
    report = fa.Report("Field Agents | S0-F2 Wake Up Call")

    report.check(path.exists(), f"CLAUDE.md found at {path}", "Run /init in Claude Code, then shape the file into your agent's standing orders.")
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    secs = fa.sections(text)

    found = {name: find_section(secs, aliases) for name, aliases in REQUIRED.items()}
    for name, body in found.items():
        report.check(body is not None and body.strip(), f"Section: {name.title()}", f"Add a '## {name.title()}' section with real content.")

    scope = found["scope"] or ""
    report.check(any(t in scope for t in TARGETS), "Scope names the target (shop.fieldagents.test or localhost:3000)",
                 "Tell your agent exactly which host it may touch.")
    report.check(re.search(r"out of scope|out-of-scope|never touch|do not (touch|access|scan)|only\b", scope, re.I),
                 "Scope says what is off limits", "An agent needs to know where the fence is, not just the target.")

    roe = found["rules of engagement"] or ""
    rules = [ln for ln in roe.splitlines() if re.match(r"^\s*([-*]|\d+\.)\s+\S", ln)]
    report.check(len(rules) >= 3, f"At least 3 rules of engagement ({len(rules)} found)", "List them as bullets.")
    report.check(re.search(r"\b(never|do not|don't|must not)\b", roe, re.I),
                 "Rules include at least one hard 'never'", "Example: never run destructive commands or touch real systems.")

    lines = len(text.splitlines())
    report.check(0 < lines <= 200, f"Concise: {lines} lines (200 max)", "CLAUDE.md loads every session. Keep it tight.")
    report.check(not any(re.search(p, text) for p in SECRET_PATTERNS), "No secrets in CLAUDE.md",
                 "Never put keys or tokens in agent memory. Use environment variables.")

    report.check(fa.juice_shop_solved("scoreBoardChallenge", SHOP_URL), "Juice Shop Score Board challenge solved",
                 "Find the hidden score board in the shop. Your agent can help you look.")

    report.print()
    if report.passed():
        print(f"{fa.GREEN}Agent awake and briefed. Flag: {fa.mission_flag(MISSION)}{fa.RESET}\n")
        return 0
    print("Not yet. Fix the failures above and run the grader again.\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
