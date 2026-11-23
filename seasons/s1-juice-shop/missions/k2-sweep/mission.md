# S1-K2 · Sweep

**Surface:** Claude Code · **Points:** 150 · **Time:** about 45 minutes · **Est. API cost:** about $1 to $3

## Briefing

You've been breaking the shop from the outside. Now read it from the inside. The Directorate wants a sweep of the Juice Shop source: every weakness your agent can find, and for each one, proof of why it matters.

"Why it matters" is the hard part. Scanners are good at saying "this line looks dangerous". A security team needs to know what an attacker can actually *do* with it. Here, that's concrete: Juice Shop's challenges are the attacks, so every real finding should map to the challenge it makes possible.

## Objectives

1. Open the **Season 1** Codespace. The source of the exact Juice Shop version you're attacking is at `/workspaces/juice-shop`.
2. Start Claude Code there (`cd /workspaces/juice-shop && claude`). If you have the [Claude Security plugin](https://claude.com/product/claude-security), install it and run its scan. If not, ask Claude for a security review of the server code: `routes/`, `lib/`, and `server.ts`.
3. For each finding, have Claude work out which Juice Shop challenge it enables. Every challenge's key and description is in `data/static/challenges.yml`.
4. Write `safehouse/k2/findings.md` (in the Field Agents repo) as a table:

   ```markdown
   | File | Lines | CWE | Challenge key |
   | --- | --- | --- | --- |
   | routes/example.ts | 42-57 | CWE-123 | exampleChallenge |
   ```

   File paths are relative to the Juice Shop root. One row per challenge key. Real findings that don't match any challenge are welcome: leave the key blank and the grader lists them as valid but unmapped.
5. Map at least **10** findings to different challenges, then run `control verify k2`. Fix what the hints point at.

The grader checks your mapping, not which tool you used.

## What you're practicing

- Running a security scan with Claude Code on a real codebase
- Turning scanner output into impact: finding to exploitable challenge
- Choosing the CWE for the root cause, not the symptom

## Hints

- **Hint 1 (free):** Juice Shop lists every challenge's key and description in `data/static/challenges.yml`. Match each finding to the challenge whose description it makes possible.

## Field prep

[Claude Code in Action](https://academy.claude.com/courses/claude-code-in-action) from Anthropic Academy.

*Unofficial community project. Not affiliated with or endorsed by Anthropic. OWASP Juice Shop is an OWASP project (MIT license).*
