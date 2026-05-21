# Ship With AI Skills

Reusable [Claude Code skills](https://code.claude.com/docs/en/plugins) for shipping side projects with AI. Each skill packages one Ship With AI methodology edition as a one-command install.

## Install

Two paths. Pick whichever fits your setup.

### Path A — Cross-agent via Skills CLI (recommended)

Single command. Works for 40+ agents (Claude Code, Codex, Cursor, Gemini CLI, GitHub Copilot, OpenCode, Amp, Cline, Aider, and more — auto-detected).

```bash
# Install all 10 skills to all detected agents
npx skills add Ship-With-AI/skills --all

# Or cherry-pick a single skill (e.g., just /autopilot)
npx skills add Ship-With-AI/skills --skill autopilot

# Or pick a few
npx skills add Ship-With-AI/skills --skill autopilot --skill factory

# Non-interactive (CI/CD or skip prompts)
npx skills add Ship-With-AI/skills --all -g -y
```

From [vercel-labs/skills](https://github.com/vercel-labs/skills). No CLI install needed — `npx` fetches it on demand.

### Path B — Claude Code native plugin marketplace

If you're Claude-Code-only and prefer native tooling (no extra CLI):

```bash
# 1. Register the marketplace (one-time)
claude plugin marketplace add Ship-With-AI/skills

# 2. Install the plugin (gets all 10 skills)
/plugin install ship-with-ai@ship-with-ai-skills
```

### After install

Every skill is available via natural-language invocation (`/autopilot`, `/factory`, `/graveyard`, etc.) regardless of which install path you used — agents trigger skills via the `description:` field in each `SKILL.md`, not via path or namespace.

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
| [steering-loop](./skills/steering-loop) | Scaffold an agent harness inside any project (guides + sensors + steering-log) and iterate it one rep at a time — Read → Guide → Run → Sense → Log. The companion to the WHAT/WHY/HOW skill stack. |

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
