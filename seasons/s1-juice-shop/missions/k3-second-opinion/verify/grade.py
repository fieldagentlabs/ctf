#!/usr/bin/env python3
"""Grader for S1-K3 Second Opinion.

Usage: control verify k3   (or: python3 grade.py [path/to/triage.json])
Reads safehouse/k3/triage.json:

  {"findings": {"F-01": {"verdict": "true_positive", "reason": "..."}, ...},
   "patches":  {"P-01": {"verdict": "accept", "reason": "..."}, ...}}

Expected verdicts are stored as salted hashes, so this file doesn't give them away.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO / "platform" / "grader"))
import fa_grader as fa  # noqa: E402

MISSION = "S1-K3"
SALT = "fa-s1-k3"
FINDING_IDS = [f"F-{i:02d}" for i in range(1, 13)]
PATCH_IDS = ["P-01", "P-02"]
FINDINGS = {
    "14712c133c3852d2",
    "187356d73dc91566",
    "1e11930de209134f",
    "23eaabc5fdfb45f2",
    "43e821066d5da032",
    "45ce369a7535e55f",
    "5d8ba1f2216b73e5",
    "7c6a8539cecc8938",
    "92380c9bf6d521f6",
    "c3303daed01a87a7",
    "d1873c91348f52a9",
    "f4683db118120912",
}
PATCHES = {
    "aec52db8c2126d94",
    "d3d427102f67555d",
}
TP = {"true_positive", "true positive", "tp", "true", "confirmed", "valid", "real", "vulnerable"}
FP = {"false_positive", "false positive", "fp", "false", "refuted", "invalid", "not vulnerable", "not_vulnerable", "decoy"}
ACCEPT = {"accept", "accepted", "approve", "approved", "correct", "valid", "merge"}
REJECT = {"reject", "rejected", "deny", "denied", "incorrect", "invalid", "wrong", "block"}
BYPASS = re.compile(r"first|only one|once|single occurrence|global|/g\b|replaceall|all occurrences|second|multiple|"
                    r"more than one|repeated|backslash|still injectable|still vulnerable|bypass", re.I)


def h(s: str) -> str:
    return hashlib.sha256((SALT + "|" + s).encode()).hexdigest()[:16]


def norm(verdict: str, kind: str) -> str:
    v = re.sub(r"[-_]+", " ", str(verdict).strip().lower())
    v_ = v.replace(" ", "_")
    if kind == "finding":
        return "true_positive" if v in TP or v_ in TP else "false_positive" if v in FP or v_ in FP else v_
    return "accept" if v in ACCEPT else "reject" if v in REJECT else v_


def agent_files() -> list:
    dirs = [REPO / "safehouse" / ".claude" / "agents", Path(os.environ.get("JUICE_SHOP_SRC", "/workspaces/juice-shop")) / ".claude" / "agents",
            Path.home() / ".claude" / "agents"]
    found = []
    for d in dirs:
        for f in sorted(d.glob("*.md")) if d.is_dir() else []:
            head = f.read_text(encoding="utf-8")[:2000]
            if head.startswith("---") and re.search(r"(?m)^name:\s*\S", head) and re.search(r"(?m)^description:\s*\S", head):
                found.append(f)
    return found


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "safehouse" / "k3" / "triage.json"
    report = fa.Report("Field Agents | S1-K3 Second Opinion")
    report.check(path.exists(), f"triage.json found at {path}", "Write your verdicts to safehouse/k3/triage.json.")
    try:
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except json.JSONDecodeError as e:
        data = {}
        report.check(False, "triage.json is valid JSON", f"JSON error: {e}")
    f, p = data.get("findings", {}) or {}, data.get("patches", {}) or {}
    entries = [(i, f.get(i)) for i in FINDING_IDS] + [(i, p.get(i)) for i in PATCH_IDS]
    missing = [i for i, e in entries if not isinstance(e, dict) or not e.get("verdict") or not str(e.get("reason", "")).strip()]
    report.check(data and not missing, "Every finding and patch has a verdict and a reason",
                 f"Missing a verdict or reason: {', '.join(missing[:6])}." if missing else "Use the format in the mission page.")

    right_f = sum(1 for i in FINDING_IDS if isinstance(f.get(i), dict) and h(f"{i}|{norm(f[i].get('verdict'), 'finding')}") in FINDINGS)
    report.check(right_f == len(FINDING_IDS), f"Findings judged correctly: {right_f}/{len(FINDING_IDS)}",
                 f"{len(FINDING_IDS) - right_f} finding(s) misjudged. A scanner's confidence isn't evidence: have a subagent "
                 "read the code behind each claim and say what would actually make it exploitable.")
    right_p = sum(1 for i in PATCH_IDS if isinstance(p.get(i), dict) and h(f"{i}|{norm(p[i].get('verdict'), 'patch')}") in PATCHES)
    report.check(right_p == len(PATCH_IDS), f"Patches judged correctly: {right_p}/{len(PATCH_IDS)}",
                 "At least one patch verdict is wrong. Have a reviewer subagent apply each patch to a copy and test "
                 "whether the original attack still works.")
    p02 = p.get("P-02") if isinstance(p.get("P-02"), dict) else {}
    rejected = norm(p02.get("verdict", ""), "patch") == "reject"
    report.check(rejected and BYPASS.search(str(p02.get("reason", ""))), "P-02's verdict explains how it can still be bypassed",
                 "Don't just say P-02 is wrong: say why its escaping doesn't hold for every input. Have Claude "
                 "test the patched function on a few tricky inputs and explain what it sees.")

    agents = agent_files()
    report.check(agents, f"A subagent is defined in .claude/agents/ ({len(agents)} found)",
                 "Create a subagent (for example with /agents in Claude Code) under safehouse/.claude/agents/ or "
                 "/workspaces/juice-shop/.claude/agents/, with a name and description in its frontmatter.")
    return report.finish(MISSION, "Second opinion delivered.")


if __name__ == "__main__":
    sys.exit(main())
