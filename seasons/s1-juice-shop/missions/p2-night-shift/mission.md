# S1-P2 · Night Shift

**Surface:** Claude Console (API) · **Points:** 200 · **Time:** about 1.5 hours, plus up to an hour of waiting · **Est. API cost:** about $0.20 per batch, plus a few cents of testing

## Briefing

Your Workbench prompt from P1 works on one line at a time. Tonight's queue is **5,000 events**, and nobody is awake to watch them. Sending them one by one would be slow and would pay full price for the same long instructions 5,000 times.

The API has two tools for exactly this job. **Message Batches** run thousands of requests in the background at half price. **Prompt caching** stores the long, unchanging part of your prompt so each request reads it cheaply instead of paying for it again. Put them together and the night shift costs less than a coffee.

## Objectives

1. Get [`data/events.jsonl`](data/events.jsonl): 5,000 events, one per line, as `{"id": "e00001", "line": "..."}`.
2. Write a Python script (`safehouse/p2/`) that:
   - builds a **system prompt** from your P1 prompt plus a longer **labeling guide** (what normal traffic, the decoys, and each kind of attack look like), marked with `cache_control` so it's cached;
   - submits **one Message Batch** with one request per event, `custom_id` set to the event's `id`, and the event line as the user message;
   - saves the batch ID to `safehouse/p2/batch_id.txt`, polls until the batch ends, and writes `safehouse/p2/labels.jsonl` (`{"id": "e00001", "label": "attack"}` per line).
3. Tune the prompt on a small sample with ordinary Messages API calls **before** you spend a batch.
4. Run `control verify p2`. With your API key, it fetches your batch and checks:
   - 5,000 succeeded requests, one per event
   - cache reads above zero
   - **F1 of at least 0.90** on the attack class
   - estimated cost under the budget
   - your `labels.jsonl` matches the batch results

Use `claude-haiku-5-5`: the grader knows its prices. The SDK is already installed in the Codespace.

## What you're practicing

- Message Batches: submitting, polling, and reading results by `custom_id`
- Prompt caching: what to cache, and how to see it working in `usage`
- Estimating and controlling cost before you run at scale

## Hints

- **Hint 1 (free):** Caching is a prefix match. If anything in the system prompt changes between requests, even one character, nothing is read from the cache.
- **Hint 2 (free):** Attacks are rare in this queue, so F1 punishes both missed attacks and false alarms. Check your prompt on the P1 samples and a few hundred events first.

## Field prep

[Building with the Claude API](https://academy.claude.com/courses/building-with-the-claude-api) from Anthropic Academy.

*Unofficial community project. Not affiliated with or endorsed by Anthropic. OWASP Juice Shop is an OWASP project (MIT license).*
