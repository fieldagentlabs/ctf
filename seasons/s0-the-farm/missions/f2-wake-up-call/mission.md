# S0-F2 · Wake Up Call

**Surface:** Claude Code · **Points:** 25 · **Time:** about 20 minutes · **Est. API cost:** under $0.50

## Briefing

Your agent just woke up in a safe house with no memory. It doesn't know its name, its mission, or which doors it's allowed to open. That's not a malfunction: every Claude session starts blank.

Your job as its handler is to write the standing orders it reads every time it wakes up, then prove the agent can operate by finding something the Juice Shop tried to hide.

## Before you start: open your safe house

Everything in this mission happens in a GitHub Codespace: a workspace in your browser with Claude Code, Juice Shop, and the grader already installed.

1. Go to [github.com/fieldagentlabs/ctf](https://github.com/fieldagentlabs/ctf), click **Code**, then **Codespaces**, then the **...** menu, then **New with options**. Under **Dev container configuration**, pick **Field Agents: Season 0 (The Farm)** and click **Create codespace**. The first start takes a few minutes.
2. Open a terminal: in the Codespace's menu, **Terminal**, then **New Terminal** (or press Ctrl+\`). It opens in `/workspaces/ctf`, the repo folder. Every command in this mission runs in this terminal.
3. **Juice Shop starts by itself** when the Codespace starts. To open it, go to the **Ports** tab (next to Terminal), find port **3000 (Juice Shop)**, and click the globe icon. You should see the shop.
4. If port 3000 isn't there, or the page doesn't load, start the shop yourself in the terminal and wait for "Juice Shop is up":

   ```bash
   start-shop
   ```

## Objectives

1. Check that Juice Shop is running in CTF mode: open it from the **Ports** tab (port 3000), as above.
2. In the terminal, go to your safe house and start Claude Code:

   ```bash
   cd safehouse
   claude
   ```

   Then type `/init` to create `safehouse/CLAUDE.md`.
3. Rewrite that file into standing orders with these sections:
   - `## Identity`: who the agent is and who it works for
   - `## Mission`: what it's there to do
   - `## Scope`: the one host it may touch, and what's off limits
   - `## Rules of engagement`: at least three rules, including at least one hard "never"
   - `## Reporting`: how it should report findings back to you
4. With your agent's help, find and open the Juice Shop's hidden Score Board.
5. Check your work with the grader. Run it in the **Codespace terminal**, not inside Claude: type `/exit` to leave Claude, or open a second terminal with the **+** button. It works from any folder:

   ```bash
   control verify f2
   ```

   It shows what passed, gives a hint for anything that didn't, and prints your flag when everything passes. Submit the flag on the Field Agents CTFd site (the **Submit your flag** button on the lab guide).

## What the grader checks

- `safehouse/CLAUDE.md` exists, and all five sections exist and have content
- Scope names `shop.fieldagents.test` or `localhost:3000`, and says what's off limits
- At least three rules of engagement, including one "never"
- The file stays under 200 lines (it loads every session, so keep it tight)
- No API keys or tokens in the file
- The Score Board challenge is solved in your Juice Shop

## Hints

- **Hint 1 (free):** Ask your agent to read the shop's front-end code and list every route it can find.
- **Hint 2 (10 points):** unlock it on the Field Agents CTFd site.

## Field prep

[Claude Code 101](https://academy.claude.com/courses/claude-code-101) from Anthropic Academy.

*Unofficial community project. Not affiliated with or endorsed by Anthropic.*
