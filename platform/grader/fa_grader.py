"""Field Agents grader toolkit (shared by every mission).

Stdlib only, so graders run in any Codespace without installs.
Supports Python 3.9 and newer.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import sys
import urllib.parse
import urllib.request

GREEN, RED, DIM, RESET = "\033[32m", "\033[31m", "\033[2m", "\033[0m"
DEFAULT_SHOP_URL = "http://localhost:3000"
SECRET_PATTERNS = (
    r"sk-ant-[A-Za-z0-9_-]{10,}",
    r"ghp_[A-Za-z0-9]{20,}",
    r"github_pat_[A-Za-z0-9_]{20,}",
    r"CTF_KEY\s*=\s*\S+",
)


def ctf_key() -> str:
    key = os.environ.get("CTF_KEY")
    if not key:
        sys.exit(f"{RED}CTF_KEY is not set. Open the mission from the Field Agents Codespace.{RESET}")
    return key


def mission_flag(mission_id: str) -> str:
    """FA{s0_f2_xxxxxxxxxxxx} derived from the season CTF_KEY and the mission id."""
    digest = hmac.new(ctf_key().encode(), mission_id.encode(), hashlib.sha256).hexdigest()[:12]
    season, mission = mission_id.lower().split("-")
    return f"FA{{{season}_{mission}_{digest}}}"


def shop_url() -> str:
    return os.environ.get("SHOP_URL", DEFAULT_SHOP_URL)


class ShopUnreachable(Exception):
    """Juice Shop did not answer, or answered with something unexpected."""


def juice_shop_solved(challenge_key: str, url: str | None = None) -> bool:
    """True if the Juice Shop challenge is solved. Raises ShopUnreachable."""
    base = (url or shop_url()).rstrip("/")
    query = urllib.parse.urlencode({"key": challenge_key})
    try:
        with urllib.request.urlopen(f"{base}/api/Challenges/?{query}", timeout=5) as resp:
            data = json.load(resp)["data"]
    except Exception as exc:
        raise ShopUnreachable(f"Can't reach Juice Shop at {base} ({exc}). Is it running?") from exc
    return bool(data) and bool(data[0].get("solved"))


_FENCE = re.compile(r"^\s*(```|~~~)")


def sections(markdown: str) -> dict:
    """Map lowercased H2 headings to their body text. Ignores fenced code blocks."""
    out, current, in_fence = {}, None, False
    for line in markdown.splitlines():
        if _FENCE.match(line):
            in_fence = not in_fence
        m = None if in_fence else re.match(r"^##\s+(.+?)\s*#*\s*$", line)
        if m:
            current = m.group(1).strip().lower()
            out[current] = ""
        elif current is not None:
            out[current] += line + "\n"
    return out


def find_section(secs: dict, aliases) -> str | None:
    """Body of the first heading containing any alias as a whole word or phrase."""
    for heading, body in secs.items():
        for alias in aliases:
            if re.search(rf"(?<![a-z0-9]){re.escape(alias.lower())}(?![a-z0-9])", heading):
                return body
    return None


def bullets(text: str) -> list:
    """List items (-, *, or 1.) in a block of markdown."""
    return [ln.strip() for ln in text.splitlines() if re.match(r"^\s*([-*+]|\d+[.)])\s+\S", ln)]


def find_secrets(text: str) -> list:
    """Every substring that looks like a key or token."""
    return [m.group(0) for p in SECRET_PATTERNS for m in re.finditer(p, text)]


class Report:
    def __init__(self, title: str):
        self.title, self.results = title, []

    def check(self, ok, label: str, hint: str = "") -> bool:
        self.results.append((bool(ok), label, hint))
        return bool(ok)

    def check_solved(self, challenge_key: str, label: str, hint: str = "", url: str | None = None) -> bool:
        """Check a Juice Shop challenge; an unreachable shop is a failed check, not a crash."""
        try:
            return self.check(juice_shop_solved(challenge_key, url), label, hint)
        except ShopUnreachable as exc:
            return self.check(False, label, str(exc))

    def passed(self) -> bool:
        return bool(self.results) and all(ok for ok, _, _ in self.results)

    def print(self):
        print(f"\n{self.title}\n" + "-" * len(self.title))
        for ok, label, hint in self.results:
            mark = f"{GREEN}PASS{RESET}" if ok else f"{RED}FAIL{RESET}"
            print(f"  {mark}  {label}")
            if not ok and hint:
                print(f"        {DIM}hint: {hint}{RESET}")
        print()

    def finish(self, mission_id: str, success: str = "Mission complete.") -> int:
        """Print the report, then the flag if every check passed. Returns the exit code."""
        self.print()
        if self.passed():
            print(f"{GREEN}{success} Flag: {mission_flag(mission_id)}{RESET}\n")
            return 0
        print("Not yet. Fix the failures above and run the grader again.\n")
        return 1
