# S1-P3 · Desk Officer

**Surface:** Claude Console (API) · **Points:** 250 · **Time:** about 2 hours · **Est. API cost:** about $0.05 per grader run

## Briefing

Every morning since the breach, someone from leadership asks the same kinds of questions: who got in, when, how many times, what did they take. Each answer means someone digging through 50,000 log lines. The Directorate wants a desk officer that can answer on its own, and show its work.

Claude can't read a 48-hour log in one go, and it shouldn't guess. Give it **tools** instead: small functions that search, count, and order the log. Claude decides which tool to call, reads the result, and calls again until it can answer. You write the tools and the loop; Claude does the investigating.

## Objectives

1. Use the canonical log from C1: [`../c1-morning-briefing/data/access.log.gz`](../c1-morning-briefing/data/access.log.gz). The grader passes its path to your script in the `FA_LOG` environment variable.
2. Write `safehouse/p3/ask.py` with three tools over the log, using the Messages API's tool use:
   - `search_logs`: return matching lines (by IP, status, method, path, or text)
   - `count_events`: count matching lines, optionally grouped (for example by IP or status)
   - `get_timeline`: one IP's requests in time order
3. Add the loop: send the question with the tools, run each tool Claude asks for, return the results, and repeat until Claude answers.
4. Make the script's contract exact. `python3 safehouse/p3/ask.py "<question>"` must print, as its **last line**, one JSON object:

   ```json
   {"answer": "203.0.113.x compromised the shop.", "tool_calls": [{"name": "count_events", "input": {"group_by": "ip"}}]}
   ```

   Keep answers short and specific (under 400 characters). When a question asks whether something was an attack, start the verdict with **Yes** or **No**.
5. Run `control verify p3`. It asks 10 questions about the breach. You pass with at least 9 right, each backed by at least one tool call.

Use `claude-haiku-5-5` (or set `FA_MODEL`, which the grader passes through). The SDK is already installed in the Codespace.

## What you're practicing

- Defining tools with clear names, descriptions, and input schemas
- Writing the tool-use loop, including returning tool errors to Claude
- Designing tool output that's small enough to read and big enough to answer from

## Hints

- **Hint 1 (free):** Tool results are tokens too. Return a total and the first few dozen lines, not 50,000 lines.
- **Hint 2 (free):** Models count badly by eye. If a question asks "how many", make sure your tools can do the counting.

## Field prep

[Tool use with the Messages API](https://academy.claude.com/courses/tool-use-with-the-messages-api) from Anthropic Academy.

*Unofficial community project. Not affiliated with or endorsed by Anthropic. OWASP Juice Shop is an OWASP project (MIT license).*
