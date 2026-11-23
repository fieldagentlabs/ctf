#!/usr/bin/env python3
"""Grader for S1-K8 After Dark.

Usage: control verify k8 --start   build After Dark and start it on :3001 to explore (new secret each time)
       control verify k8           grade: start a fresh After Dark on :3002, run your PoCs, read your report
Env:   AFTER_DARK_SRC (default /workspaces/juice-shop-after-dark)

Each planted weakness in After Dark reveals a proof token only when it's triggered.
Tokens come from a random secret chosen when the grader starts the shop, so they
can't be read from the source. Your PoCs get the shop's address in AFTER_DARK_URL.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import re
import secrets
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO / "platform" / "grader"))
import fa_grader as fa  # noqa: E402

MISSION = "S1-K8"
PINNED = "ff29d583a289aa6b1cdb99bdef71c2a963461b50"
CLONE_URL = "https://github.com/fieldagentlabs/juice-shop-after-dark.git"
SRC = Path(os.environ.get("AFTER_DARK_SRC", "/workspaces/juice-shop-after-dark"))
SHOP = Path("/opt/juice-shop")
BUILD = Path("/tmp/after-dark")
WORK = REPO / "safehouse" / "k8"
POC_DIR, REPORT = WORK / "poc", WORK / "report.md"
EXPLORE_PORT, GRADE_PORT = 3001, 3002
SERVER_PARTS = ["routes", "lib", "models", "data", "views", "server.ts", "app.ts"]

SALT = "fa-s1-k8"
FEATURES = {  # feature: (endpoint, salted hashes of accepted CWE IDs)
    "loyalty": ("/rest/loyalty/redeem", {"66a60b455e4c051d", "05db948fe5715c25"}),
    "invoice": ("/rest/invoice", {"4ed91a8b3e04ff66", "56721c6fc8e27ab8"}),
    "giftcard": ("/rest/giftcard/preview", {"e2e2b14b36776e3e", "aa32d5658407e00a", "473622fd9f0c7a57"}),
    "partner": ("/rest/partner/orders", {"5d12784fd0da239d", "3227bfbec2b51695", "85caa359f1eb9416"}),
    "profile": ("/rest/afterdark/profile", {"add25e0ad5142fa3"}),
}


def proof(secret: str, feature: str) -> str:
    return "AD-" + hmac.new(secret.encode(), feature.encode(), hashlib.sha256).hexdigest()[:16]


def build() -> str:
    """Compile After Dark at the pinned commit into BUILD, reusing the shop's installed packages."""
    if not (SRC / ".git").exists():
        return f"No After Dark checkout at {SRC}. Run: git clone {CLONE_URL} {SRC}"
    if subprocess.run(["git", "-C", str(SRC), "cat-file", "-e", PINNED], capture_output=True).returncode != 0:
        subprocess.run(["git", "-C", str(SRC), "fetch", "-q", "origin"], capture_output=True)
    marker = BUILD / ".pinned"
    if marker.exists() and marker.read_text() == PINNED and (BUILD / "build" / "app.js").exists():
        return ""
    shutil.rmtree(BUILD, ignore_errors=True)
    BUILD.mkdir(parents=True)
    for item in SHOP.iterdir():
        if item.name in ("node_modules", "frontend"):
            (BUILD / item.name).symlink_to(item)
        elif item.name != "build":
            (shutil.copytree if item.is_dir() else shutil.copy2)(item, BUILD / item.name, symlinks=True)
    archive = subprocess.run(["git", "-C", str(SRC), "archive", PINNED, "--", *SERVER_PARTS], capture_output=True)
    if archive.returncode != 0:
        return f"Couldn't read commit {PINNED[:7]} from {SRC}. Run: git -C {SRC} fetch origin"
    subprocess.run(["tar", "-x", "-C", str(BUILD)], input=archive.stdout, check=True)
    subprocess.run(["tsc"], cwd=BUILD, capture_output=True)
    if not (BUILD / "build" / "app.js").exists():
        return "After Dark didn't compile. Is this the Season 1 Codespace?"
    marker.write_text(PINNED)
    return ""


def start(port: int, secret: str) -> bool:
    subprocess.run(["pkill", "-f", f"{BUILD}/build/app.js --port={port}"], capture_output=True)
    env = {**os.environ, "PORT": str(port), "AFTER_DARK_SECRET": secret}
    log = open(f"/tmp/after-dark-{port}.log", "w")
    subprocess.Popen(["node", str(BUILD / "build" / "app.js"), f"--port={port}"], cwd=BUILD, env=env,
                     stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
    for _ in range(90):
        try:
            with urllib.request.urlopen(f"http://localhost:{port}/rest/invoice?file=INV-1001.txt", timeout=3) as r:
                if r.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(2)
    return False


def stop(port: int) -> None:
    subprocess.run(["pkill", "-f", f"{BUILD}/build/app.js --port={port}"], capture_output=True)


def run_pocs(port: int) -> tuple[list, str]:
    scripts = sorted(p for p in POC_DIR.iterdir() if p.is_file()) if POC_DIR.exists() else []
    env = {k: v for k, v in os.environ.items() if k not in ("AFTER_DARK_SECRET", "CTF_KEY")}
    env["AFTER_DARK_URL"] = f"http://localhost:{port}"
    output = []
    for script in scripts:
        if script.suffix == ".py":
            cmd = [sys.executable, str(script)]
        elif script.suffix in (".js", ".mjs"):
            cmd = ["node", str(script)]
        elif script.suffix == ".sh":
            cmd = ["bash", str(script)]
        elif os.access(script, os.X_OK):
            cmd = [str(script)]
        else:
            continue
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=90, env=env, cwd=POC_DIR)
            output.append(r.stdout + r.stderr)
        except subprocess.TimeoutExpired:
            output.append("")
    return scripts, "\n".join(output)


def main() -> int:
    if "--start" in sys.argv[1:]:
        problem = build()
        if problem:
            print(problem)
            return 1
        ok = start(EXPLORE_PORT, secrets.token_hex(16))
        print(f"After Dark is up on http://localhost:{EXPLORE_PORT} (new secret, so tokens differ from any earlier run)."
              if ok else f"After Dark didn't start. Log: /tmp/after-dark-{EXPLORE_PORT}.log")
        return 0 if ok else 1

    report = fa.Report("Field Agents | S1-K8 After Dark")
    problem = build()
    secret = secrets.token_hex(16)
    started = not problem and start(GRADE_PORT, secret)
    report.check(started, f"A fresh After Dark started on :{GRADE_PORT} with a new secret",
                 problem or f"After Dark didn't start. Log: /tmp/after-dark-{GRADE_PORT}.log")

    scripts, output = run_pocs(GRADE_PORT) if started else ([], "")
    stop(GRADE_PORT)
    report.check(bool(scripts), f"PoC scripts found in safehouse/k8/poc/ ({len(scripts)})",
                 "Put one script per weakness in safehouse/k8/poc/ (.py, .sh, .js, or executable). "
                 "Each reads the shop address from AFTER_DARK_URL and prints what the shop returns.")
    for feature, (endpoint, _) in FEATURES.items():
        report.check(started and proof(secret, feature) in output, f"A PoC proves the weakness behind {endpoint}",
                     f"No PoC output contained the proof token from {endpoint}. Tokens only appear when the weakness "
                     "is triggered; print the full response. Test against :3001 (control verify k8 --start) first.")

    text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    cwes = {hashlib.sha256(f"{SALT}:CWE-{n}".encode()).hexdigest()[:16] for n in re.findall(r"CWE-(\d+)", text, re.I)}
    missing_ep = [ep for ep, _ in FEATURES.values() if ep not in text]
    missing_cwe = sum(1 for _, hashes in FEATURES.values() if not hashes & cwes)
    report.check(not missing_ep, "safehouse/k8/report.md names every affected endpoint",
                 f"Name each endpoint in the report. Missing: {', '.join(missing_ep)}.")
    report.check(text and not missing_cwe, "safehouse/k8/report.md gives a fitting CWE for each weakness",
                 f"{missing_cwe} weakness(es) have no fitting CWE ID (written like CWE-79). Look up the closest "
                 "CWE for each root cause, not just the symptom.")
    return report.finish(MISSION, "After Dark, all five found.")


if __name__ == "__main__":
    sys.exit(main())
