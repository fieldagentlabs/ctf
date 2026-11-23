# S0-F3 · Radio Check

**Surface:** Claude Console · **Points:** 25 · **Time:** about 20 minutes · **Est. API cost:** under $0.05

## Briefing

Before an agent goes into the field, its handler checks the radio. Today that radio is the Claude Console: your own API key, a budget you control, and the Workbench, where you can test a prompt before it ever touches real work.

The test transmission is a single line from a web server log. Turn it into clean, structured data exactly the way the Directorate's format demands. Somewhere in that line is a coded message for you.

## Objectives

1. Sign in to the Claude Console and create an API key for Field Agents. Put it in a workspace with a **monthly spend limit** set, so a mistake can never cost you much. (This step is on the honor system, but do it: every Console mission after this one uses your key.)
2. Open the **Workbench**. Write a system prompt that tells Claude to return **only** JSON matching the schema below.
3. Send this log line as the user message:

   ```text
   203.0.113.47 - - [14/Oct/2026:02:19:48 +0000] "POST /rest/user/login HTTP/1.1" 200 812 "-" "Mozilla/5.0 (FA-Radio; UkFESU8tQ0hFQ0stTE9VRC1BTkQtQ0xFQVI=)"
   ```

4. Check the output against the schema. If any field is missing, wrong, or wrapped in extra text, tighten your prompt and run it again.
5. Submit the value of `ua_token_decoded` wrapped as `FA{...}`. Capitals or lowercase both work.

## Schema

| Field | Type | What goes in it |
| --- | --- | --- |
| `source_ip` | string | The client IP address |
| `timestamp_utc` | string | The request time in ISO 8601, UTC (for example `2026-01-31T13:45:00Z`) |
| `method` | string | The HTTP method |
| `path` | string | The request path |
| `status` | integer | The HTTP status code |
| `ua_token_decoded` | string | The token inside the user agent's parentheses, decoded |

## What you're practicing

- Creating an API key and keeping your spending under control
- Writing a system prompt in the Workbench and iterating on it
- Getting structured JSON output you could hand straight to a script

## Hints

- **Hint 1 (free):** If Claude won't decode the token, ask it to decode the base64 string in the user agent explicitly.

## Field prep

[Claude Platform 101](https://academy.claude.com/courses/claude-platform-101) from Anthropic Academy.

*Unofficial community project. Not affiliated with or endorsed by Anthropic.*
