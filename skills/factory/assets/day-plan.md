# Day Plan — {YYYY-MM-DD}

Total human attention budget: ~90 minutes spread across 12 hours.

The factory ships when the human attention is timed. Skip a window and blocked tickets stay blocked.

- **{HH:MM + 0h} — Standup.** Each agent reports {what shipped / what's blocked / what's next}. Triage: kill, continue, escalate. ~15 minutes.
- **{HH:MM + 4h} — Checkpoint.** Scan audit log + budget burn rate. Reassign blocked tickets. ~15 minutes.
- **{HH:MM + 8h} — Gate review.** Approve DEPLOY transitions across active projects. ~30 minutes.
- **{HH:MM + 12h} — Daily review.** Read audit log. Compute mortality (shipped / paused / killed). Append one rule to portfolio CLAUDE.md `## Lessons`. ~30 minutes.

Between windows: agents work async. You don't watch.

## Standup checklist (paste into the standup window)

For each agent, the CEO reports:

- ✓ Shipped since last standup
- ⏸ Blocked / waiting on
- → Next ticket

Triage the report in 30 seconds per agent:

- **Kill** — feature is out of scope, project is undeliverable
- **Continue** — agent is on track, no intervention needed
- **Escalate** — block is real, needs CTO/CEO routing

## Gate review checklist (paste into the 5pm window)

For every project at the DEPLOY stage:

- Live URL returns 200?
- Done.md acceptance criteria all green?
- Did the agent stay inside scope.md or expand mid-build?
- Approve / reject / revise

## Daily review checklist (paste into the 9pm window)

- Mortality table: how many shipped, paused, killed
- Total agent spend vs. monthly budget cap
- One rule for portfolio CLAUDE.md `## Lessons` (portfolio-shaped, not project-shaped)
- Set or adjust tomorrow's company goal if needed
