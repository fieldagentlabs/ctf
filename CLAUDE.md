# ctf (PUBLIC)

This is the public, player-facing repo for Field Agents, an unofficial, free security CTF for learning Claude chat, Claude Code, and the Claude Console.

**Everything here is visible to players.** Never add answers, real flags, solutions, the answer key, data generators that reveal answers, or `CTF_KEY` values. Those live in the private repo, `fieldagentlabs/ctf-hq`, and its `CLAUDE.md` holds the full build rules.

If you were started in this repo by mistake, stop and tell the user to run Claude Code from `ctf-hq` with `--add-dir ../ctf`.

Player-side layout:

- `platform/grader/`: shared grader toolkit
- `seasons/<season>/missions/<id>-<slug>/`: `mission.md`, `data/`, `verify/grade.py`
- `.devcontainer/`: Codespace configs, one per season

Never use the long dash character in any file.
