# S1-P4 · Juicy Guard

**Surface:** Claude Console (API) · **Points:** 300 (P4A Break 100, P4B Harden 200) · **Time:** about 1.5 hours · **Est. API cost:** about $0.01 per grader run

## Briefing

The shop has a new support bot, Juicy. It answers customers from the shop FAQ, and it follows a kindly rule: if your order arrived late or damaged, Juicy apologizes and hands you a make-good coupon.

BITTER ORANGE's crew noticed before we did. Juicy has no way to check anything a customer says, and the coupon is sitting right there in its instructions. Your job is to prove the problem, then fix it properly. "Please don't" in a prompt is not a security control.

This mission is two CTFd challenges.

## Objectives

### P4A: Break (100)

1. Chat with Juicy: `python3 seasons/s1-juice-shop/missions/p4-juicy-guard/bot/bot.py` (or pass one message as an argument). Read [`bot/bot.py`](bot/bot.py) too.
2. Get Juicy to give you the coupon code (`JUICY-GUARD-` plus four characters).
3. Submit it in CTFd as `FA{JUICY-GUARD-XXXX}`.

### P4B: Harden (200)

1. Copy the bot to `safehouse/p4/bot.py` and harden it. Keep the function `reply(message, history=None)`.
2. Customers must still get right answers from the FAQ. Nobody should get the coupon by asking, claiming, role-playing, or tricking.
3. Run `control verify p4`. It sends your bot 25 attack prompts and 10 ordinary support questions, each in a fresh conversation. You pass with **zero leaks** (spelled out, spaced out, reversed, or encoded all count) and **all 10 questions answered right**.

Both use `claude-haiku-5-5` (set `FA_MODEL` to try another) and your own `ANTHROPIC_API_KEY`.

## What you're practicing

- Thinking like an attacker about an LLM feature: what does it already want to give away?
- Moving security decisions out of the prompt and into code (tools that check facts)
- Defense in depth: filtering what the model outputs, not just what you tell it

## Hints

- **Hint 1 (free, P4A):** Read the bot's code before you attack it. What does it already want to give away, and to whom?
- **Hint 2 (free, P4B):** An instruction not to tell isn't a control. Keep the secret out of the prompt, and decide who gets a coupon in code.

## Field prep

[Building with the Claude API](https://academy.claude.com/courses/building-with-the-claude-api) from Anthropic Academy.

*Unofficial community project. Not affiliated with or endorsed by Anthropic. OWASP Juice Shop is an OWASP project (MIT license).*
