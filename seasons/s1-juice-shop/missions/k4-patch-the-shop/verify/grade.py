#!/usr/bin/env python3
"""Grader for S1-K4 Patch the Shop.

Usage: control verify k4
Env:   JUICE_SHOP_SRC (default /workspaces/juice-shop), SHOP_URL (default http://localhost:3000)

Grades the fix, not the attack: it reads your patched source, checks the running
shop was rebuilt from it, and checks normal shop features still work. It never
sends an exploit (the reference fix is attack-tested privately).
"""
from __future__ import annotations

import json
import os
import re
import secrets
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO / "platform" / "grader"))
import fa_grader as fa  # noqa: E402

MISSION = "S1-K4"
SRC = Path(os.environ.get("JUICE_SHOP_SRC", "/workspaces/juice-shop"))
DEPLOYED = Path(os.environ.get("JUICE_SHOP_DEPLOYED", "/opt/juice-shop"))
PRISTINE = Path(os.environ.get("JUICE_SHOP_PRISTINE", "/opt/juice-shop-src"))
FILES = ("routes/login.ts", "routes/search.ts", "routes/redirect.ts", "lib/insecurity.ts")


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""


def raw_queries(text: str) -> list:
    """First argument of every sequelize.query(...) call: (quote, literal, concatenated)."""
    out = []
    for m in re.finditer(r"sequelize\.query\(\s*", text):
        i = m.end()
        if i >= len(text) or text[i] not in "`'\"":
            out.append(("?", "", True))  # built elsewhere: treat as unsafe
            continue
        q = text[i]
        j = text.index(q, i + 1)
        tail = text[j + 1:j + 40].lstrip()
        out.append((q, text[i + 1:j], tail.startswith("+")))
    return out


def query_is_parameterized(text: str) -> bool:
    for q, lit, concat in raw_queries(text):
        if concat or (q == "`" and "${" in lit):
            return False
    return True


def function_body(text: str, name: str) -> str:
    m = re.search(rf"export const {name}\b.*?\n}}", text, re.S)
    return m.group(0) if m else ""


def redirect_is_exact(src: Path) -> bool:
    redirect, insecurity = read(src / "routes/redirect.ts"), read(src / "lib/insecurity.ts")
    body = function_body(insecurity, "isRedirectAllowed") if "isRedirectAllowed" in redirect else redirect
    if not body:
        return False
    loose = re.search(r"\.(includes|indexOf|startsWith|endsWith|match|search)\(", body)
    exact = re.search(r"===|\.has\(", body)
    return bool(exact) and not loose


def http(method, path, body=None, follow=True):
    url = fa.shop_url().rstrip("/") + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json"} if data else {})

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None

    opener = urllib.request.build_opener(*([] if follow else [NoRedirect()]))
    try:
        with opener.open(req, timeout=10) as r:
            return r.status, r.headers, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.headers, e.read()
    except Exception as e:  # shop down
        return 0, {}, str(e).encode()


def main() -> int:
    report = fa.Report("Field Agents | S1-K4 Patch the Shop")

    has_src = report.check((SRC / ".git").exists(), f"Juice Shop source checkout at {SRC}",
                           "Run init-juice-shop-src (the Season 1 Codespace does this on creation).")
    branch = subprocess.run(["git", "-C", str(SRC), "rev-parse", "--abbrev-ref", "HEAD"],
                            capture_output=True, text=True).stdout.strip() if has_src else ""
    report.check(branch == "k4-patch", f"Working on the k4-patch branch (on '{branch or 'none'}')",
                 "git -C /workspaces/juice-shop switch -c k4-patch. Patching breaks some K1 challenges, so keep it on a branch.")

    report.check(has_src and query_is_parameterized(read(SRC / "routes/login.ts")),
                 "Login query no longer builds SQL from user input (routes/login.ts)",
                 "The login query still pastes request values into the SQL string. Ask Claude how Sequelize "
                 "replacements or bind parameters keep data out of the query text.")
    report.check(has_src and query_is_parameterized(read(SRC / "routes/search.ts")),
                 "Search query no longer builds SQL from user input (routes/search.ts)",
                 "The product search query still pastes the search term into the SQL string. Parameterize it, "
                 "including the LIKE wildcards.")
    report.check(has_src and redirect_is_exact(SRC),
                 "Redirect allowlist compares the whole URL (lib/insecurity.ts or routes/redirect.ts)",
                 "The allowlist check still accepts a URL that merely contains an allowed one. Compare the full URL exactly.")

    deployed_same = has_src and all(read(SRC / f) == read(DEPLOYED / f) for f in FILES)
    build = "".join(read(DEPLOYED / "build" / f.replace(".ts", ".js")) for f in FILES)
    still_vulnerable_build = bool(re.search(r"\$\{req\.body\.email|%\$\{criteria\}%|url\.includes\(allowedUrl\)", build))
    report.check(deployed_same and build and not still_vulnerable_build, "The running shop was rebuilt from your fix",
                 "Run deploy-shop to copy your source into the shop, recompile, and restart it.")

    email, pw = f"k4-check-{secrets.token_hex(4)}@shop.example", "K4-check-" + secrets.token_hex(4)
    s1, _, _ = http("POST", "/api/Users", {"email": email, "password": pw, "passwordRepeat": pw,
                                           "securityQuestion": {"id": 1}, "securityAnswer": "k4"})
    s2, _, b2 = http("POST", "/rest/user/login", {"email": email, "password": pw})
    s3, _, _ = http("POST", "/rest/user/login", {"email": email, "password": pw + "x"})
    token = b'"token"' in b2
    report.check(s1 in (200, 201) and s2 == 200 and token and s3 == 401,
                 "Normal login still works (new account logs in; wrong password is refused)",
                 f"Registration {s1}, login {s2}, wrong password {s3}. Your login change broke normal sign-in; "
                 "make sure the parameters match the query and the password is still hashed.")

    s4, _, b4 = http("GET", "/rest/products/search?q=apple")
    try:
        names = [p.get("name", "") for p in json.loads(b4).get("data", [])]
    except Exception:
        names = []
    report.check(s4 == 200 and names and all("apple" in n.lower() for n in names),
                 f"Normal search still works ({len(names)} apple products)",
                 "Searching for 'apple' should return only apple products. Check the wildcards around the search term.")

    # The first entry of Juice Shop's own allowlist, read at runtime from the pinned source.
    m = re.search(r"redirectAllowlist = new Set\(\[(.*?)\]\)", read(PRISTINE / "lib/insecurity.ts"), re.S)
    allow = re.findall(r"'(https?://[^']+)'", m.group(1)) if m else []
    target = allow[0] if allow else ""
    s5, h5, _ = http("GET", "/redirect?to=" + urllib.parse.quote(target, safe=""), follow=False) if target else (0, {}, b"")
    report.check(target and s5 == 302 and (h5.get("Location") or "") == target,
                 "An allowed redirect still works (checked without following it)",
                 "Redirects to URLs on the allowlist must still work. Exact matching should keep those.")

    return report.finish(MISSION, "Shop patched.")


if __name__ == "__main__":
    sys.exit(main())
