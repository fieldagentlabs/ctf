#!/usr/bin/env python3
"""Grader for S1-K6 One Shot.

Usage:
  control verify k6 --start   restart Juice Shop (clears all solves) and open the run window
  claude -p "..." --output-format json > safehouse/k6/run.json     (one headless run)
  control verify k6           check the run

Checks: the run window was opened; a skill exists; run.json is a real headless
result made after the window opened; the five target challenges were solved inside
the window; total tokens are under the budget.
Env: SHOP_URL (default http://localhost:3000)
"""
from __future__ import annotations

import json
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO / "platform" / "grader"))
import fa_grader as fa  # noqa: E402

MISSION = "S1-K6"
WORK = REPO / "safehouse" / "k6"
WINDOW = WORK / ".run-window.json"
RUN = WORK / "run.json"
SKILLS = REPO / "safehouse" / ".claude" / "skills"
TARGETS = {  # challenge key -> name players see
    "loginAdminChallenge": "Login Admin",
    "adminSectionChallenge": "Admin Section",
    "directoryListingChallenge": "Confidential Document",
    "errorHandlingChallenge": "Error Handling",
    "zeroStarsChallenge": "Zero Stars",
}
# Total tokens (input + output + cache creation + cache reads, as reported in run.json).
# PLACEHOLDER until the reference run is measured: then set to 2x the reference total.
TOKEN_BUDGET = 3_000_000


def now() -> datetime:
    return datetime.now(timezone.utc)


def start() -> int:
    WORK.mkdir(parents=True, exist_ok=True)
    print("Restarting Juice Shop (this clears every solved challenge)...")
    if subprocess.run(["restart-shop"]).returncode != 0:
        print("restart-shop failed; is this the Season 1 Codespace?")
        return 1
    WINDOW.write_text(json.dumps({"started": now().isoformat()}) + "\n")
    RUN.unlink(missing_ok=True)
    print(f"\nRun window open. Now make ONE headless run, for example:\n"
          f"  cd {REPO / 'safehouse'} && claude -p \"<your prompt>\" --output-format json > k6/run.json\n"
          f"Then run: control verify k6\n")
    return 0


def challenge(key: str):
    url = f"{fa.shop_url().rstrip('/')}/api/Challenges/?{urllib.parse.urlencode({'key': key})}"
    with urllib.request.urlopen(url, timeout=10) as r:
        data = json.load(r).get("data", [])
    return data[0] if data else {}


def parse_time(s: str):
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None


def total_tokens(usage: dict) -> int:
    fields = ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
    return sum(int(usage.get(f) or 0) for f in fields)


def main() -> int:
    if "--start" in sys.argv[1:]:
        return start()
    report = fa.Report("Field Agents | S1-K6 One Shot")

    window = json.loads(WINDOW.read_text()) if WINDOW.exists() else {}
    started = parse_time(window.get("started", ""))
    report.check(started, "Run window opened with `control verify k6 --start`",
                 "Run `control verify k6 --start` first. It resets the shop so the run starts clean.")

    skills = [p for p in SKILLS.glob("*/SKILL.md")
              if p.read_text(encoding="utf-8").startswith("---") and "name:" in p.read_text(encoding="utf-8")[:500]]
    report.check(skills, f"A skill exists in safehouse/.claude/skills/ ({', '.join(p.parent.name for p in skills) or 'none'})",
                 "Write your skill at safehouse/.claude/skills/shop-recon/SKILL.md, with name and description in its frontmatter.")

    try:
        run = json.loads(RUN.read_text(encoding="utf-8")) if RUN.exists() else {}
    except json.JSONDecodeError:
        run = {}
    is_result = run.get("type") == "result" and isinstance(run.get("usage"), dict) and run.get("num_turns")
    report.check(is_result and not run.get("is_error"), "safehouse/k6/run.json is a completed headless run",
                 "Save the output of `claude -p \"...\" --output-format json` to safehouse/k6/run.json (one run, not edited).")
    made = datetime.fromtimestamp(RUN.stat().st_mtime, timezone.utc) if RUN.exists() else None
    report.check(started and made and made >= started, "The run happened after the window opened",
                 "run.json is older than your last --start. Start again, then make one run.")

    solved, outside = [], []
    try:
        for key, name in TARGETS.items():
            c = challenge(key)
            if c.get("solved"):
                solved.append(name)
                when = parse_time(c.get("updatedAt", ""))
                # run.json's mtime is when the run finished writing; allow a few seconds of clock slack.
                if not (started and made and when and started <= when <= made + timedelta(seconds=5)):
                    outside.append(name)
        reachable = True
    except Exception:
        reachable = False
    missing = [n for n in TARGETS.values() if n not in solved]
    report.check(reachable and not missing, f"All five targets solved ({len(solved)}/5)",
                 f"Not solved: {', '.join(missing)}. Make your skill check each challenge's status in /api/Challenges "
                 "before it stops." if reachable else "Can't reach Juice Shop. Is it running?")
    report.check(reachable and solved and not outside, "Every solve happened during the run",
                 f"Solved outside the run window: {', '.join(outside)}. Solves must come from the one headless run: "
                 "--start again, then run once." if outside else "Nothing solved yet.")

    tokens = total_tokens(run.get("usage", {})) if is_result else 0
    report.check(is_result and tokens <= TOKEN_BUDGET, f"Tokens: {tokens:,} of {TOKEN_BUDGET:,} budget",
                 "Over budget. Tighten the skill: tell the agent exactly what to check and when to stop, and avoid "
                 "reading large files it doesn't need.")
    return report.finish(MISSION, "One shot, five hits.")


if __name__ == "__main__":
    sys.exit(main())
