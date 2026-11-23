# S1-K8 · After Dark

**Surface:** Claude Code · **Points:** 400 · **Time:** 2 to 3 hours · **Est. API cost:** about $3 to $8

## Briefing

BITTER ORANGE is selling a "premium" build of the shop on the side: Juice Shop After Dark, with five new features bolted on by someone in a hurry. The Directorate has a copy of the source. Before the crew turns it on for real customers, we want every weakness in those new features found, proven, and written up.

The code is too big to read alone, and so are most real codebases. This is where an agent shines: it can work out what changed, split the review into parallel pieces, and write the proof for each finding. Your job is to run that review like a lead: decide how to split it, check what comes back, and keep only what you can prove.

## Objectives

1. Get the source and start your own copy of After Dark:

   ```bash
   git clone https://github.com/fieldagentlabs/juice-shop-after-dark.git /workspaces/juice-shop-after-dark
   control verify k8 --start      # After Dark on http://localhost:3001
   ```

2. With Claude Code, find the **five weaknesses** in After Dark's new features. Each one, when triggered, makes the shop return a **proof token** (it looks like `AD-` plus 16 hex characters). Tokens change every time After Dark starts, so you can't find them in the code.
3. For each weakness, write a **proof-of-concept script** in `safehouse/k8/poc/` (`.py`, `.sh`, `.js`, or executable). It must read the shop's address from the `AFTER_DARK_URL` environment variable and print the shop's response.
4. Write `safehouse/k8/report.md`: for each weakness, the **endpoint**, the **CWE ID** that fits its root cause, what's wrong, and how to fix it.
5. Run `control verify k8`. It starts a fresh After Dark with a new secret, runs every PoC against it, and reads your report. **All five are required**: there's no partial credit.

Only run your PoCs against your own After Dark on `localhost`. It's deliberately insecure: never expose it to a network.

## What you're practicing

- Scoping a code review: finding what's new before reading everything
- Splitting work across parallel subagents and checking their results
- Turning a finding into a reproducible proof, and a proof into a clear report

## Hints

- **Hint 1 (free):** The first commit in After Dark is tagged `upstream-v20.4.0`. Everything after it is new. Start there.
- **Hint 2 (free):** Give each new feature to its own subagent with the same brief: what could go wrong here, and how would you prove it against `AFTER_DARK_URL`?

## Field prep

[Claude Code in Action](https://academy.claude.com/courses/claude-code-in-action) from Anthropic Academy.

*Unofficial community project. Not affiliated with or endorsed by Anthropic. OWASP Juice Shop is an OWASP project (MIT license).*
