# Ship With AI Skills

Reusable [Claude Code skills](https://code.claude.com/docs/en/plugins) for shipping side projects with AI. Each skill packages one Ship With AI methodology edition as a one-command install.

## Install

Two paths. Pick whichever fits your setup.

### Path A — Cross-agent via Skills CLI (recommended)

Single command. Works for 40+ agents (Claude Code, Codex, Cursor, Gemini CLI, GitHub Copilot, OpenCode, Amp, Cline, Aider, and more — auto-detected).

```bash
# Install every skill detected by your agent
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

```text
# Inside Claude Code: register the marketplace, then install the collection.
/plugin marketplace add Ship-With-AI/skills
/plugin install ship-with-ai@ship-with-ai-skills
```

### After install

Invocation names depend on the agent and installation route. Native Claude Code collection skills use the plugin namespace, such as `/ship-with-ai:autopilot`; selectively installed Claude Code skills use standalone names such as `/autopilot`. Other agents use their own skill syntax. Each SKILL.md description guides discovery.

## Available skills

| Skill | Description |
|-------|-------------|
| [autopilot](./skills/autopilot) | Wire the deterministic 5-decision harness that ships your next side project end-to-end — three input files, four named stages, three approval gates, one reflection rule per run. |
| [collect-feedback](./skills/collect-feedback) | Find testers, prepare outreach, analyze feedback, and convert it into buildable specs. |
| [context-tax](./skills/context-tax) | Audit a Claude Code session — measure how much time and tokens went to re-explaining context vs. shipping features. |
| [case-study](./skills/case-study) | Turn an existing internal script or tool into a buyer-facing case study and outreach message, grounded in repository evidence. |
| [cumpa](./skills/cumpa) | Open Cumpa's native local code-review flow and consume canonical feedback. Requires the separately installed CLI; supports explicit Claude Code, Codex, Pi, and OMP routes. |
| [evaluate-side-project](./skills/evaluate-side-project) | Evaluate, score, and pressure-test a side project idea before implementation — Reddit problem mining, Kaufman 10-factor score, and one-feature PASTA MVP verdict. |
| [factory](./skills/factory) | Run multiple side projects in parallel via an AI org chart — Paperclip company, 3-5 agents, per-agent budgets, four daily attention windows. Companion to /autopilot at the portfolio scale. |
| [go-live](./skills/go-live) | Deploy to production — stack detection, hosting setup, domain config, and verification. |
| [graveyard](./skills/graveyard) | Close out dead or abandoned side-project repos — produces portfolio story, three rehearsable STAR+R stories, and a closing README commit. |
| [launch-day](./skills/launch-day) | Get first users and revenue — platform-specific launch posts, outreach templates, and a 24-hour timeline. |
| [niche-finder](./skills/niche-finder) | Turn recurring work complaints into a defensible niche statement grounded in lived pain, payable demand, and edge-case knowledge. |
| [night-shift](./skills/night-shift) | Run autonomous overnight builds safely — pre-sleep checklists, guardrail configuration, and morning review. |
| [parallel-build](./skills/parallel-build) | Build multiple features simultaneously — dependency analysis, parallel agent sessions, and integration checks. |
| [pre-flight](./skills/pre-flight) | 4-question first-user-readiness eval — runs after /autopilot or /factory says "shipped." Checks output (does the URL work), trace (does the user flow complete), component (do promises resolve to code), drift (still shipping the original idea?). Produces a SHIP/FIX/REBUILD verdict. |
| [proof-project](./skills/proof-project) | Turn one personally observed problem into a narrowly scoped live portfolio project — one user, one input, one useful output, a three-step demo, and a build-ready brief. |
| [steering-loop](./skills/steering-loop) | Scaffold an agent harness inside any project (guides + sensors + steering-log) and iterate it one rep at a time — Read → Guide → Run → Sense → Log. The companion to the WHAT/WHY/HOW skill stack. |

## Cumpa: local code review

[Cumpa](./skills/cumpa) is a thin, independently [MIT-licensed](./skills/cumpa/LICENSE) delegate to the separately installed [Cumpa CLI](https://github.com/Ship-With-AI/cumpa). The skill does not bundle or automatically install the application.

Install the CLI yourself before invoking the skill. Node.js 24+ and Git 2.43.0+ are required:

```bash
npm install --global @shipwithai/cumpa@1.5.0
```

The skill accepts stable Cumpa versions `>=1.5.0 <2.0.0`, including valid build metadata, but rejects prereleases. Cumpa 1.5.0 is the independently verified release; acceptance of future stable 1.x versions is a policy, not a claim that those releases have been tested. Missing or incompatible Cumpa stops with installation guidance; there is no automatic upgrade or npx fallback.

Run project-scoped installation commands from the repository where you want to use the skill:

| Agent | Skill installation | Invoke in the agent |
|-------|--------------------|---------------------|
| Claude Code | Install the existing collection through Path B above. | `/ship-with-ai:cumpa` |
| Codex | `npx skills add Ship-With-AI/skills --skill cumpa -a codex` | `$cumpa` or choose Cumpa in `/skills` |
| Pi | `npx skills add Ship-With-AI/skills --skill cumpa -a pi` | `/skill:cumpa` |
| OMP | Use the native marketplace commands below. | `/skill:cumpa` |

```bash
omp plugin marketplace add Ship-With-AI/skills
omp plugin install --scope project ship-with-ai@ship-with-ai-skills
```

Pi and OMP are separate targets. OMP uses the existing Claude-compatible marketplace catalog, not an assumed Skills CLI `-a omp` adapter. The installer's wider agent list is not a blanket Cumpa compatibility claim.

The developer reviews in Cumpa and presses **Finish**. The skill waits for successful process exit and canonical JSON before reporting feedback; opening a browser or displaying a URL is not completion. Pi uses foreground Bash with live stderr, while Claude Code, Codex, and OMP use their supported supervised process mechanisms. The skill never edits code, commits, pushes, or implements its own review engine.

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

Per the [Claude Code plugins reference](https://code.claude.com/docs/en/plugins-reference): keep one plugin manifest and marketplace catalog, with skills under `skills/<name>/SKILL.md`. Add new skill directories to that collection and increment the declared plugin version when publishing content updates so existing installations can receive them.

## Companion newsletter

Ship With AI publishes a weekly methodology edition at [shipwithai.substack.com](https://shipwithai.substack.com). Each skill in this repo ships alongside an edition that explains the methodology behind it.
