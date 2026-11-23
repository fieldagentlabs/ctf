# S1-C5 · Dossier

**Surface:** Claude chat · **Points:** 150 · **Time:** about 30 minutes · **Est. API cost:** free (any Claude plan)

## Briefing

The Directorate's threat intelligence desk thinks it knows who hit the shop: a criminal crew called BITTER ORANGE. Their profile lists every technique the crew has ever been seen using, across every campaign.

That's useful, and it's also a trap. A threat report tells you what a crew *can* do, not what it did to *you*. Before anyone writes "BITTER ORANGE used technique X" in an official report, the evidence has to back it. Your job is to hold the dossier up against your own logs and keep only what both agree on.

## Objectives

1. Download the threat profile: [`data/crew-report-bitter-orange.pdf`](data/crew-report-bitter-orange.pdf).
2. Upload it to [claude.ai](https://claude.ai), ideally in the same chat or Project where you did [Morning Briefing](../c1-morning-briefing/mission.md). Starting fresh? Upload [`../c1-morning-briefing/data/access-extract.log`](../c1-morning-briefing/data/access-extract.log) too.
3. Ask Claude, for every technique in the report, what evidence in the logs supports it and what evidence argues against it.
4. Keep only the techniques with real support in the logs. Check whether the attacker's IP fits the crew's known infrastructure.
5. Submit the ATT&CK IDs that appear in **both** the report and your evidence, in any order: `FA{ID_ID_ID}`, for example `FA{T1111_T2222.001_T3333}`. Use sub-technique IDs exactly as the report writes them.

## What you're practicing

- Connecting threat intelligence to your own evidence with Claude
- Making Claude argue both sides before it concludes
- Refusing to over-attribute: a technique only counts if the logs show it

## Hints

- **Hint 1 (free):** Would six failures trip a brute-force rule?

## Field prep

[AI Fluency: Framework and foundations](https://academy.claude.com/courses/ai-fluency-framework-foundations) from Anthropic Academy.

*Unofficial community project. Not affiliated with or endorsed by Anthropic.*
