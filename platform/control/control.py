#!/usr/bin/env python3
"""control: the Field Agents player CLI. Stdlib only, Python 3.9+.

Usage:
  control verify <mission> [grader args...]   e.g. control verify f2

<mission> is the id from the mission folder name (f2, c1, k4, ...), or the
full id (S0-F2). Extra arguments go straight to that mission's grader.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def missions(root: Path = REPO) -> dict:
    """Map short mission id (f2) to its grader path, for every mission with a grader."""
    out = {}
    for grader in sorted(root.glob("seasons/*/missions/*/verify/grade.py")):
        short = grader.parents[1].name.split("-", 1)[0].lower()
        out[short] = grader
    return out


def resolve(mission: str, root: Path = REPO) -> Path | None:
    short = re.sub(r"^s\d+-", "", mission.strip().lower())
    return missions(root).get(short)


def verify(mission: str, args: list, root: Path = REPO) -> int:
    grader = resolve(mission, root)
    if grader is None:
        known = ", ".join(missions(root)) or "none yet"
        print(f"control: no mission called '{mission}'. Missions with graders: {known}", file=sys.stderr)
        return 2
    return subprocess.call([sys.executable, str(grader), *args])


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(prog="control", description="Field Agents player CLI.")
    sub = parser.add_subparsers(dest="command", required=True)
    v = sub.add_parser("verify", help="run a mission's grader, e.g. control verify f2")
    v.add_argument("mission", help="mission id, e.g. f2")
    v.add_argument("args", nargs=argparse.REMAINDER, help="passed to the grader")
    ns = parser.parse_args(argv)
    return verify(ns.mission, ns.args)


if __name__ == "__main__":
    sys.exit(main())
