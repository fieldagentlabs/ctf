# S1-K5 · Catch Yourself

**Surface:** Claude Code · **Points:** 200 · **Time:** about 1 hour · **Est. API cost:** about $1 to $3

## Briefing

You've spent the season attacking the shop. Every request you made through its nginx front was written down. Now switch sides: turn your own attacks into detections the Directorate's SOC could run tomorrow, before BITTER ORANGE comes back.

Good detections are a balance. Too loose and the SOC drowns in false alarms from a search engine's crawler or an employee who can't remember their password. Too tight and the next variation walks straight past. Your agent can draft a rule in seconds. Your job is to test it against real traffic and tune it until it catches attacks and leaves people alone.

## Objectives

1. Make sure you have attack traffic of your own: work through some [Shop Floor](../k1-shop-floor/mission.md) challenges via `http://shop.fieldagents.test`. It's all in `/var/log/shop/access.log`, in the same format as the [breach evidence](../c1-morning-briefing/mission.md).
2. With Claude Code, group your attacks into behaviors and write **Sigma** rules for at least these four:
   - SQL injection against the login
   - UNION injection in the product search
   - null bytes or path traversal in a request path
   - wordlist scanning (bursts of 404s)
3. Save the rules as `.yml` files in `safehouse/k5/detections/`. Use `logsource: category: webserver` and these fields:

   | Field | Meaning |
   | --- | --- |
   | `c-ip` | client IP |
   | `cs-method` | HTTP method |
   | `cs-uri-stem` | path, without the query string |
   | `cs-uri-query` | query string, as logged (URL-encoded) |
   | `sc-status` | status code (a number) |
   | `sc-bytes` | response size (a number) |
   | `cs-referer`, `cs-user-agent` | as logged |
   | `cs-body` | request body |

4. Package what you did as a **skill** (for example `.claude/skills/detection-from-logs/SKILL.md`), so the next handler can rerun it after the next attack.
5. Run `control verify k5`. It replays a breach shaped like the one you studied, mixed with 50,000+ lines of normal traffic and two decoys, and needs **90% of each behavior caught**, at most **0.5% of normal traffic flagged**, and **neither decoy flagged**.

## What you're practicing

- Writing detection rules from evidence with Claude Code
- Tuning against real noise, not just the attack
- Packaging a workflow as a reusable skill

## Hints

- **Hint 1 (free):** A burst of 404s isn't an attack by itself. Count them per client over a time window with a Sigma correlation rule, and set the threshold above what an ordinary crawler does.

## Field prep

[Introduction to agent skills](https://academy.claude.com/courses/introduction-to-agent-skills) from Anthropic Academy.

*Unofficial community project. Not affiliated with or endorsed by Anthropic. OWASP Juice Shop is an OWASP project (MIT license).*
