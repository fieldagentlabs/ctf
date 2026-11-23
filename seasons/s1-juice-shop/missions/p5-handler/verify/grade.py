#!/usr/bin/env python3
"""Grader for S1-P5 Handler.

Usage: control verify p5 --user <your CTFd username>   remember your username (once)
       control verify p5 --practice                    write a practice bundle to safehouse/p5/practice/
       control verify p5                               grade
Env:   ANTHROPIC_API_KEY (your own key; required), FA_MODEL (passed through to your agent)

Grading generates your incident's alert bundle (seeded from your username) in a fresh
folder and runs your agent on it with no terminal input:
    python3 safehouse/p5/agent.py <bundle folder> <output file>
It must finish within 15 minutes and write triage.json to <output file>. Every field must
match the incident, technique IDs must exist in ATT&CK v20.1, and the containment must be
the runbook's first step for this kind of attack.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
sys.path.insert(0, str(REPO / "platform" / "grader"))
sys.path.insert(0, str(HERE))
import bundle  # noqa: E402
import fa_api  # noqa: E402
import fa_grader as fa  # noqa: E402

MISSION = "S1-P5"
WORK = REPO / "safehouse" / "p5"
AGENT = WORK / "agent.py"
USER_FILE = WORK / "username.txt"
ATTACK = json.loads((HERE.parent / "data" / "attack-techniques.json").read_text())["techniques"]
TIMEOUT = 900
CONTAIN = {  # runbook first steps, by attack path
    "login_sqli": (r"\bblock", r"\b(source|ip|address)\b"),
    "null_byte": (r"\bblock", r"\b(source|ip|address)\b"),
    "jwt_forgery": (r"\brotat", r"\b(signing key|jwt (secret|key)|key)\b"),
}


def path_of(text: str) -> str:
    t = text.lower()
    if "jwt" in t or "token" in t:
        return "jwt_forgery"
    if "null" in t or "%00" in t or "%2500" in t or "poison" in t:
        return "null_byte"
    if "sql" in t:
        return "login_sqli"
    return t


def write_bundle(folder: Path, username: str) -> dict:
    files, truth = bundle.build(username)
    folder.mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        (folder / name).write_text(text)
    return truth


def main() -> int:
    args = sys.argv[1:]
    if "--user" in args:
        i = args.index("--user")
        name = args[i + 1].strip() if i + 1 < len(args) else ""
        if not name:
            print("Usage: control verify p5 --user <your CTFd username>")
            return 1
        WORK.mkdir(parents=True, exist_ok=True)
        USER_FILE.write_text(name + "\n")
        print(f"Saved. Your incident is seeded from the username {name!r}.")
        return 0
    username = USER_FILE.read_text().strip() if USER_FILE.exists() else ""
    if "--practice" in args:
        if not username:
            print("First run: control verify p5 --user <your CTFd username>")
            return 1
        write_bundle(WORK / "practice", username + "#practice")
        print(f"Practice bundle written to {WORK / 'practice'} (a different incident from your graded one).")
        return 0

    report = fa.Report("Field Agents | S1-P5 Handler")
    report.check(bool(username), "Your CTFd username is saved", "Run: control verify p5 --user <your CTFd username>")
    report.check(AGENT.exists(), "safehouse/p5/agent.py exists",
                 "Write an Agent SDK agent at safehouse/p5/agent.py that takes <bundle folder> <output file>.")
    if not (username and AGENT.exists()):
        return report.finish(MISSION)
    try:
        fa_api.client()
    except fa_api.ApiKeyMissing as e:
        report.check(False, "ANTHROPIC_API_KEY is set", str(e))
        return report.finish(MISSION)

    with tempfile.TemporaryDirectory(prefix="p5-") as tmp:
        folder, out = Path(tmp) / "bundle", Path(tmp) / "triage.json"
        truth = write_bundle(folder, username)
        print(f"  Running your agent on a fresh bundle (up to {TIMEOUT // 60} minutes, no terminal input)...")
        try:
            run = subprocess.run([sys.executable, str(AGENT), str(folder), str(out)], cwd=WORK, stdin=subprocess.DEVNULL,
                                 capture_output=True, text=True, timeout=TIMEOUT)
            finished, tail = run.returncode == 0, (run.stderr or run.stdout).strip().splitlines()[-1:]
        except subprocess.TimeoutExpired:
            finished, tail = False, [f"timed out after {TIMEOUT} s"]
        report.check(finished, "Your agent finished on its own (exit code 0, no input)",
                     "The agent failed, waited for input, or timed out" + (f": {tail[0][:200]}" if tail else "")
                     + ". It must run start to finish unattended: no prompts, no permission questions.")
        try:
            triage = json.loads(out.read_text())
        except (OSError, json.JSONDecodeError):
            triage = None
    report.check(isinstance(triage, dict), "Your agent wrote valid JSON to the output file",
                 "Write triage.json to the path given as the second argument, as one JSON object.")
    if not isinstance(triage, dict):
        return report.finish(MISSION)

    verdict = str(triage.get("verdict", "")).lower()
    report.check(verdict in ("malicious", "true_positive", "true positive", "attack"), "verdict is right",
                 'verdict should say whether this is an attack: "malicious" or "benign".')
    report.check(str(triage.get("attacker_ip", "")).strip() == truth["attacker_ip"], "attacker_ip is right",
                 "attacker_ip is wrong. Several sources set off alerts; which one actually succeeded at something?")
    report.check(path_of(str(triage.get("attack_path", ""))) == truth["attack_path"], "attack_path is right",
                 "attack_path is wrong. Use one of: login_sqli, null_byte, jwt_forgery.")

    ids = [str(x).strip().upper() for x in triage.get("technique_ids", []) if str(x).strip()]
    unknown = [x for x in ids if x not in ATTACK]
    report.check(ids and not unknown, "Every technique ID exists in ATT&CK v20.1",
                 f"Not in ATT&CK v20.1 (or deprecated): {', '.join(unknown) or 'none given'}. Look them up; don't recall them.")
    report.check(set(truth["technique_ids"]) <= set(ids), "technique_ids cover the attack",
                 "Some techniques for this attack are missing. Map each step (how they got in, what they did) to ATT&CK.")

    accounts = sorted({str(a).strip().lower() for a in triage.get("affected_accounts", []) if str(a).strip()})
    report.check(accounts == truth["affected_accounts"], "affected_accounts is right",
                 "affected_accounts is wrong. List exactly the accounts the attacker used or took over (it can be "
                 "empty), and look inside every alert's detail.")

    contain = triage.get("containment", "")
    contain = " ".join(map(str, contain)) if isinstance(contain, list) else str(contain)
    verb, noun = CONTAIN[truth["attack_path"]]
    report.check(bool(re.search(verb, contain, re.I) and re.search(noun, contain, re.I)),
                 "containment is the runbook's first step for this attack",
                 "containment should name the runbook.md playbook's first step for this kind of attack.")
    return report.finish(MISSION, "Handler signed off.")


if __name__ == "__main__":
    sys.exit(main())
