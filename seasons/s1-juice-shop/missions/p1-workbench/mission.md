# S1-P1 · Workbench

**Surface:** Claude Console · **Points:** 150 · **Time:** about 1 hour · **Est. API cost:** under $0.05

## Briefing

Two weeks after the breach, BITTER ORANGE came back for another look. This time the shop's alert pipeline should catch them, but right now it pages the on-call analyst for every 404 and every mistyped password. The night shift has stopped reading the pages.

The Directorate wants a classifier that reads one log line and says **attack** or **normal**, with a reason, in a format the pipeline can parse. You'll build it as a prompt in the Claude Console Workbench, where you can test it, compare versions side by side, and see exactly what it costs before anything ships.

## Objectives

1. Open [`data/samples.jsonl`](data/samples.jsonl): 20 labeled lines from the shop's nginx front (same format as C1, request body at the end).
2. In the [Claude Console](https://platform.claude.com) Workbench, write a **system prompt** that:
   - explains what counts as an attack and what doesn't,
   - includes 3 to 5 example lines with their answers,
   - makes the reply **only** a JSON object: `{"label": "attack" | "normal", "reason": "..."}`.
3. Test it on the sample lines. Use the Workbench's evaluate view to run it over many lines at once and compare prompt versions.
4. Save the final system prompt as `safehouse/p1/prompt.txt` (the system prompt only).
5. Run `control verify p1`. With your API key, it runs your prompt on **50 held-out lines** it has never shown you, one line per request. You pass with every reply valid JSON and at least 45 labels right.

The grader uses `claude-haiku-5-5` at low effort by default; set `FA_MODEL` to try another model. Test in the Workbench with the same model.

## What you're practicing

- Writing and iterating on a system prompt in the Workbench
- Few-shot examples and output formats a program can rely on
- Evaluating a prompt on data it hasn't seen

## Hints

- **Hint 1 (free):** Noisy isn't the same as hostile. Look at the sample lines labeled normal that still look alarming, and tell the prompt why they're normal.
- **Hint 2 (free):** The held-out lines don't share the samples' IP addresses. Teach the prompt to judge the request, not the address.

## Field prep

[Claude Platform 101](https://academy.claude.com/courses/claude-platform-101) and [Introduction to evals](https://academy.claude.com/courses/introduction-to-evals) from Anthropic Academy.

*Unofficial community project. Not affiliated with or endorsed by Anthropic. OWASP Juice Shop is an OWASP project (MIT license).*
