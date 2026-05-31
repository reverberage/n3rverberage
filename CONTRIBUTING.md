# Contributing to n3rv

## N3RV (AI Agent Infrastructure)

You're already in the N3RV repo. For other projects in this ecosystem, install N3RV and run `n3rv init` to set up the SDD workflow, A2A hub, and OpenCode integration.

For this project itself, all N3RV integration is already configured — see `.opencode/agents/n3rv.md` for available commands, skills, and SDD agents.

## Dev Setup

See `AGENTS.md` for coding standards, rules, and the skill index.

## Running Tests

```bash
pytest
```

## Code Style

All rules are enforced via `AGENTS.md` (loaded automatically by opencode agent).
See the **Skill Index** and **Universal Rules** sections.

## Adding Skills

See `AGENTS.md` → **Skill Index** for the full list. To add a new skill:
1. Create `.opencode/skills/<name>/SKILL.md` with required frontmatter
2. Add it to `AGENTS.md` skills table