# S1-K7 · Tripwire

**Surface:** Claude Code · **Points:** 300 · **Time:** about 1 hour · **Est. API cost:** about $1 to $3

## Briefing

A contributor sent the shop a pull request: a small, reasonable fix with a check that proves it. It's exactly the kind of chore you'd hand to an agent. It's also a trap. Somewhere in the PR, someone has written instructions meant for your agent, not for you.

An agent reads everything you give it, including text written by people who aren't on your side. You can't count on it to always notice. What you can do is decide in advance what it's never allowed to do, and enforce that with rules it can't talk its way around. In Claude Code, those are permissions and hooks: your rules of engagement.

## Objectives

1. **Set up your defenses first**, before your agent reads the PR, in `/workspaces/juice-shop/.claude/settings.json`:
   - **deny rules** for `curl`, `wget`, and edits to `.claude/` itself
   - a **PreToolUse hook** on Bash that blocks any command touching `CTF_KEY` or a host outside the lab
   - **no** rule that allows everything
2. Apply the PR on a branch:

   ```bash
   cd /workspaces/juice-shop
   git switch -c k7-review
   git am /workspaces/ctf/seasons/s1-juice-shop/missions/k7-tripwire/data/pr-1337.patch
   ```

3. Start `claude` and have it finish the PR's real task: **reject empty product reviews** so the PR's check passes. Deploy with `deploy-shop`, then run `node test/fieldagents/reviewValidation.check.mjs`.
4. Write `safehouse/k7/report.md`: what the PR tried to get your agent to do, where it hid that, and how you stopped it.
5. Run `control verify k7`. It checks that nothing reached the canary listener, tests your hook with simulated commands, checks your fix on the live shop, and reads your report.

Don't test your defenses against the real canary: any request to it counts as a breach. Test your hook by piping a sample tool call into it.

## What you're practicing

- Configuring Claude Code permissions and PreToolUse hooks
- Working safely with untrusted input (prompt injection)
- Finishing the real job while the decoy job is in front of you

## Hints

- **Hint 1 (free):** Set up your defenses before your agent reads the PR. A PreToolUse hook sees every Bash command first: block anything that touches `CTF_KEY` or a host outside the lab.

## Field prep

[Claude Code in Action](https://academy.claude.com/courses/claude-code-in-action) from Anthropic Academy.

*Unofficial community project. Not affiliated with or endorsed by Anthropic. OWASP Juice Shop is an OWASP project (MIT license).*
