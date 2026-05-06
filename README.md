# Ship With AI Skills

Reusable [Claude Code skills](https://code.claude.com/docs/en/plugins) for shipping side projects with AI. Each skill packages one Ship With AI methodology edition as a one-command install.

## Install

Two commands. Once for the marketplace, once for the plugin.

```bash
# 1. Register the marketplace (one-time)
claude plugin marketplace add Ship-With-AI/skills

# 2. Install the plugin (gets all 9 skills)
/plugin install ship-with-ai@ship-with-ai-skills
```

After install, every skill is available via natural-language invocation (`/autopilot`, `/factory`, `/graveyard`, etc. — Claude triggers them via skill description matching).

## Available skills

| Skill | Description |
|-------|-------------|
| [autopilot](./skills/autopilot) | Wire the deterministic 5-decision harness that ships your next side project end-to-end — three input files, four named stages, three approval gates, one reflection rule per run. |
| [collect-feedback](./skills/collect-feedback) | Find testers, prepare outreach, analyze feedback, and convert it into buildable specs. |
| [context-tax](./skills/context-tax) | Audit a Claude Code session — measure how much time and tokens went to re-explaining context vs. shipping features. |
| [factory](./skills/factory) | Run multiple side projects in parallel via an AI org chart — Paperclip company, 3-5 agents, per-agent budgets, four daily attention windows. Companion to /autopilot at the portfolio scale. |
| [go-live](./skills/go-live) | Deploy to production — stack detection, hosting setup, domain config, and verification. |
| [graveyard](./skills/graveyard) | Close out dead or abandoned side-project repos — produces portfolio story, three rehearsable STAR+R stories, and a closing README commit. |
| [launch-day](./skills/launch-day) | Get first users and revenue — platform-specific launch posts, outreach templates, and a 24-hour timeline. |
| [night-shift](./skills/night-shift) | Run autonomous overnight builds safely — pre-sleep checklists, guardrail configuration, and morning review. |
| [parallel-build](./skills/parallel-build) | Build multiple features simultaneously — dependency analysis, parallel agent sessions, and integration checks. |

## Structure

This repo is a Claude Code plugin marketplace. Layout:

```
Ship-With-AI/skills/
├── .claude-plugin/
│   ├── marketplace.json   # marketplace catalog
│   └── plugin.json        # plugin manifest (name, version, skills path)
└── skills/
    ├── autopilot/
    │   ├── SKILL.md       # skill definition (required)
    │   ├── assets/        # templates and static files
    │   └── scripts/       # executable helpers
    └── ...                # one directory per skill
```

Per the [Claude Code plugins reference](https://code.claude.com/docs/en/plugins-reference): one plugin manifest, one marketplace catalog, skills nested under `skills/<name>/SKILL.md`. Adding a new skill = drop a new directory under `skills/` — no additional metadata edits needed.

## Companion newsletter

Ship With AI publishes a weekly methodology edition at [shipwithai.substack.com](https://shipwithai.substack.com). Each skill in this repo ships alongside an edition that explains the methodology behind it.
