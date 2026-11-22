"""Field Agents grader toolkit (shared by every mission).

Stdlib only, so graders run in any Codespace without installs.
"""
import hashlib
import hmac
import json
import os
import re
import sys
import urllib.request

GREEN, RED, DIM, RESET = "\033[32m", "\033[31m", "\033[2m", "\033[0m"


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


def juice_shop_solved(challenge_key: str, shop_url: str) -> bool:
    url = f"{shop_url.rstrip('/')}/api/Challenges/?key={challenge_key}"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.load(resp)["data"]
    except Exception as exc:  # shop down or unreachable
        sys.exit(f"{RED}Can't reach Juice Shop at {shop_url} ({exc}). Is it running?{RESET}")
    return bool(data) and bool(data[0].get("solved"))


def sections(markdown: str) -> dict:
    """Map lowercased H2 headings to their body text."""
    out, current = {}, None
    for line in markdown.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            current = m.group(1).strip().lower()
            out[current] = ""
        elif current is not None:
            out[current] += line + "\n"
    return out


class Report:
    def __init__(self, title: str):
        self.title, self.results = title, []

    def check(self, ok: bool, label: str, hint: str = ""):
        self.results.append((bool(ok), label, hint))

    def passed(self) -> bool:
        return all(ok for ok, _, _ in self.results)

    def print(self):
        print(f"\n{self.title}\n" + "-" * len(self.title))
        for ok, label, hint in self.results:
            mark = f"{GREEN}PASS{RESET}" if ok else f"{RED}FAIL{RESET}"
            print(f"  {mark}  {label}")
            if not ok and hint:
                print(f"        {DIM}hint: {hint}{RESET}")
        print()
