---
name: steering-loop
description: Use this skill whenever the user wants to scaffold an agent harness (guides + sensors + steering-log) inside a side project, then iterate it one rep at a time. Also trigger when the user says "/steering-loop", "scaffold a harness for this project", "set up agent steering", "build the harness that compounds", "start a steering loop", "iterate the guide for my agent", or asks how to practice the WHAT/WHY/HOW skill stack on a real project. Takes a project directory plus four questions (which agent, which framework, one named first user, kill condition) and scaffolds a `harness/` directory containing `guides/CLAUDE.md` (feedforward), `sensors/eval.md` (feedback), `steering-log.md` (the iteration record), `RUN_REP.md` (the cheat sheet), and `README.md`. Human-in-the-loop: shows the scaffold plan and waits for explicit "go" before writing files. Never overwrites an existing `harness/` without `--reset` + explicit consent. Never auto-runs the agent.
---

# Steering Loop — Build & Iterate Your Agent Harness

Scaffold an agent harness inside any side project, then iterate it one rep at a time. Five moves per rep: Read → Guide → Run → Sense → Log. The harness compounds across Saturdays; the side project is where you practice the skill before your day job rewrites itself around it.

Ship With AI artifact #24 · post-LtM cadence · companion to [How One Side Project Teaches You The 2026 Engineering Job](https://shipwithai.substack.com/).

## When to run

Invoke when the user:

- Types `/steering-loop` or `/steering-loop <path>`
- Asks to "scaffold a harness," "set up steering," or "build a guides + sensors structure"
- Wants to practice the WHAT/WHY/HOW agent-direction skill on a real side project
- Has a fresh project directory and wants the steering scaffold before the first agent run
- Has an existing project with a scattered `CLAUDE.md` or `.cursorrules` they want consolidated into a portable `harness/`

Do NOT invoke when the user wants to:

- Run a one-off agent task (just hand the agent a ticket — no harness needed)
- Build a multi-agent factory (use `/factory` — that scaffolds the org chart)
- Run eval-only checks on a finished project (use `/pre-flight` — that's the gate before sending the first-user DM)
- Close out a dead project (use `/graveyard`)

## Input surface

- `/steering-loop` → operate on `cwd` (need not be a git repo)
- `/steering-loop /abs/path/to/project` → operate on the given local path
- `/steering-loop --reset` → re-scaffold an existing `harness/`. Backs up the existing directory to `harness.bak-{YYYY-MM-DD}/` first. Requires explicit confirmation.

If `cwd` is empty (no `package.json`, no `README.md`, no source files), stop and ask whether the user wants to scaffold a harness for a project that doesn't exist yet, or point the skill at a real project directory.

## Process

### Phase 1 — Discovery (silent, ~15 seconds)

Read, in order, and form an internal picture:

1. `ls -F` at the project root — top-level structure
2. `package.json` / `Cargo.toml` / `pyproject.toml` / `go.mod` / `Gemfile` / `requirements.txt` — infer the stack
3. `README.md` — what the project claims to be
4. Any existing `CLAUDE.md` / `AGENTS.md` / `.cursorrules` / `.cursor/rules/` — existing guide content (will be referenced, not overwritten)
5. Any existing `tests/`, `__tests__/`, `spec/` directories — existing sensor coverage
6. Last 10 git commits (if it's a git repo) — recent shape of changes

Do not print anything to the user during this phase.

If a `harness/` directory already exists at the project root, stop and ask:

> A `harness/` already exists at the project root. Run `/steering-loop --reset` to back it up and re-scaffold, or run with no flag inside an existing harness to append a new entry to `steering-log.md`. Which?

### Phase 2 — Interview (exactly four questions)

Ask these four questions, one at a time, waiting for each answer before proceeding. Do not ask follow-up questions. Four is the budget.

**Q1.** Which agent are you steering?

> Examples: "Claude Code," "Cursor agent mode," "Codex CLI," "Aider," "Gemini CLI."

The answer determines the primary guide filename (`CLAUDE.md` for Claude, `AGENTS.md` for Codex/Cursor, etc.) and which symlinks to create for cross-agent portability.

**Q2.** Which framework or stack are you working in?

> Examples: "Next.js 15 + Drizzle + Postgres," "FastAPI + SQLAlchemy + Postgres," "SvelteKit + Supabase," "vanilla TypeScript + Node + Vitest."

The answer seeds the starter guide with stack-specific defaults (test runner, linting, framework patterns).

**Q3.** Who is the one named first user you're aiming this project at?

> Examples: "a developer friend who builds n8n workflows for clients," "my past self six months ago," "two specific PMs at a target company," "myself but on weekends."

The answer seeds `sensors/eval.md` with first-user-specific gates.

**Q4.** What's your kill condition?

> Examples: "If I've spent 4 Saturdays and the first user still says 'I don't get it,' I kill the project." "If the third Saturday's pre-flight returns REBUILD, I pivot or stop." "I'll keep going as long as something ships every weekend; the day nothing ships, I revisit scope."

The kill condition gets written verbatim into `RUN_REP.md` as the loop's exit gate. No kill condition = no harness — without it, the loop runs forever. If the user resists, explain why and ask again. Do not proceed without an answer.

### Phase 3 — Scaffold plan (show, then wait for "go")

Print the proposed `harness/` directory structure, with the first line of each file's content as preview:

```
harness/
├── README.md                      → "What's in this directory and how to use it."
├── RUN_REP.md                     → "Read → Guide → Run → Sense → Log. Five moves per rep."
├── guides/
│   └── CLAUDE.md                  → "## Stack defaults\n- Next.js 15 app router\n- Drizzle ORM..."
├── sensors/
│   └── eval.md                    → "## First-user eval (named: Alex, n8n freelancer)\n- [ ] URL works..."
└── steering-log.md                → "| date | guide change | sensor caught |\n| --- | --- | --- |"
```

Print the proposed `harness/guides/CLAUDE.md` content in full (the user needs to see the starter rules before they're written).

Print the final prompt, verbatim:

> Type **go** to scaffold the harness into your project. Anything else to revise the plan first.

### Phase 4 — Scaffold (on explicit "go" only)

On the user's exact reply of `go` (or `scaffold`, or a clear affirmative like `yes, scaffold`):

1. Create `harness/` directory and the `guides/` and `sensors/` subdirectories
2. Write each file with its full starter content (templates below)
3. If the agent name from Q1 is not Claude Code, also create the appropriate symlink (e.g., `harness/guides/AGENTS.md` → `harness/guides/CLAUDE.md`) for cross-agent portability
4. If the project has an existing `CLAUDE.md` at the root, leave it alone. Print:

> Your root `CLAUDE.md` was not modified. The new starter is at `harness/guides/CLAUDE.md`. After your first rep, copy any rules you want from the root file into the harness guide, then archive the root file.

5. Print:

> Harness scaffolded at `harness/`. Read `harness/RUN_REP.md` for the loop. Hand a ticket to your agent. Come back after the first rep to update the guide.

### Phase 5 — First rep walkthrough (optional, on request only)

If the user asks "walk me through the first rep" or "show me how to use this":

1. Print the Read → Guide → Run → Sense → Log loop in order
2. Suggest a starter ticket small enough to surface a guide-iteration moment on the first rep (e.g., "scaffold the signup form" or "wire the first API route")
3. Wait for the user to return after running the rep, then walk them through reading the diff and appending one rule to `harness/guides/CLAUDE.md`
4. Append the user's first rep entry to `harness/steering-log.md` together

Do not auto-run the agent. The agent is the user's tool; the skill orchestrates the loop around it.

## Output templates

### harness/README.md

```markdown
# Harness

The system around your AI agent. Three pieces:

- `guides/` — feedforward. What the agent should know before it starts. Your CLAUDE.md, your system prompt, your project rules. One rule added per rep.
- `sensors/` — feedback. What you check after the agent runs. Your evals, your tests, your output checks.
- `steering-log.md` — the iteration record. One line per rep: date, what changed in the guide, what the sensor caught.

The loop: Read → Guide → Run → Sense → Log. See `RUN_REP.md` for the cheat sheet.
```

### harness/RUN_REP.md

```markdown
# One Rep

## Read
Read what the agent wrote in the last run. Read, not skim. If you can't read the code, code-literacy is the floor under this loop — see `harness/guides/CLAUDE.md` § "Read what they write."

## Guide
Open `harness/guides/CLAUDE.md`. Add one rule that would have prevented the worst thing the agent did this rep. One rule. Not a refactor.

## Run
Hand the next ticket to the agent. Watch the output, not the keystrokes.

## Sense
Pass the output through `harness/sensors/eval.md`. Minimum sensor: did it ship what the spec said? Richer sensor: does it pass `/pre-flight`?

## Log
Append one line to `harness/steering-log.md`. Date, guide change, sensor catch.

## Kill condition
{user's Q4 answer verbatim — never paraphrase}
```

### harness/guides/CLAUDE.md

```markdown
# Project rules for {agent name from Q1}

## Stack defaults

{Seeded from Phase 1 discovery + Q2. Framework, test runner, lint, package manager.
Example for Next.js 15 + Drizzle + Postgres:
- Next.js 15 app router (no pages router)
- Drizzle ORM for all DB access; never raw SQL
- Postgres via Supabase; magic-link auth via Resend by default
- Vitest for tests; tsc --noEmit before every commit}

## Read what they write

Code-literacy is the floor under WHAT/WHY/HOW. Before approving any agent output, read the diff. If you can't tell what changed, the rep doesn't count.

## Rules added per rep

{Empty. One rule per rep gets added below. Each rule is one sentence. Each rule is reactive to a specific thing the agent did wrong in the prior rep.}
```

### harness/sensors/eval.md

```markdown
# Sensors

## First-user eval (named: {user's Q3 answer verbatim})

- [ ] URL works for this user
- [ ] User flow completes end-to-end
- [ ] Promises on landing page resolve to real code
- [ ] Idea hasn't drifted from session 1
- [ ] Steering log received a new entry this rep

## Notes

{Empty. After each rep, note what the sensor caught.}
```

### harness/steering-log.md

```markdown
# Steering log

| date | guide change | sensor caught |
| --- | --- | --- |
```

## Anti-patterns to avoid

1. **No auto-running the agent.** The skill scaffolds the harness; the user hands tickets to the agent. Never invoke the agent on behalf of the user.
2. **No overwriting an existing `harness/` without `--reset` + explicit confirmation.** If `harness/` exists, the skill stops and asks. The reset flag backs up to `harness.bak-{YYYY-MM-DD}/`.
3. **No skipping the kill condition (Q4).** A harness without a kill condition is a Sunday-night infinite loop. If the user resists, explain why once and ask again. Do not scaffold without it.
4. **No editorializing the user's kill condition.** Write Q4 verbatim into `RUN_REP.md`. Do not soften or "improve" their language — kill conditions only work when they're the user's own words.
5. **No mixing stack defaults with reactive rules.** Stack defaults go under `## Stack defaults` in the guide. Rules added during reps go under `## Rules added per rep`. Mixing the two pollutes the log and makes it impossible to tell which rules came from which rep.
6. **No naming the agent in the file system if avoidable.** Use the canonical filename for the named agent (`CLAUDE.md` for Claude, `AGENTS.md` for Codex/Cursor) and add symlinks for cross-agent portability. The harness should keep working if the user switches agents.
7. **No auto-running `/pre-flight` from inside `/steering-loop`.** The sensor file references `/pre-flight` as the richer eval; the user runs it separately when they're ready to ship.

## What "done" looks like

The skill completed successfully when:

- `harness/` exists at the project root with all five expected files
- `harness/guides/CLAUDE.md` is pre-populated with stack defaults derived from discovery + Q2
- `harness/sensors/eval.md` names the user's first user verbatim from Q3
- `harness/RUN_REP.md` contains the user's kill condition verbatim from Q4
- `harness/steering-log.md` exists with the header row, ready for entry 1
- The user knows where to go next: read `RUN_REP.md`, hand a ticket to the agent, come back for the first rep update

The user should now be able to:

- Hand the first ticket to their agent and execute one full Read → Guide → Run → Sense → Log rep
- Append one rule to `harness/guides/CLAUDE.md` after the first rep
- Append one row to `harness/steering-log.md` after each rep
- Carry the same `harness/` structure into their next side project (the stack defaults change per project; the loop structure and the read-what-they-write rule don't)

## Start here

Begin with Phase 1 (silent discovery). Output nothing user-facing until Phase 2 (the four questions).
