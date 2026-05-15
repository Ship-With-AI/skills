# Pre-flight report — {PROJECT_NAME}

**Verdict: {VERDICT}** _(generated {TIMESTAMP_ISO})_

{VERDICT_HINT}

---

## The 4 questions

| # | Question | Result |
|---|---|---|
| 1 | Does the URL actually work? | {Q1_RESULT} |
| 2 | Can one user complete the core flow? | {Q2_RESULT} |
| 3 | Does each promise resolve to working code? | {Q3_RESULT} |
| 4 | Are you still shipping the original idea? | {Q4_RESULT} |

---

## Top 3 blockers _(impact × effort, descending)_

{BLOCKERS_TABLE}

---

## Question 1 — Output

{Q1_DETAILS}

## Question 2 — Trace

{Q2_DETAILS}

Screenshots: `pre-flight-trace/screens/`

## Question 3 — Component

{Q3_DETAILS}

## Question 4 — Drift

{Q4_DETAILS}

---

## Next moves

- **If SHIP** → send the DM to {FIRST_USER_TARGET}. The product matches the promise. The flow works.
- **If FIX** → fix the 3 blockers above in order, then re-run `/pre-flight`. Expected time-to-clear: {TIME_TO_FIX_ESTIMATE}.
- **If REBUILD** → drift is severe (see Question 4 details). Decide: revert to the original `idea.md` and rebuild, or document the new product as v2 and rewrite the landing page to match it.

---

_Raw eval data: `pre-flight-trace/q1-output.json` · `q2-trace.json` · `q3-component.json` · `q4-drift.json`_
