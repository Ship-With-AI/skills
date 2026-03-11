# Ship-With-AI Skills

Reusable [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code/skills) for building and shipping products.

## Install a skill

```bash
claude install-skill https://github.com/Ship-With-AI/skills/tree/main/<skill-name>
```

## Available skills

| Skill | Description |
|-------|-------------|
| [collect-feedback](./collect-feedback) | Find testers, prepare outreach, analyze feedback, and convert it into buildable specs. |

## Structure

Each skill is a directory at the repo root:

```
<skill-name>/
├── SKILL.md        # Skill definition (required)
├── assets/         # Templates and static files
├── references/     # Reference material the skill reads
└── scripts/        # Executable scripts
```
