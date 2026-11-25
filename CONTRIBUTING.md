# Contributing to Field Agents

This is the public, player-facing repo. **Everything here is visible to players.** Never add answers, real flags, solutions, the answer key, data generators that reveal answers, or `CTF_KEY` values. Those live in the private repo, `fieldagentlabs/ctf-hq`, whose `CLAUDE.md` holds the full build rules.

Maintainers: run Claude Code from `ctf-hq` with `--add-dir ../ctf`. The root `CLAUDE.md` in this repo is written for players' agents, not for building the CTF.

## Layout

- `platform/grader/`: shared grader toolkit (`fa_grader.py`) and its tests
- `seasons/<season>/missions/<id>-<slug>/`: `data/` and `verify/grade.py` (whichever the mission needs). Briefs (`mission.md`) live in `ctf-hq` and reach players only through the site.
- `safehouse/`: where players run `claude` and keep their own agent files
- `.devcontainer/`: Codespace configs, one per season
- `tools/lint.py`: repo lint, run in CI

## Rules

- Never use the long dash character in any file (`tools/lint.py` checks).
- No `mission.md` here (`tools/lint.py` checks).
- Reserved names only: `*.test`, `*.example`, 203.0.113.0/24, 198.51.100.0/24, 192.0.2.0/24.
- Paid hint text lives only in CTFd, never in this repo.
