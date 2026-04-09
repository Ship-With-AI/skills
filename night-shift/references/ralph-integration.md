# Ralph Integration

This skill uses Ralph (github.com/snarktank/ralph) for the actual overnight loop. Ralph is battle-tested, has 13.9K stars, and implements the "fresh context per iteration" pattern that prevents quality degradation.

This reference covers:
1. Installing Ralph
2. Converting Issue 03 specs into Ralph's `prd.json` format
3. Configuring Ralph for safe overnight runs
4. Alternative: using Claude Code's native `/loop` feature

---

## Installing Ralph

Ralph is available as a Claude Code plugin:

```bash
# In Claude Code, add the marketplace:
/plugin marketplace add snarktank/ralph

# Install the skills:
/plugin install ralph-skills@ralph-marketplace
```

Or manual install:

```bash
# From the user's project root
mkdir -p scripts/ralph
git clone https://github.com/snarktank/ralph.git /tmp/ralph
cp /tmp/ralph/ralph.sh scripts/ralph/
cp /tmp/ralph/CLAUDE.md scripts/ralph/CLAUDE.md
chmod +x scripts/ralph/ralph.sh
rm -rf /tmp/ralph
```

Ralph requires:
- `jq` (`brew install jq` on macOS, `apt install jq` on Linux)
- A git repository
- Claude Code authenticated

---

## Converting Specs to prd.json

Ralph uses a `prd.json` file with user stories. Our Issue 03 specs convert cleanly with this mapping:

### Issue 03 Spec Format → Ralph User Story

| Issue 03 Spec | Ralph prd.json |
|---------------|----------------|
| `# Feature: [Name]` | `"title": "[Name]"` |
| `## Context` bullets | `"context"` field (joined) |
| `## Requirements` numbered list | `"requirements"` array |
| `## Constraints` Do NOT list | `"constraints"` array |
| `## Acceptance` checkboxes | `"tests"` array (verification steps) |
| `## Edge Cases` | `"edge_cases"` array |

### Conversion Example

**Input (Issue 03 spec at `/specs/feature-response-analytics.md`):**

```markdown
# Feature: Response Analytics Dashboard

## Context
- Responses currently display as a raw list at /app/forms/[id]/responses/page.tsx
- Data lives in the responses table (id, form_id, answers, created_at, completed_at)

## Requirements
1. Add analytics summary at the top of the responses page
2. Show: total responses, completion rate, responses over time (last 7 days)
3. Use existing chart components from /components/ui/ if available
4. Data from responses table — aggregate with SQL, don't compute client-side

## Constraints
- Do NOT add individual user tracking
- Do NOT install a new charting library if one exists
- Do NOT move or modify the existing response list

## Acceptance
- [ ] Analytics summary appears above the response list
- [ ] Total count matches actual responses in database
- [ ] Completion rate is accurate (completed_at not null / total)
- [ ] Time chart shows last 7 days of responses
```

**Output (appended to `prd.json`):**

```json
{
  "branchName": "night-shift/2026-04-07",
  "userStories": [
    {
      "id": "feature-response-analytics",
      "priority": 1,
      "title": "Response Analytics Dashboard",
      "context": "Responses currently display as a raw list at /app/forms/[id]/responses/page.tsx. Data lives in the responses table (id, form_id, answers, created_at, completed_at).",
      "requirements": [
        "Add analytics summary at the top of the responses page",
        "Show: total responses, completion rate, responses over time (last 7 days)",
        "Use existing chart components from /components/ui/ if available",
        "Data from responses table — aggregate with SQL, don't compute client-side"
      ],
      "constraints": [
        "Do NOT add individual user tracking",
        "Do NOT install a new charting library if one exists",
        "Do NOT move or modify the existing response list"
      ],
      "tests": [
        "Analytics summary appears above the response list",
        "Total count matches actual responses in database",
        "Completion rate is accurate (completed_at not null / total)",
        "Time chart shows last 7 days of responses"
      ],
      "passes": false
    }
  ]
}
```

The `passes: false` flag tells Ralph this story isn't complete yet. Ralph picks the highest-priority `passes: false` story, builds it, runs tests, and sets `passes: true` when done.

### Conversion Script

The skill can generate this programmatically. If doing it manually, the key rules:
- Priority 1 is highest
- Order stories by dependency (Issue 09's `analyze_deps.py` helps here)
- Keep `branchName` unique per run (date-based works)
- Requirements and tests should be copy-paste from the spec — no rewording

---

## Configuring Ralph for Overnight Safety

Ralph's default configuration is permissive — it's built for hands-on development. For overnight runs, add these safeguards to the generated `prd.json`:

```json
{
  "branchName": "night-shift/2026-04-07",
  "maxIterations": 8,
  "config": {
    "killConditionsFile": "/.night-shift/kill-conditions.json",
    "allowedPaths": [
      "/app/forms/**",
      "/components/ui/**"
    ],
    "blockedPaths": [
      "/app/api/auth/**",
      "/prisma/migrations/**",
      ".env*",
      "package.json"
    ],
    "preIterationChecks": [
      "test -f /.night-shift/ABORT && exit 0",
      "git diff --name-only | grep -qv '^\\(app/forms\\|components/ui\\)' && exit 1 || true"
    ],
    "postIterationChecks": [
      "npm test || exit 1",
      "npx tsc --noEmit || exit 1"
    ]
  },
  "userStories": [ ... ]
}
```

The `preIterationChecks` run at the start of each Ralph iteration. They check:
- The kill switch file (`/.night-shift/ABORT`) — if present, exit cleanly
- No files modified outside allowed scope — if so, exit with error

The `postIterationChecks` run after each completed story. They verify:
- All tests still pass
- Typecheck still passes

If any check fails, Ralph's loop exits and the story is marked incomplete.

### Ralph's CLAUDE.md for Overnight Mode

Ralph uses a `CLAUDE.md` file as the prompt template. For overnight runs, customize it to emphasize safety:

```markdown
You are running in OVERNIGHT AUTONOMOUS MODE.

RULES:
1. Before modifying any file, check that it's in the `allowedPaths` list.
2. Do NOT install new dependencies. If a dependency is missing, mark the story 
   as failed and move on.
3. Do NOT modify files in `blockedPaths`. If you think you need to, skip the story.
4. After every file modification, run `npm test`. If tests fail, try to fix in 
   at most 2 iterations. If still failing, mark the story failed and move on.
5. If you encounter the same error 3 times in a row, mark the story failed and 
   move on. Do not attempt a 4th fix.
6. Append learnings to `progress.txt` after each story — what worked, what 
   didn't, and why. This runs before the next agent reads it.
7. NEVER modify git config, CI workflows, or environment files.
8. NEVER use `git push --force` or `git reset --hard` on the main branch.

If you're uncertain about anything, SKIP the story. A skipped story is much 
better than corrupted code.

The human will review everything in the morning. They'd rather see 3 completed 
stories and 2 skipped than 5 stories with subtle bugs.
```

---

## Running the Loop

Once `prd.json` is configured and the pre-flight check passes, start the loop:

```bash
# Background the process so the terminal can close
nohup ./scripts/ralph/ralph.sh --tool claude 8 > /.night-shift/ralph.log 2>&1 &

# Or in a screen/tmux session:
screen -dmS night-shift ./scripts/ralph/ralph.sh --tool claude 8
```

The `8` is the max iteration count. Ralph stops when all stories pass OR it hits max iterations OR a kill condition triggers.

Tell the user:

```
Loop started in background. Sleep well.

To check progress (if you wake up):
  tail -f /.night-shift/ralph.log

To abort the loop:
  bash /.night-shift/kill.sh

In the morning, say:
  "review last night's work"
```

---

## Alternative: Claude Code's Native `/loop` Feature

Claude Code has a native `/loop` command (as of 2026) that provides similar functionality without Ralph. Pros and cons:

| Feature | Ralph | Claude Code `/loop` |
|---------|-------|---------------------|
| Fresh context per iteration | ✅ Yes | ✅ Yes |
| Progress persistence | ✅ via progress.txt | ✅ via session memory |
| Custom kill conditions | ✅ via shell checks | ⚠️ Limited |
| Setup effort | Medium (clone + configure) | Low (built-in) |
| Battle-tested | ✅ 13.9K stars, many users | Newer, fewer reports |
| Works with plain shell scripts | ✅ Yes | ❌ Requires Claude Code |

**Recommendation:** Use Ralph for overnight runs because the shell-based kill conditions are more reliable for unattended operation. Use `/loop` for shorter supervised sessions where you can monitor the screen.

If using `/loop`, the config is simpler:

```
/loop --specs /specs/feature-response-analytics.md --max-iterations 8 --stop-on-test-failure
```

But you lose some guardrail flexibility. Worth it if Ralph feels like too much setup for a first try.

---

## Troubleshooting

**"Ralph exited immediately"** — Check `progress.txt`. Usually means the pre-iteration check failed (dirty git, failing tests) or the kill switch file existed.

**"Ralph ran forever on one story"** — The story was too big. Break it down. Ralph's fresh-context model assumes each story fits in a single context window (roughly 3-5 files, 100-200 lines of changes).

**"Ralph completed but the code is wrong"** — The acceptance criteria weren't tight enough. Rewrite the spec with more specific `tests` and try again.

**"Ralph stopped at iteration 3 of 8"** — It hit a kill condition. Check the logs for which one. Usually means the story had an ambiguity the agent couldn't resolve.
