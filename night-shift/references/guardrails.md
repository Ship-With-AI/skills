# Guardrails for Overnight Runs

Guardrails are the difference between waking up to shipped code and waking up to 8 hours of damage. The skill generates guardrails specific to each run, but the patterns below are the foundation.

## The Three Categories

### 1. Scope Guardrails (what the agent can touch)

These are the hardest boundaries. If the agent modifies a file outside the allowed list, abort immediately.

**Allowed list** — only files directly relevant to the spec:
- Files explicitly named in the spec's Requirements section
- New files in directories mentioned in the spec
- Test files for the modified code

**Blocked list** — always off-limits during autonomous runs:
- `/app/api/auth/**` — authentication logic (too risky)
- `/app/api/webhooks/**` — payment webhooks (broken money = bad morning)
- `/prisma/migrations/**`, `/supabase/migrations/**` — DB migrations (irreversible)
- `.env*` — environment variables (credentials)
- `middleware.ts` — request middleware (can break entire app)
- `.github/workflows/**` — CI config (can corrupt deployments)
- `/docs/**` (unless the spec is about docs)
- `package.json` dependencies section (new deps need human review)

**Read-only list** — the agent can read but not write:
- `PROJECT.md`
- `SKILL.md` files in `.claude/skills/`
- Production configuration files

### 2. Kill Conditions (when to abort the loop)

Kill conditions trigger the agent to stop the loop mid-run. Without these, a stuck agent can burn through tokens for hours making things worse.

**Automatic kill conditions (always enabled):**
- Tests fail and can't be fixed in 2 iterations → abort
- Build fails and can't be fixed in 2 iterations → abort
- Same error message appears 3 times → stuck loop, abort
- Agent modifies a file outside the allowed list → drift, abort immediately
- Agent installs a dependency not mentioned in the spec → scope creep, abort
- More than 20 files modified in a single run → scope creep, abort
- Git history branches or diverges unexpectedly → corruption, abort
- Commit count > max_iterations × 3 → too many retries, abort

**Custom kill conditions (spec-specific):**
For each spec, add conditions based on what it's building:
- Settings page spec: abort if agent creates routes outside `/app/settings/`
- API endpoint spec: abort if agent modifies more than the single route file
- UI component spec: abort if agent creates new base components
- Bug fix spec: abort if the diff size exceeds 50 lines

### 3. Budget Guardrails (resource limits)

**Iteration cap**: Max number of retry loops. Default 8. First run: 3.

**Wall-clock cap**: Max runtime. Set to slightly less than actual sleep window (if you sleep 7 hours, cap at 6).

**Token budget** (if your Claude plan has limits):
- Estimate per spec: ~10K tokens per iteration × 3 iterations per spec
- Leave headroom: if you have 100K tokens, cap at 70K

**File budget**: Max files touched. Default 20. If the spec should only touch 3-4 files, cap at 10.

---

## How to Write Good Kill Conditions

Kill conditions must be observable and unambiguous. The agent (or the loop wrapper) needs to detect them without human judgment.

**Good kill conditions:**
- `git diff --stat` shows more than 20 files changed
- The last 3 commit messages are nearly identical (Levenshtein distance < 10)
- `npm test` exits with non-zero status
- A file outside `allowed_paths` appears in `git status`
- `package.json` has more dependencies than at checkpoint
- The same error string appears in the last 3 log entries

**Bad kill conditions** (too subjective, can't be auto-detected):
- "The code looks wrong"
- "The agent seems confused"
- "Something feels off"
- "The approach is different than I expected"

If a kill condition can't be expressed as a script check, it doesn't belong in the guardrails. That's for morning review.

---

## Patterns by Spec Type

### Feature spec (building new functionality)

```yaml
scope:
  allowed:
    - /app/[feature-path]/**
    - /components/[relevant-components]/**
    - tests for the above
  blocked:
    - /app/api/auth/**
    - .env*
    - package.json (deps)
kill_conditions:
  - files_modified > 10
  - tests_failing after 2 retries
  - new dependency added
  - same error × 3
iteration_cap: 5
```

### Fix spec (bug fix, UX change)

```yaml
scope:
  allowed:
    - the specific files mentioned in the spec
    - tests for those files
  blocked:
    - everything else
kill_conditions:
  - files_modified > 4
  - diff size > 100 lines
  - tests_failing after 2 retries
  - new dependency added
iteration_cap: 3
```

### Refactor spec (internal restructuring)

```yaml
scope:
  allowed:
    - /src/[refactor-target]/**
  blocked:
    - /app/api/** (don't touch API contracts)
    - /prisma/**, /supabase/** (don't touch data)
    - .env*
kill_conditions:
  - tests_failing at any point
  - behavior changes (integration tests fail)
  - files_modified > 15
iteration_cap: 4
```

**Special rule for refactors**: tests should PASS throughout, not just at the end. A refactor that breaks tests mid-run is corrupted. Kill immediately.

---

## First-Run Guardrails (extra strict)

For the very first autonomous overnight run, use the strictest possible limits:

```yaml
specs: 1 (maximum)
max_iterations: 3
max_runtime: 1 hour (not 8 — start with a "nap run")
max_files_modified: 5
allowed_paths: [exact files from the single spec only]
blocked_paths: [the default blocked list + any file mentioned in PROJECT.md's critical paths]
kill_on_any_test_failure: true
```

The goal of the first run is to discover what your specific project needs in its guardrails — not to ship code. Treat it as a calibration run. Expect it to fail or abort. Adjust based on what happened.

After 3-5 successful nap runs, expand to a 4-hour half-night run. After 3-5 of those, try full 8-hour overnights.

---

## Updating Guardrails Over Time

After each overnight run, the skill's REVIEW mode suggests guardrail updates. Common adjustments:

- **Tightening** after drift: add the drifted path to blocked, reduce allowed scope
- **Loosening** after false aborts: the kill condition was too sensitive
- **New rules** after novel failures: discovered a new failure mode, add a check for it

Keep a `/.night-shift/guardrails-history.md` file logging these updates so patterns emerge:

```markdown
# Guardrails History

## 2026-04-07
- Added `/lib/email/**` to blocked list (agent tried to modify email templates for a settings spec)
- Tightened iteration cap from 5 to 3 for UI fixes (more than 3 iterations = spec was ambiguous)

## 2026-04-09
- Removed `.env.example` from blocked list (agents legitimately needed to add variables)
- Added kill condition: if commit message contains "revert", count as a retry for stuck detection
```

Over time, your guardrails become project-specific and increasingly reliable.
