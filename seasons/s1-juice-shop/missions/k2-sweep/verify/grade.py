#!/usr/bin/env python3
"""Grader for S1-K2 Sweep.

Usage: control verify k2   (or: python3 grade.py [path/to/findings.md])
Reads a markdown table with columns for file, line range, CWE, and challenge key
(any order, any extra columns). Rows with no challenge key count as "valid but
unmapped": real issues, not scored.

The answer table is stored as salted hashes so this file doesn't hand it out.
"""
from __future__ import annotations

import hashlib
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO / "platform" / "grader"))
import fa_grader as fa  # noqa: E402

MISSION = "S1-K2"
SALT = "fa-s1-k2"
NEEDED = 10
PAIRS = {
    "03bbbaf83a11d7de",
    "0624f21168ce4b03",
    "1bafb6709b9a09c5",
    "26f364766f852f93",
    "2c551ee408f0bd44",
    "32b8a8f2b51b7fef",
    "40cbc4e346bc191a",
    "426229ce68151445",
    "4b65b4c30dd7b1cf",
    "4dcf285f2ff0b4bc",
    "54d03df4b65c2f20",
    "631d0abf27868dd6",
    "6654d5b2511e3279",
    "77308e88823bde07",
    "8b491a18165dcc7d",
    "9377e179cc2acfe1",
    "9e4fa8554e92a685",
    "a6c9ed2a29f9c9ec",
    "b7ab08afd4dbf412",
    "b9680b1da9798afa",
    "d2985ee100579100",
    "f60bc20c8bbe8907",
}
CWES = {
    "04adeb26209c6b6a",
    "0577ab805baac806",
    "13db58405bb717c7",
    "13f44f29bede0f01",
    "1b2e76dc661aaf6d",
    "289e4b08ccc16635",
    "29b921cff029720b",
    "3188e9f1fd1731ab",
    "3504c6b1c7829d0a",
    "365ef826cb549621",
    "3806ec7e3ea6f485",
    "3c1bdd7424388769",
    "443c0ac786941497",
    "523480b165562ba3",
    "5d17610b9a77390c",
    "6a37d5cdf1aeb61b",
    "741a56ac767c8c96",
    "77785f4ea3c9c9fd",
    "8ab8dd4ff3c7d297",
    "8af6b931093da54c",
    "93b87826b7ccbd0a",
    "9dfef57f38128d19",
    "a9b87c6d06aec2b8",
    "b92dd2b58a667f0d",
    "c155f59df3f54f05",
    "c2744551cc5d5b42",
    "c879041d5da39712",
    "d32146418dd3e444",
    "d4b6e9e994db070c",
    "db840ad23d45ceb4",
    "dc58f24081f5965f",
    "dec80ce840502188",
    "f438b98c11819711",
    "f5864fbe04e045fd",
    "f6e00aca33d01593",
    "fd5565f370f7be59",
    "fdde3270e0dccee4",
    "fe9692c4845b3514",
}
KEYS = {
    "0709bd1229c0034e",
    "0a476dc9e68f7b74",
    "0ba882a4a584711a",
    "17d8497922052e6f",
    "24c8ed10f30b2812",
    "28cb19be964d2d3b",
    "2ce61353f440aa0a",
    "422952ae1549295f",
    "655a08445525014f",
    "906bff7b66e0fb8e",
    "948d16b0ccabd7f4",
    "9a538578d4defbbf",
    "9d23ba2df8d8cc6f",
    "a509447ec4f983bb",
    "b5fbde5742941e1a",
    "d09fcf10ea20ac18",
    "e64ec88d0ec5d151",
    "f81ada78a48fff26",
}


def h(s: str) -> str:
    return hashlib.sha256((SALT + "|" + s).encode()).hexdigest()[:16]


def norm_file(cell: str) -> str:
    f = re.sub(r"[`*]", "", cell).strip().split()[0] if cell.strip() else ""
    f = re.sub(r"^(\./|/?workspaces/juice-shop/|juice-shop/)", "", f.lstrip("/"))
    return re.sub(r"[:#].*$", "", f)  # drop "file.ts:12" or "file.ts#L12"


def norm_cwe(cell: str) -> str:
    m = re.search(r"(\d{1,4})", cell)
    return f"CWE-{int(m.group(1))}" if m else ""


def norm_key(cell: str) -> str:
    k = re.sub(r"[`*]", "", cell).strip()
    return "" if k.lower() in ("", "-", "none", "n/a", "na", "unmapped") else k


def read_table(text: str):
    """Return (rows, problem). Each row is a dict with file, lines, cwe, key."""
    lines = [ln for ln in text.splitlines() if ln.strip().startswith("|")]
    for i, ln in enumerate(lines[:-1]):
        head = [c.strip().lower() for c in ln.strip().strip("|").split("|")]
        if not re.match(r"^\|?\s*:?-{3,}", lines[i + 1].strip()):
            continue
        col = {}
        for j, c in enumerate(head):
            if "file" in c and "file" not in col:
                col["file"] = j
            elif "line" in c and "lines" not in col:
                col["lines"] = j
            elif "cwe" in c and "cwe" not in col:
                col["cwe"] = j
            elif ("challenge" in c or c == "key") and "key" not in col:
                col["key"] = j
        if set(col) != {"file", "lines", "cwe", "key"}:
            continue
        rows = []
        for ln2 in lines[i + 2:]:
            cells = [c.strip() for c in ln2.strip().strip("|").split("|")]
            if len(cells) < len(head):
                break
            rows.append({k: cells[j] for k, j in col.items()})
        return rows, None
    return [], "No table with File, Lines, CWE, and Challenge key columns (and a --- separator row)."


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "safehouse" / "k2" / "findings.md"
    report = fa.Report("Field Agents | S1-K2 Sweep")
    report.check(path.exists(), f"findings.md found at {path}",
                 "Write your findings table to safehouse/k2/findings.md.")
    rows, problem = read_table(path.read_text(encoding="utf-8")) if path.exists() else ([], "missing file")
    report.check(not problem, "Findings table has File, Lines, CWE, and Challenge key columns",
                 "Use a markdown table: | File | Lines | CWE | Challenge key |, one finding per row.")

    keyed = [r for r in rows if norm_key(r["key"])]
    mapped = [r for r in keyed if h(norm_key(r["key"])) in KEYS]          # challenges this mission scores
    unmapped = [r for r in rows if r not in mapped]                         # no key, or a challenge not scored here
    keys = [norm_key(r["key"]) for r in mapped]

    report.check(len(set(keys)) >= NEEDED, f"At least {NEEDED} findings mapped to distinct scored challenges ({len(set(keys))} found)",
                 "Map more findings to the Juice Shop challenge they enable, using the exact key from "
                 "data/static/challenges.yml (for example someNameChallenge). Findings shown as unmapped don't count.")
    wrong_file = [f"{norm_file(r['file'])} -> {norm_key(r['key'])}" for r in mapped
                  if h(f"{norm_file(r['file'])}|{norm_key(r['key'])}") not in PAIRS]
    report.check(mapped and not wrong_file, "Every mapped finding points at the file with the vulnerable code",
                 f"Check these files: {'; '.join(wrong_file[:5])}. Paths are relative to the Juice Shop root, like routes/x.ts."
                 if wrong_file else "Add file paths to your findings.")
    dupes = sorted({k for k in keys if keys.count(k) > 1})
    report.check(not dupes, "No challenge key used twice",
                 f"Used more than once: {', '.join(dupes)}. One row per challenge.")
    bad_cwe = [f"{norm_key(r['key'])} ({norm_cwe(r['cwe']) or 'no CWE'})" for r in mapped
               if h(f"{norm_key(r['key'])}|{norm_cwe(r['cwe'])}") not in CWES]
    report.check(mapped and not bad_cwe, "Every CWE fits the weakness behind its challenge",
                 f"Rethink: {', '.join(bad_cwe[:5])}. Ask Claude which CWE describes the root cause, then check cwe.mitre.org."
                 if bad_cwe else "Add CWE IDs to your findings.")
    bad_lines = [norm_file(r["file"]) for r in rows if not re.match(r"^\s*L?\d+(\s*[-:]\s*L?\d+)?\s*$", r["lines"])]
    report.check(rows and not bad_lines, "Every finding has a line or line range",
                 f"Give lines as 42 or 42-57 for: {', '.join(bad_lines[:5])}.")

    if unmapped:
        print("\nValid but unmapped (real issues, not scored here):")
        for r in unmapped:
            key = norm_key(r["key"])
            print(f"  - {norm_file(r['file'])} {r['lines']} {norm_cwe(r['cwe'])}" + (f" ({key})" if key else ""))
    return report.finish(MISSION, "Sweep complete.")


if __name__ == "__main__":
    sys.exit(main())
