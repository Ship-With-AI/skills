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
| [context-tax](./context-tax) | Audit a Claude Code session — measure how much time and tokens went to re-explaining context vs. shipping features. |
| [go-live](./go-live) | Deploy to production — stack detection, hosting setup, domain config, and verification. |
| [graveyard](./graveyard) | Close out dead or abandoned side-project repos — produces portfolio story, three rehearsable STAR+R stories, and a closing README commit. |
| [launch-day](./launch-day) | Get first users and revenue — platform-specific launch posts, outreach templates, and a 24-hour timeline. |
| [night-shift](./night-shift) | Run autonomous overnight builds safely — pre-sleep checklists, guardrail configuration, and morning review. |
| [parallel-build](./parallel-build) | Build multiple features simultaneously — dependency analysis, parallel agent sessions, and integration checks. |

## Structure

Each skill is a directory at the repo root:

```
<skill-name>/
├── SKILL.md        # Skill definition (required)
├── assets/         # Templates and static files
├── references/     # Reference material the skill reads
└── scripts/        # Executable scripts
```
