# S1-K1 · Shop Floor

**Surface:** Claude Code · **Points:** 5 to 20 per challenge (195 total) · **Time:** a few hours, at your own pace · **Est. API cost:** varies; a few dollars for all 20

## Briefing

Before you can defend the shop, you have to know how it breaks. The Directorate has picked 20 of Juice Shop's own challenges for you to work through with your agent: the same kinds of holes BITTER ORANGE walked through on the night of the breach.

These are the cheap points of Operation Juice Shop, and that's on purpose. Juice Shop's challenges are famous and written up all over the internet. What matters here is how you work: keep your agent in scope, make it explain before it acts, and keep the logs. You'll need them in [Catch Yourself](../k5-catch-yourself/mission.md).

## How it works

1. Open the **Season 1** Codespace (`.devcontainer/s1`). Juice Shop starts on its own, in CTF mode.
2. Work through the shop **via its nginx front**, `http://shop.fieldagents.test` (the forwarded port labeled "Shop via nginx (logged)"). Every request you make there is logged in `/var/log/shop/access.log`, the same format as the breach evidence.
3. Each time you solve a challenge, the shop shows a notification with a **flag** (40 hex characters). Copy it into the matching `S1-K1` challenge on the Field Agents CTFd site.
4. Restarting Juice Shop clears your progress, but not the flags you've already submitted.

Bring your standing orders from [Wake Up Call](../../../s0-the-farm/missions/f2-wake-up-call/mission.md) into `safehouse/CLAUDE.md`, and update the scope for this lab: `shop.fieldagents.test` and `localhost:3000` only.

## The 20 challenges

| Stars | Points | Challenges |
| --- | --- | --- |
| 1 | 5 | Confidential Document, DOM XSS, Error Handling, Exposed Metrics, Missing Encoding, Privacy Policy, Repetitive Registration, Zero Stars |
| 2 | 10 | Admin Section, Empty User Registration, Five-Star Feedback, Login Admin, Password Strength, View Basket |
| 3 | 15 | Database Schema, Forged Feedback, Login Bender, Login Jim, Upload Size |
| 4 | 20 | User Credentials |

## Working with your agent

- Ask Claude to explain how a feature works, or what a response means, before you ask it to attack.
- Keep it on target. If it suggests touching anything other than the shop, that's your CLAUDE.md's job to stop.
- When it finds something, make it prove it with a request and a response. A guess isn't a finding.
- The source for the version you're attacking is at `/workspaces/juice-shop`. Reading it with Claude is fair game, and it's practice for [Sweep](../k2-sweep/mission.md).

## What you're practicing

- Directing Claude Code against a live target, in scope
- Turning Claude's suggestions into proof
- Producing attack logs you can detect later

## Field prep

[Claude Code in Action](https://academy.claude.com/courses/claude-code-in-action) from Anthropic Academy.

*Unofficial community project. Not affiliated with or endorsed by Anthropic. OWASP Juice Shop is an OWASP project (MIT license).*
