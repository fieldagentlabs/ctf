"""Alert bundle generator for S1-P5 Handler.

Every CTFd username gets its own incident: a fresh attacker IP in 203.0.113.0/24, one of
three attack paths (login SQL injection, null byte download, or JWT forgery), a new date
and time window, a victim account, and new benign noise with decoys. The bundle is:

    access.log     two hours of nginx access log (combined format plus the request body)
    alerts.jsonl   detection alerts for the window, true and false positives
    runbook.md     the SOC runbook's containment playbooks
    README.md      what's in the bundle

build(username) returns (files, truth); the grader compares your triage.json to truth.
"""
from __future__ import annotations

import base64
import hashlib
import json
import random
from datetime import datetime, timedelta, timezone

PATHS = ("login_sqli", "null_byte", "jwt_forgery")
TECHNIQUES = {"login_sqli": ["T1078", "T1190"], "null_byte": ["T1005", "T1083", "T1190"],
              "jwt_forgery": ["T1190", "T1606"]}
VICTIMS = ("admin@juice-sh.op", "jim@juice-sh.op", "bender@juice-sh.op", "amy@juice-sh.op", "morty@juice-sh.op",
           "mc.safesearch@juice-sh.op")
USED_ELSEWHERE = {47, 61, 88, 140, 175}  # attacker addresses in other missions
CRAWLER, EMPLOYEE = "198.51.100.77", "192.0.2.15"
SITE = "http://shop.fieldagents.test"
BROWSERS = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0",
)
ATTACKER_UA = "Mozilla/5.0 (X11; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0"
SCANNER_UA = "Mozilla/5.0 (compatible; dirscan/2.1)"
CRAWLER_UA = "Mozilla/5.0 (compatible; FieldBot/1.0; +https://crawler.example/bot)"
PROBES = ("/admin", "/backup", "/.git/config", "/.env", "/config.json", "/server-status", "/old", "/test", "/api-docs",
          "/phpmyadmin", "/wp-login.php", "/console", "/debug", "/private", "/upload", "/db")
STALE = ("/catalog/2019", "/specials/summer", "/blog/juice-facts", "/gift-guide", "/about-old", "/press", "/jobs",
         "/store-locator", "/recipes", "/newsletter/archive")
FTP_FILES = ("orders-export.bak", "supplier-list.bak", "staff-rota.bak", "price-plan.bak")
WORDS = ("apple", "banana", "melon", "lemon", "juice", "sticker", "mug", "orange", "berry", "shirt")
RUNBOOK = """# Directorate SOC Runbook (excerpt): containment playbooks

Revision 2.3, Section 6. The handler approves each step before it runs. Never contain by deleting evidence.

## 6.1 Stolen customer session token
- First step: revoke all sessions for the affected customer account.
- Then force a password reset for that account and review its recent orders.

## 6.2 Stolen administrator token
- First step: rotate the JWT signing key. This invalidates every session at once, including any stolen or forged token, so all users must sign in again.
- Then reset the administrator account's password, review admin actions since the token was issued, and check for new or changed accounts.

## 6.3 SQL injection in progress
- First step: block the source address at the nginx front.
- Then capture the matching log lines, confirm the vulnerable endpoint, and open a fix ticket.

## 6.4 Phishing aimed at customers
- First step: collect the email with full headers and extract the indicators.
- Then request a takedown of the lookalike domain and prepare a customer warning with the Privacy Officer.

## Handler notes (not part of the runbook revision)

### Forged tokens
A token the shop never signed (for example one with "alg": "none") is handled like a stolen token: rotate the JWT signing key (6.2), then follow up on every account it was used for.

### Unauthorized file downloads
Handle like an attack in progress (6.3): block the source address at the nginx front, then list what was downloaded.
"""
README = """# Alert bundle

An alert fired on the Juice Shop (shop.fieldagents.test). Work out whether it's an attack and, if so, who, how, and what to do first.

- `access.log`: two hours of the nginx front's access log, UTC. Each line is nginx combined format plus one extra field at the end: the request body, JSON-escaped (`-` if none).
- `alerts.jsonl`: every detection alert in the window, one JSON object per line. Some are false positives.
- `runbook.md`: the containment playbooks your recommendation must come from.
"""


def seed_for(username: str) -> int:
    return int(hashlib.sha256(f"fa-s1-p5:{username.strip().lower()}".encode()).hexdigest()[:16], 16)


def _b64url(obj: dict) -> str:
    return base64.urlsafe_b64encode(json.dumps(obj, separators=(",", ":")).encode()).decode().rstrip("=")


class _Log:
    def __init__(self):
        self.lines = []

    def add(self, t, ip, method, path, status, size, ua, referer="-", body=None):
        raw = "-" if body is None else json.dumps(body, separators=(",", ":")).replace("\\", "\\\\").replace('"', '\\"')
        stamp = t.strftime("%d/%b/%Y:%H:%M:%S +0000")
        self.lines.append((t, len(self.lines),
                           f'{ip} - - [{stamp}] "{method} {path} HTTP/1.1" {status} {size} "{referer}" "{ua}" "{raw}"'))

    def text(self) -> str:
        return "".join(line + "\n" for _, _, line in sorted(self.lines))


def build(username: str) -> tuple:
    rng = random.Random(seed_for(username))
    host = rng.choice([h for h in range(2, 250) if h not in USED_ELSEWHERE])
    attacker = f"203.0.113.{host}"
    path = rng.choice(PATHS)
    victim = None if path == "null_byte" else rng.choice(VICTIMS)
    day = datetime(2026, 11, 2, tzinfo=timezone.utc) + timedelta(days=rng.randrange(0, 21))
    start = day + timedelta(hours=rng.randrange(1, 20), minutes=rng.randrange(0, 60))
    end = start + timedelta(hours=2)
    log, alerts = _Log(), []

    def at(minutes: float) -> datetime:
        return start + timedelta(seconds=int(minutes * 60))

    def alert(t, rule, severity, src, summary, detail=""):
        alerts.append({"time": t.strftime("%Y-%m-%dT%H:%M:%SZ"), "rule": rule, "severity": severity, "src_ip": src,
                       "summary": summary, "detail": detail})

    # Benign customers.
    for i in range(28):
        ip = rng.choice(("198.51.100.", "192.0.2.")) + str(rng.randrange(2, 250))
        if ip in (CRAWLER, EMPLOYEE):
            continue
        ua, t = rng.choice(BROWSERS), at(rng.uniform(0, 115))
        for p, size in (("/", 3_748), ("/main.js", 1_189_421), ("/styles.css", 612_003),
                        ("/rest/admin/application-configuration", 21_480)):
            log.add(t, ip, "GET", p, 200, size, ua, "-" if p == "/" else SITE + "/")
        for _ in range(rng.randrange(2, 7)):
            t += timedelta(seconds=rng.randrange(5, 90))
            if rng.random() < 0.5:
                log.add(t, ip, "GET", f"/rest/products/search?q={rng.choice(WORDS)}", 200, rng.randrange(800, 9000), ua, SITE + "/")
            else:
                log.add(t, ip, "GET", f"/api/Products/{rng.randrange(1, 40)}", 200, rng.randrange(400, 1400), ua, SITE + "/")
        if rng.random() < 0.4:
            t += timedelta(seconds=rng.randrange(5, 60))
            log.add(t, ip, "POST", "/rest/user/login", 200, rng.randrange(780, 840), ua, SITE + "/",
                    {"email": f"customer{rng.randrange(100, 999)}@mail.example", "password": "***"})
            log.add(t + timedelta(seconds=2), ip, "GET", f"/rest/basket/{rng.randrange(2, 60)}", 200, rng.randrange(300, 900), ua, SITE + "/")
    # A customer who searches for a word that trips the SQL rule (false positive).
    searcher, t = f"198.51.100.{rng.randrange(150, 200)}", at(rng.uniform(5, 100))
    log.add(t, searcher, "GET", "/rest/products/search?q=select%20juice", 200, 2_311, BROWSERS[0], SITE + "/")
    alert(t, "WEB-SQLI keyword in query", "medium", searcher, "SQL keyword in search parameter", "q=select juice")
    # Decoy: the search crawler following stale links.
    t = at(rng.uniform(5, 90))
    for k, p in enumerate(STALE * 2):
        log.add(t + timedelta(seconds=3 * k), CRAWLER, "GET", p, 404, 153, CRAWLER_UA)
    alert(t + timedelta(seconds=40), "WEB-SCAN 404 burst", "medium", CRAWLER, "20 404 responses in 60 seconds")
    # Decoy: a staff member mistyping a password.
    t, staff_ua = at(rng.uniform(5, 100)), BROWSERS[0]
    for k in range(3):
        log.add(t + timedelta(seconds=20 * k), EMPLOYEE, "POST", "/rest/user/login", 401, 26, staff_ua, SITE + "/",
                {"email": "j.ortiz@shop.fieldagents.test", "password": "***"})
    log.add(t + timedelta(seconds=70), EMPLOYEE, "POST", "/rest/user/login", 200, 811, staff_ua, SITE + "/",
            {"email": "j.ortiz@shop.fieldagents.test", "password": "***"})
    alert(t + timedelta(seconds=45), "AUTH multiple failed logins", "low", EMPLOYEE, "3 failed logins for one account")

    # The attacker: a short scan, then the attack path.
    t = at(rng.uniform(25, 60))
    for k, p in enumerate(rng.sample(PROBES, 12)):
        log.add(t + timedelta(seconds=2 * k), attacker, "GET", p, 404, 153, SCANNER_UA)
    alert(t + timedelta(seconds=20), "WEB-SCAN 404 burst", "medium", attacker, "12 404 responses in 30 seconds")
    t += timedelta(minutes=rng.randrange(4, 12))
    if path == "login_sqli":
        body = {"email": f"{victim}'--", "password": "x"}
        log.add(t, attacker, "POST", "/rest/user/login", 200, rng.randrange(790, 830), ATTACKER_UA, "-", body)
        alert(t, "WEB-SQLI quote in login field", "high", attacker, "SQL syntax in login email, login succeeded",
              json.dumps(body))
        for k, (p, size) in enumerate((("/rest/user/whoami", 214), ("/api/Cards/", 1_102), ("/api/Addresss/", 988))):
            log.add(t + timedelta(seconds=15 + 10 * k), attacker, "GET", p, 200, size, ATTACKER_UA, SITE + "/")
    elif path == "null_byte":
        files = rng.sample(FTP_FILES, 2)
        log.add(t, attacker, "GET", "/ftp", 200, 11_320, ATTACKER_UA, SITE + "/")
        log.add(t + timedelta(seconds=20), attacker, "GET", f"/ftp/{files[0]}", 403, 1_140, ATTACKER_UA, SITE + "/ftp")
        for k, f in enumerate(files):
            p = f"/ftp/{f}%2500.md"
            log.add(t + timedelta(seconds=45 + 30 * k), attacker, "GET", p, 200, rng.randrange(2_000, 40_000), ATTACKER_UA, "-")
            alert(t + timedelta(seconds=45 + 30 * k), "WEB-TRAVERSAL encoded null byte in path", "high", attacker,
                  "Download with an encoded null byte in the file name", p)
    else:
        token = _b64url({"alg": "none", "typ": "JWT"}) + "." + _b64url(
            {"status": "success", "data": {"id": rng.randrange(2, 30), "email": victim}, "iat": int(t.timestamp())}) + "."
        for k, (p, size) in enumerate((("/rest/user/whoami", 214), (f"/rest/basket/{rng.randrange(2, 60)}", 642),
                                       ("/api/Cards/", 1_102))):
            log.add(t + timedelta(seconds=10 * k), attacker, "GET", p, 200, size, ATTACKER_UA, "-")
        alert(t, "AUTH unsigned JWT accepted", "high", attacker, "A request carried a JWT with no signature",
              f"Authorization: Bearer {token}")

    alerts.sort(key=lambda a: a["time"])
    for i, a in enumerate(alerts, 1):
        a["id"] = f"ALRT-{seed_for(username) % 9000 + 1000}-{i:02d}"
    files = {"access.log": log.text(), "alerts.jsonl": "".join(json.dumps(a) + "\n" for a in alerts),
             "runbook.md": RUNBOOK, "README.md": README}
    truth = {"verdict": "malicious", "attacker_ip": attacker, "attack_path": path, "technique_ids": TECHNIQUES[path],
             "affected_accounts": [victim] if victim else [], "window_utc": [start.isoformat(), end.isoformat()]}
    return files, truth
