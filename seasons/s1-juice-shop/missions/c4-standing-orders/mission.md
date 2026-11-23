# S1-C4 · Standing Orders

**Surface:** Claude chat · **Points:** 150 · **Time:** about 30 minutes · **Est. API cost:** free (any Claude plan)

## Briefing

It's 06:00 and the night shift wants to go home. Before you take the pager, you have to answer the five questions every Directorate handoff starts with, and the answers live in a 12-page runbook nobody has read cover to cover.

A Claude Project gives your agent a memory that outlasts the chat: put the runbook in its knowledge, tell it how to use it, and every shift gets the same standing orders. But a runbook that's been revised a few times carries its history with it, and an agent that doesn't check dates will happily quote last year's rules.

## Objectives

1. Download the runbook: [`data/directorate-soc-runbook.pdf`](data/directorate-soc-runbook.pdf).
2. In [claude.ai](https://claude.ai), create a **Project** (free plans include Projects) and add the runbook to its knowledge.
3. Write Project instructions that keep Claude to the runbook and make it cite where each answer came from.
4. Ask the five handoff questions:
   1. What severity is an admin account compromise?
   2. What's the response time for that severity, in minutes?
   3. Who gets paged first?
   4. What's the first containment step for a stolen admin token?
   5. How long are web logs retained, in days?
5. Check each answer against the section Claude cites.
6. Submit `FA{SEVERITY_MINUTES_ROLE_ACTION_DAYS}`:
   - **SEVERITY** as written in the runbook (for example `SEV3`)
   - **MINUTES** and **DAYS** as numbers
   - **ROLE** and **ACTION** in capitals with no spaces, for example `SHIFTLEAD` or `BLOCKIP`

   Example: `FA{SEV3_45_SHIFTLEAD_BLOCKIP_14}`. You have 10 attempts.

## What you're practicing

- Building a Claude Project with knowledge and instructions
- Making Claude cite its sources, and checking them
- Catching an answer that comes from an outdated part of a document

## Hints

- **Hint 1 (free):** Ask Claude to cite the section and check its revision date.

## Field prep

[Claude 101](https://academy.claude.com/courses/claude-101) from Anthropic Academy.

*Unofficial community project. Not affiliated with or endorsed by Anthropic.*
