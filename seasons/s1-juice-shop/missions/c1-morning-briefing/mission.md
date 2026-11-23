# S1-C1 · Morning Briefing

**Surface:** Claude chat · **Points:** 100 · **Time:** about 30 minutes · **Est. API cost:** free (any Claude plan)

## Briefing

Operation Juice Shop starts with a bad night. Sometime on 14 October 2026, someone got into `shop.fieldagents.test`. The night shift saw nothing; the morning shift found the access logs and a very nervous shop manager.

You're the first handler on the ticket. Before anyone can contain, report, or brief leadership, someone has to answer three questions: who got in, how, and when. Your agent can read a day of logs faster than you can scroll them. Your job is to point it at the right questions and check every answer against the evidence.

## Objectives

1. Download the evidence (a dead drop from the shop's nginx front):
   - [`data/access-extract.log`](data/access-extract.log): about 20 hours of traffic around the incident (5 MB, plain text). Start here.
   - [`data/access.log.gz`](data/access.log.gz): the full 48 hours, if you want everything.
2. Upload the extract to [claude.ai](https://claude.ai) (any plan).
3. With Claude, find:
   - the **attacker's IP address**,
   - the **entry point**: the endpoint they used to break in,
   - the **minute (UTC) of the first successful exploit**.
4. Ask Claude for a timeline of the attack, and check at least two of its entries against the raw log lines yourself.
5. Submit `FA{IP_ENDPOINT_HHMM}`, for example `FA{192.0.2.1_/api/Example_1342}`. You can separate the parts with `_`, `:`, or `|`.

Keep your timeline: the next missions build on it.

## About the logs

Each line is nginx's standard "combined" format with one extra field at the end: the request body, JSON-escaped (`-` when there is none). Times are UTC.

```text
IP - - [time] "METHOD path HTTP/1.1" status bytes "referer" "user agent" "request body"
```

## What you're practicing

- Uploading evidence to Claude and asking structured questions about it
- Telling apart noisy traffic and malicious traffic
- Checking Claude's conclusions against the raw evidence before you report them

## Hints

- **Hint 1 (free):** Noisy isn't the same as malicious. Who succeeded at something they shouldn't?

## Field prep

[Claude 101](https://academy.claude.com/courses/claude-101) from Anthropic Academy.

*Unofficial community project. Not affiliated with or endorsed by Anthropic.*
