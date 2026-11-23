# S1-K6 · One Shot

**Surface:** Claude Code · **Points:** 250 · **Time:** about 45 minutes · **Est. API cost:** a few dollars (one run)

## Briefing

Some jobs don't get a conversation. The Directorate needs an agent that can be sent in alone, with no one to answer its questions, and come back with the job done. In Claude Code that's a headless run: one prompt, one session, no second chances.

What makes that work is preparation. A skill tells your agent, every time, what it's allowed to touch, how to work, how to check its own results, and when to stop. Get the skill right and one run is enough. Get it wrong and the agent wanders, burns your budget, and comes back with half the job.

## Objectives

1. In the **Season 1** Codespace, write a skill at `safehouse/.claude/skills/shop-recon/SKILL.md` (with `name` and `description` in its frontmatter). It should cover:
   - **scope:** only the shop at `localhost:3000` / `shop.fieldagents.test`
   - **the loop:** try something, then check the challenge's status in `/api/Challenges`
   - **when to stop**
2. Open the run window. This restarts Juice Shop and clears every solve:

   ```bash
   control verify k6 --start
   ```

3. Make **one** headless run that solves these five Juice Shop challenges: **Login Admin, Admin Section, Confidential Document, Error Handling, Zero Stars**.

   ```bash
   cd safehouse
   claude -p "<your prompt>" --output-format json > k6/run.json
   ```

4. Run `control verify k6`. It checks your skill, that all five were solved during the run, and that the run's total tokens are under the budget.

Didn't make it? Improve the skill, then start again from step 2. One run per window.

## What you're practicing

- Writing a Claude Code skill that makes an agent reliable
- Running Claude Code headless (`claude -p`) and reading its JSON output
- Designing for a token budget

## Hints

- **Hint 1 (free):** A headless run can't ask you anything. Put the scope, the loop (try, then check `/api/Challenges`), and the stopping rule in the skill so the agent never wanders.

## Field prep

[Introduction to agent skills](https://academy.claude.com/courses/introduction-to-agent-skills) from Anthropic Academy.

*Unofficial community project. Not affiliated with or endorsed by Anthropic. OWASP Juice Shop is an OWASP project (MIT license).*
