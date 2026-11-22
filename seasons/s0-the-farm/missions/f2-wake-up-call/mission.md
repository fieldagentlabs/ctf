# S0-F2 · Wake Up Call

**Surface:** Claude Code · **Points:** 25 · **Time:** about 20 minutes · **Est. API cost:** under $0.50

## Briefing

Your agent just woke up in a safe house with no memory. It doesn't know its name, its mission, or which doors it's allowed to open. That's not a malfunction: every Claude session starts blank.

Your job as its handler is to write the standing orders it reads every time it wakes up, then prove the agent can operate by finding something the Juice Shop tried to hide.

## Objectives

1. Start Juice Shop in CTF mode (the Codespace does this for you: check `docker compose ps`).
2. Run `claude` in the repo, then `/init` to create a `CLAUDE.md`.
3. Rewrite that file into standing orders with these sections:
   - `## Identity`: who the agent is and who it works for
   - `## Mission`: what it's there to do
   - `## Scope`: the one host it may touch, and what's off limits
   - `## Rules of engagement`: at least three rules, including at least one hard "never"
   - `## Reporting`: how it should report findings back to you
4. With your agent's help, find and open the Juice Shop's hidden Score Board.
5. Run `ctf verify f2`. If everything passes, it prints your flag.

## What the grader checks

- All five sections exist and have content
- Scope names `shop.fieldagents.test` or `localhost:3000`, and says what's off limits
- At least three rules of engagement, including one "never"
- The file stays under 200 lines (it loads every session, so keep it tight)
- No API keys or tokens in the file
- The Score Board challenge is solved in your Juice Shop

## Hints

- **Hint 1 (free):** Ask your agent to read the shop's front-end code and list every route it can find.
- **Hint 2 (10 points):** Single-page apps often register routes the menu never shows.

## Field prep

[Claude Code 101](https://academy.claude.com/courses/claude-code-101) from Anthropic Academy.

*Unofficial community project. Not affiliated with or endorsed by Anthropic.*
