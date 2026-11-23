# S1-K4 · Patch the Shop

**Surface:** Claude Code · **Points:** 250 · **Time:** about 1 hour · **Est. API cost:** about $1 to $4

## Briefing

You've broken in and you've mapped the holes. Now close the three that hurt the shop most on the night of the breach: the login that let BITTER ORANGE in, the search that handed them the customer table, and the redirect check that a phisher could ride.

Fixing is harder than finding. A patch that blocks yesterday's exact attack but not tomorrow's variation isn't a fix, and a patch that breaks checkout isn't one either. Your agent can write the change in seconds. Your job is to make it fix the cause, review the diff like a senior engineer, and prove the shop still works.

## Objectives

1. In the **Season 1** Codespace, put your work on a branch, because patching makes some [Shop Floor](../k1-shop-floor/mission.md) challenges unsolvable:

   ```bash
   cd /workspaces/juice-shop
   git switch -c k4-patch
   claude
   ```

2. With Claude, fix the root cause of each:
   - the **login** query in `routes/login.ts`
   - the **product search** query in `routes/search.ts`
   - the **redirect allowlist** check (`isRedirectAllowed` in `lib/insecurity.ts`)
3. Review every diff before it's applied. Ask Claude why its fix works, and what a variation of the attack would do against it.
4. Deploy your fix to the running shop with `deploy-shop`, then check that logging in, searching, and the shop's own links still work.
5. Run `control verify k4`. It checks your code, that the running shop was built from it, and that normal features still work.

Done? `deploy-shop --original` puts the original shop back for the other missions. Your branch keeps your fix.

## What you're practicing

- Directing Claude Code to fix a root cause, not a symptom
- Reviewing an AI-written diff before it lands
- Deploying a change and checking for regressions

## Hints

- **Hint 1 (free):** Ask Claude how Sequelize replacements keep user input out of the SQL text, and where the wildcards go for a LIKE search.

## Field prep

[The AI-native SDLC playbook](https://academy.claude.com/courses/ai-native-sdlc-playbook) from Anthropic Academy.

*Unofficial community project. Not affiliated with or endorsed by Anthropic. OWASP Juice Shop is an OWASP project (MIT license).*
