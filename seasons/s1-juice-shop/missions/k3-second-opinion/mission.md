# S1-K3 · Second Opinion

**Surface:** Claude Code · **Points:** 200 · **Time:** about 45 minutes · **Est. API cost:** about $1 to $3

## Briefing

A scanner just dropped 12 findings and two ready-made patches on your desk. Every finding says "confidence: high". Every patch says it fixes the problem. The Directorate's rule: nothing ships on a tool's word.

Some of these findings are wrong, and one of the patches looks right and isn't. A single agent reading all of it at once gets tired and agreeable. A team of focused agents, each checking one claim against the code, doesn't. Your job is to build that team, run it, and sign off only on what survives.

## Objectives

1. In the **Season 1** Codespace, open the bundle: [`data/findings-bundle.json`](data/findings-bundle.json). Every finding and patch refers to the Juice Shop source at `/workspaces/juice-shop`.
2. In Claude Code, create **subagents** (`/agents`), for example one that verifies a single finding against the code and one that reviews a patch. Save them as definition files in `.claude/agents/` (in `safehouse/` or `/workspaces/juice-shop/`).
3. Have Claude spawn a verifier per finding, and a reviewer per patch that applies it to a scratch copy and tests whether it fixes the root cause.
4. Write `safehouse/k3/triage.json`:

   ```json
   {
     "findings": {
       "F-01": {"verdict": "true_positive", "reason": "one or two sentences, citing the code"}
     },
     "patches": {
       "P-01": {"verdict": "accept", "reason": "why it does or doesn't fix the root cause"}
     }
   }
   ```

   Verdicts: `true_positive` or `false_positive` for findings, `accept` or `reject` for patches. Every one needs a reason. When you reject a patch, explain how the weakness survives it.
5. Run `control verify k3`.

## What you're practicing

- Creating and running Claude Code subagents in parallel
- Treating tool output as claims to verify
- Reviewing a plausible patch until you can say exactly why it's wrong

## Hints

- **Hint 1 (free):** Give each finding to its own subagent with one job: read the code and decide whether the claim actually holds. Frameworks escape and parameterize more than scanners assume.

## Field prep

[Introduction to subagents](https://academy.claude.com/courses/introduction-to-subagents) from Anthropic Academy.

*Unofficial community project. Not affiliated with or endorsed by Anthropic. OWASP Juice Shop is an OWASP project (MIT license).*
