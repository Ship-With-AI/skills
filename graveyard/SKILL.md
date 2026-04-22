---
name: graveyard
description: Use this skill whenever the user wants to close out a dead or abandoned side-project repo and turn it into portfolio evidence. Also trigger when the user says "close out my dead repo", "/graveyard", "archive this project properly", "turn this abandoned project into evidence", or "what should I do with this old repo". Takes a repo path or GitHub URL plus a target use-case and a one-sentence real reason-for-stopping, then produces a CLOSED.md with a portfolio paragraph and three rehearsable STAR+R interview stories, plus a closing-commit README section. Human-in-the-loop: shows diffs and waits for explicit approval before committing. Never runs `git push`. Never runs `gh repo archive` without approval.
---

# Graveyard — Close Out Dead Side Projects

Close out a dead or abandoned side-project repo so it becomes permanent evidence instead of hidden shame. One evening. Three interview-ready artifacts. One closing commit.

Ship With AI artifact #23 · post-series adjacent · companion to [Your Dead Side Project Is Your Next Job Interview](https://shipwithai.substack.com/).

## When to run

Invoke when the user:

- Types `/graveyard` or `/graveyard <path-or-url>`
- Asks to "close out," "archive properly," or "document" a dead or abandoned project
- Mentions dead repos they want to turn into portfolio evidence or interview material

Do NOT invoke when the user wants to:

- Revive a dead project (this skill archives; it does not resurrect)
- Delete a repo (deleting destroys evidence — archive instead)
- Review a currently-active project (use `/context-tax` instead)

## Input surface

- `/graveyard` → operate on `cwd` (must be a git repo with at least one commit)
- `/graveyard /abs/path/to/repo` → operate on the given local path
- `/graveyard https://github.com/user/repo` → clone to `/tmp/graveyard-<slug>/` and operate there; the closing commit stays local in `/tmp`; the user pushes manually after review

If `cwd` is not a git repo and no path/URL is given, stop and ask for one.

## Process

### Phase 1 — Discovery (silent, ~15 seconds)

Read, in order, and form an internal picture:

1. `git log --oneline --since='3 years ago'` — find the last meaningful commit date
2. `git log --stat --since='1 year ago' --format='%h %s'` — identify the largest-line-count commits
3. `README.md` — what the project claimed to be
4. `package.json` / `Cargo.toml` / `pyproject.toml` / `go.mod` / `Gemfile` / `requirements.txt` — infer the stack
5. Top-level file tree (`ls -F` equivalent) — what was actually built vs. claimed
6. Last 20 commits' messages — spot any `TODO` / `FIXME` / `WIP:` patterns

Do not print anything to the user during this phase.

If the repo has zero commits, or no `README.md`, stop and print:

> This repo has no archaeology to work from (missing commits or README). Close it out manually, or point the skill at a different repo.

### Phase 2 — Interview (exactly two questions)

Ask these two questions, in this order, and wait for the user to answer each before proceeding. Do **not** ask follow-up questions. Two questions is the budget.

**Q1.** What job, role, or use-case do you want this repo to be evidence for?

> Examples: "senior full-stack engineer at a B2B SaaS," "freelance automation consulting," "a conference talk on domain-specific AI," "portfolio for applying to a bootcamp cohort."

**Q2.** Why did you actually stop? (One sentence. The real reason — not the diplomatic one.)

> Examples: "The auth flow required middleware I couldn't justify for the scope." "I lost interest after the first user survey came back weak." "I ran out of time between a kid's birthday and a day-job deadline."

All other calibration comes from Phase 1 discovery. Do not ask the user for stack, target company, project history, or feature list — you already have those from discovery.

### Phase 3 — Analysis (silent)

Map the project's commit history and file structure to four interview-question categories:

- **Tradeoffs** — decisions with clear alternatives considered
- **Scoping** — moments where the project's scope shifted or failed
- **Debugging** — long-running issues or multi-commit fixes
- **Decision-reversal** — where the project pivoted from a prior approach

Select the **three strongest** stories. Not three — the three *best* — where commit evidence is strongest. Each story must have:

- A specific commit SHA to anchor it
- A clear setup-action-result arc visible in commits or code
- An interview-question category it answers

Draft each story in STAR+Reflection format (Situation, Task, Action, Result, Reflection). Each story: 250–400 words. A two-to-three-minute spoken answer.

Draft the portfolio paragraph (2–4 sentences). Structure: `I built [X] using [Y] to answer [Z]. Shipped [what worked]. Closed at [where it stopped]. Learned [W].` Past-perfect active voice. No apology language.

Draft the README close-out section (see template below).

Draft the commit message. Default: `chore: close out project, document postmortem and evidence`.

### Phase 4 — Output (show diffs, wait for approval)

1. Write `CLOSED.md` to the repo root. If one already exists, print a warning and ask whether to overwrite.
2. Print the full `CLOSED.md` content for the user to review.
3. Print the proposed `README.md` diff — the new `## Status: Closed out on {today}` section appended to the existing README.
4. Print the proposed commit message.
5. Print the final prompt, verbatim:

> Type **go** to stage both files and commit locally. Anything else to edit first.

### Phase 5 — Commit (on explicit "go" only)

On the user's exact reply of `go` (or `commit`, or a clear affirmative like `yes, commit`):

1. Append the new section to `README.md`
2. Run `git add README.md CLOSED.md`
3. Run `git commit -m "{drafted message}"`
4. Print: `Commit made locally. Push manually with 'git push' when ready.`

Do **not** run `git push`. Ever. Under any circumstance.

After the commit, print this one-sentence reminder:

> If this project is definitively closed and the repo lives on GitHub, `gh repo archive {owner}/{repo}` marks it archived (prevents accidental pushes and signals "closed" to viewers). Optional — only run it yourself.

Do **not** run `gh repo archive` automatically.

## Output templates

### CLOSED.md

```markdown
# Status: Closed out — {today as YYYY-MM-DD}

## Portfolio story

{2–4 sentence paragraph. Past-perfect active voice. Names the problem, the technical approach, the signal produced, the lesson walked away with. No apology language.}

## Three rehearsable stories

### Story 1 — {Category, e.g. "Tradeoff I made and later reconsidered"}

**Triggered by:** "Tell me about a time you changed your mind on a technical decision."

**Anchored at:** commit `{sha}` — {one-line commit message}

**Situation.** {100–150 words.}

**Task.** {50 words.}

**Action.** {100–150 words.}

**Result.** {50–75 words.}

**Reflection.** {50 words.}

### Story 2 — {Category}

{Same structure.}

### Story 3 — {Category}

{Same structure.}
```

### README close-out section

```markdown
## Status: Closed out on {today as YYYY-MM-DD}

{One-paragraph postmortem. What I set out to do. How far I got. The specific reason I stopped — use the user's Q2 sentence verbatim, don't editorialize.}

### What this repo is evidence of

- {Specific skill/framework/technique 1, e.g. "Next.js 14 app router + Postgres + Prisma schema work"}
- {Specific skill 2}
- {Specific skill 3}
- {Optional specific skill 4}

### Would I revive this?

{Either: "No. {The original blocker is still true. If I rebuilt it today I'd {different approach}}."
 Or: "Yes, under these specific conditions: {2–3 preconditions that would need to be true}."}
```

## Anti-patterns to avoid

1. **No apology language.** The close-out is evidence, not an apology. If a draft uses `never finished`, `sorry`, `unfortunately`, or `tried to`, rewrite before showing the user.
2. **No auto-push.** Ever. Local commit only. The user runs `git push` when ready.
3. **No revival suggestions unless asked.** This skill archives. Do not nudge the user toward reviving.
4. **No editorializing the Q2 reason.** Use the user's exact sentence in the postmortem. Do not speculate about the "real" reason behind their stated reason.
5. **No more than three stories.** If the repo seems to justify five, pick the three best. Four or more dilutes interview prep.
6. **No stack guessing.** If the stack isn't in package manifests or the README, do not infer — ask the user inside Phase 2. (Exception to the two-question rule: stack clarification if genuinely ambiguous.)
7. **No running `gh repo archive` automatically.** Suggest it once in Phase 5. The user runs it.
8. **No modifying existing README content.** Only append the `## Status: Closed out` section. Never rewrite or reorder existing README sections.

## What "done" looks like

The skill completed successfully when:

- `CLOSED.md` exists at the repo root with a portfolio paragraph and three STAR+R stories
- `README.md` has a closed-out section appended at the bottom
- A local commit exists with the drafted message
- The user has been told to push manually
- The user has been reminded about `gh repo archive` (but not had it run automatically)

The user should now be able to:

- Link the repo from a resume, portfolio page, twitter bio, or email signature
- Walk into any interview with three rehearsable stories they didn't have this morning
- Show recruiters a repo whose README reads as evidence, not as abandoned work

## Start here

Begin with Phase 1 (silent discovery). Output nothing user-facing until Phase 2 (the two questions).
