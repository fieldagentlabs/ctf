# S1-C2 · Paper Trail

**Surface:** Claude chat · **Points:** 100 · **Time:** about 30 minutes · **Est. API cost:** free (any Claude plan)

## Briefing

You know who got in, how, and when. Now the Directorate needs it on paper: a one-page incident report that a security lead, an auditor, and next month's handler can all read without asking you a single question.

Reports like this speak a shared language. MITRE ATT&CK names what the attacker did; CWE names the weakness that let them do it. Your agent knows both catalogs well, and it will sound sure of itself even when it picks the wrong entry. Your job is to make it show its work.

## Objectives

1. Start from your [Morning Briefing](../c1-morning-briefing/mission.md) timeline. Lost it? Re-upload [`../c1-morning-briefing/data/access-extract.log`](../c1-morning-briefing/data/access-extract.log) and rebuild it.
2. Ask Claude for a one-page incident report with: summary, impact, timeline, root cause, an ATT&CK technique for each phase, and a CWE for the root cause.
3. For the **initial access** technique and the **root-cause** CWE, make Claude justify each ID, name the closest alternative, and explain why the alternative doesn't fit. Check both IDs on [attack.mitre.org](https://attack.mitre.org) and [cwe.mitre.org](https://cwe.mitre.org).
4. Submit `FA{TECHNIQUE_CWE}`, for example `FA{T1234_CWE-123}`. Capitals or lowercase both work.

## What you're practicing

- Turning raw findings into a structured report with Claude
- Mapping evidence to ATT&CK and CWE
- Challenging Claude's confident answers instead of copying them

## Hints

- **Hint 1 (10 points):** unlock it on the Field Agents CTFd site.

## Field prep

[AI capabilities and limitations](https://academy.claude.com/courses/ai-capabilities-and-limitations) from Anthropic Academy.

*Unofficial community project. Not affiliated with or endorsed by Anthropic.*
