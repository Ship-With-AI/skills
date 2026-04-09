# Night Shift Checklist

Track every overnight run. Update during PREPARE and REVIEW.

---

## PREPARE (before bed)

**Date:** 
**Sleep window:** 
**Run number:** [First / 2nd / 3rd...]

### Pre-Flight Check
- [ ] Git working tree is clean (committed or stashed)
- [ ] On a feature branch (NOT main/master)
- [ ] Tests currently pass
- [ ] Typecheck passes (if applicable)
- [ ] Pre-sleep checkpoint committed: `git log -1`

### Specs Selected
| # | Spec | Complexity | Touches Critical? | Est. Iterations |
|---|------|------------|-------------------|-----------------|
| 1 | | simple / medium / complex | yes / no | |
| 2 | | | | |

**First-run limit:** 1 spec, 1-2 hours (nap run).
**After 3 successful runs:** Up to 3 specs, 4 hours (half-night).
**After 10 successful runs:** Up to 5 specs, full 8 hours.

### Guardrails Generated
- [ ] Allowed scope defined (only files from the specs)
- [ ] Blocked scope includes: `/app/api/auth/**`, `/prisma/migrations/**`, `.env*`, `package.json` deps
- [ ] Kill conditions set (tests fail × 2, same error × 3, scope violation, >20 files)
- [ ] Max iterations: 
- [ ] Wall-clock cap: 
- [ ] Kill switch ready: `/.night-shift/kill.sh`

### Final Sanity Check
- [ ] I would be okay if NOTHING got built (this is a calibration run)
- [ ] I have a plan for tomorrow morning's review
- [ ] Ralph (or /loop) is configured
- [ ] Loop started in background: `tail -f /.night-shift/ralph.log` to monitor

**Started at:** 
**Kill switch:** `bash /.night-shift/kill.sh`

---

## REVIEW (in the morning)

**Woke up at:** 
**Total runtime:** 

### Outcome
- [ ] ✅ SHIPPED — all specs done, tests pass, no violations
- [ ] ⚠️ PARTIAL — some specs done, some not
- [ ] 🔄 STUCK — loop got stuck early
- [ ] 🚨 DRIFTED — scope violations, reset needed
- [ ] ❌ NO_RUN — loop didn't run at all

### Metrics
| Metric | Value |
|--------|-------|
| Commits made | |
| Files modified | |
| Scope violations | |
| Tests before | |
| Tests after | |
| Specs completed | |
| Kill condition triggered | |

### Completed Specs
- [ ] Spec 1: [name] — [outcome]
- [ ] Spec 2: [name] — [outcome]

### Morning Actions
- [ ] Reviewed git diff against each spec's acceptance criteria
- [ ] Merged completed specs to working branch
- [ ] Reverted failed or partial specs
- [ ] Read `progress.txt` for agent's learnings
- [ ] Identified what caused any failures
- [ ] Archived run artifacts: `mv /.night-shift /.night-shift/archive/[date]`

### Lessons for Next Time
- **What worked:** 
- **What didn't:** 
- **Guardrail updates needed:** 
- **Specs that need rewriting:** 

### Deploy Decision
- [ ] Deploy completed work now (`npx vercel --prod`)
- [ ] Wait — needs manual verification first
- [ ] Hold — too many issues, fix before deploying

---

## Run History (cumulative)

| # | Date | Specs | Runtime | Outcome | Notes |
|---|------|-------|---------|---------|-------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

After 5 runs, review patterns. Which spec types succeed? Which fail? Adjust your writing of specs accordingly.
