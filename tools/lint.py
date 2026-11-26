#!/usr/bin/env python3
"""Repo lint for the public Field Agents repo. Stdlib only.

Checks every tracked text file for: long dashes, real-looking flags, and
keys or tokens. Fails if a mission.md appears: briefs live in the private repo and reach
players only through the Field Agents site.
Usage: python3 tools/lint.py   (exits 1 on any problem)
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "platform" / "grader"))
import fa_grader as fa  # noqa: E402

DASHES = re.compile("[" + chr(0x2013) + chr(0x2014) + "]")  # en and em dash
REAL_FLAG = re.compile(r"FA\{s\d+_[a-z0-9]+_[0-9a-f]{12}\}", re.I)
BINARY = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".gz", ".zip", ".ico", ".woff", ".woff2"}
SKIP = {"platform/grader/tests/test_fa_grader.py"}  # holds fake secrets on purpose


KEY_PLACEHOLDER = re.compile(r"CTF_KEY\s*=\s*[\"']?(\$\S*|[A-Za-z0-9_-]{1,19}[\"']?)\s*\\?$")


def real_secrets(line: str) -> list:
    """Like fa.find_secrets, but a CTF_KEY set to a $VARIABLE or a short dummy is fine in repo files."""
    return [s for s in fa.find_secrets(line) if not KEY_PLACEHOLDER.fullmatch(s)]


# Chat missions (F1, C1 to C6) happen in claude.ai, not the Codespace: their files are CTFd attachments.
CHAT_MISSION = re.compile(r"seasons/[^/]+/missions/(f1|c\d+)-")


def tracked_files() -> list:
    out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [p for p in out.split("\0") if p]


def main() -> int:
    problems = []
    for rel in tracked_files():
        path = ROOT / rel
        if CHAT_MISSION.match(rel):
            problems.append(f"{rel}: chat-mission files are CTFd attachments (kept in ctf-hq), not here")
        if path.suffix.lower() in BINARY or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for n, line in enumerate(text.splitlines(), 1):
            if DASHES.search(line):
                problems.append(f"{rel}:{n}: long dash (use a comma, colon, parentheses, or a new sentence)")
            if REAL_FLAG.search(line):
                problems.append(f"{rel}:{n}: looks like a real flag")
            if rel not in SKIP and real_secrets(line):
                problems.append(f"{rel}:{n}: looks like a key or token")
        if path.name == "mission.md":
            problems.append(f"{rel}: mission briefs belong in ctf-hq (players read them on the site), not here")

    for p in problems:
        print(p)
    print(f"lint: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
