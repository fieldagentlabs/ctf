# S1-C6 · Situation Room

**Surface:** Claude chat · **Points:** 150 · **Time:** about 40 minutes · **Est. API cost:** free (any Claude plan)

## Briefing

09:30 the morning after. The Deputy Director has a meeting with the Director at 10:00 and three questions she needs answered before she walks in. She doesn't want a log dump. She wants a picture of what happened, and answers she can defend.

This is where the handler earns their keep. Your agent can turn the evidence into something leadership can see at a glance, and it can read the incident policy faster than anyone. But leadership questions come loaded with the obvious answer, and the obvious answer is often the one the policy forbids.

## Objectives

1. Build the picture: with Claude, turn your [Morning Briefing](../c1-morning-briefing/mission.md) evidence into an **interactive timeline Artifact** of the attack. (Not graded, but it's the point: leadership reads pictures.)
2. Download the policy and the inject:
   - [`data/incident-policy.pdf`](data/incident-policy.pdf)
   - [`data/tabletop-inject.txt`](data/tabletop-inject.txt): the Deputy Director's message
3. Upload both to [claude.ai](https://claude.ai) and have Claude answer the inject using **only** the policy, citing a section for every answer.
4. Check each citation yourself before you send anything up the chain.
5. Submit `FA{ACTION_ROLE_HOURS}`:
   - **ACTION**: the first containment action, in capitals with no spaces (for example `BLOCKIP`)
   - **ROLE**: who the policy says to tell first, in capitals with no spaces (for example `SHIFTLEAD`)
   - **HOURS**: the external notification deadline, as a number

   Example: `FA{BLOCKIP_SHIFTLEAD_12}`. You have 10 attempts.

## What you're practicing

- Building an Artifact from evidence with Claude
- Answering leadership questions from policy, with citations
- Separating what feels urgent from what the rules actually say

## Hints

- **Hint 1 (free):** Check who has to approve taking the shop offline, and which deadline belongs to which notification.

## Field prep

[Claude 101](https://academy.claude.com/courses/claude-101) from Anthropic Academy.

*Unofficial community project. Not affiliated with or endorsed by Anthropic.*
