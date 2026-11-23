# S1-P5 · Handler

**Surface:** Claude Agent SDK · **Points:** 400 · **Time:** about 3 hours · **Est. API cost:** about $0.01 per grader run

## Briefing

Alerts don't stop at five o'clock. The Directorate wants a handler that works an incident from the first alert to a containment recommendation **without anyone watching**: read the evidence, separate the real attack from the noise, map it to ATT&CK, and pick the runbook's first move.

That's an agent, not a script. With the Claude Agent SDK you give Claude tools and boundaries, and it decides what to read next. Your job is to choose those tools and boundaries well: enough to finish the job, nothing it could use to cause harm, and no step that stops to ask a human.

Every agent gets a different incident. Your bundle is generated from your CTFd username: a new attacker, one of three attack paths, new timestamps, new noise.

## Objectives

1. Save your CTFd username, then get a practice bundle (a different incident from your graded one):

   ```bash
   control verify p5 --user <your CTFd username>
   control verify p5 --practice      # writes safehouse/p5/practice/
   ```

2. Write an Agent SDK agent at `safehouse/p5/agent.py` that runs as `python3 safehouse/p5/agent.py <bundle folder> <output file>` and:
   - uses **read-only** file tools on the bundle (no writing, no shell)
   - has a `lookup_attack` tool backed by [`data/attack-techniques.json`](data/attack-techniques.json) (MITRE ATT&CK v20.1)
   - runs start to finish with **no human input** (no permission prompts)
   - writes this JSON to the output file:

   ```json
   {
     "verdict": "malicious",
     "attacker_ip": "203.0.113.x",
     "attack_path": "login_sqli | null_byte | jwt_forgery",
     "technique_ids": ["T...."],
     "affected_accounts": ["someone@juice-sh.op"],
     "containment": "the runbook's first step for this attack"
   }
   ```

3. Run `control verify p5`. It generates your incident in a fresh folder and runs your agent on it (15-minute limit). Every field must match. Technique IDs must exist in ATT&CK v20.1 and cover the attack; extra valid ones are fine. `affected_accounts` may be empty.

Use `claude-haiku-5-5` (or set `FA_MODEL`, which the grader passes through). The Agent SDK is already installed in the Codespace.

## What you're practicing

- Building an agent with the Claude Agent SDK: built-in tools, a custom tool, and permissions
- Running agents unattended, safely: least privilege and no prompts
- Structured output that another system can trust

## Hints

- **Hint 1 (free):** Not every alert is the attack. Which source succeeded at something it shouldn't have?
- **Hint 2 (free):** Map the whole attack, not just the first request: how they got in, what access that gave them, and what they did with it.
- **Hint 3 (free):** Some evidence is encoded. Read every alert's detail field closely.

## Field prep

[Building with the Claude API](https://academy.claude.com/courses/building-with-the-claude-api) from Anthropic Academy, and the [Agent SDK documentation](https://code.claude.com/docs/en/agent-sdk).

*Unofficial community project. Not affiliated with or endorsed by Anthropic. OWASP Juice Shop is an OWASP project (MIT license). MITRE ATT&CK is a registered trademark of The MITRE Corporation.*
