# Integration Checks

After parallel builds complete, verify all features work together.

---

## Quick Integration Check (5 minutes)

Run these in order. If any fails, generate a fix spec.

### 1. Build Check
```bash
npm run build
```
If this fails, two agents likely created conflicting exports, duplicate type definitions, or incompatible dependency versions. Read the error — it usually points to the exact file.

### 2. Type Check (if TypeScript)
```bash
npx tsc --noEmit
```
Catches: mismatched types between features, missing imports, broken interfaces after parallel modifications.

### 3. Lint Check
```bash
npm run lint
```
Catches: unused imports from deleted code, style violations from different agent preferences.

### 4. Git Diff Review
```bash
git diff --stat
```
Verify: only files expected per the specs were changed. If a file was modified that neither spec mentioned, an agent went off-script. Check its changes.

### 5. Navigation Consistency
If multiple features added pages, verify the navigation component has all new routes. Common issue: two agents both read the nav file at the start of their build, both added their route, but the second agent's write overwrote the first agent's addition.

**Fix pattern:** After parallel builds, run:
```bash
grep -n "href" /path/to/nav-component.tsx
```
Compare against the routes both specs should have added. If one is missing, it was overwritten.

### 6. Database Schema
If multiple features modified the database (migrations, schema changes):
```bash
npx prisma db push --dry-run    # Prisma
npx drizzle-kit push --dry-run  # Drizzle
npx supabase db diff            # Supabase
```
Check for conflicting migrations or duplicate columns.

### 7. Core Flow Test
Run the first-user-test from Issue 05: sign up → core action → verify result. If this still works with all new features, integration is clean.

---

## Common Parallel Build Issues

### Two Agents Modified the Same Utility File
**Symptom:** Build error or missing function.
**Cause:** Both agents read the file at the start, both wrote their version. The second write wins.
**Fix:** Manually merge the changes or generate a spec that combines both additions.

### Duplicate Component Created
**Symptom:** Two similar components in different locations.
**Cause:** Both specs needed a similar component (e.g., a data table). Each agent created its own.
**Fix:** Pick the better one, delete the other, update imports.

### Missing Navigation Entry
**Symptom:** New page exists but doesn't appear in nav.
**Cause:** Navigation file was overwritten by the second agent.
**Fix:** Add the missing route manually or generate a one-line fix spec.

### Conflicting Environment Variables
**Symptom:** One feature works, another doesn't.
**Cause:** One agent set an env variable that another agent's feature also needs but with a different value.
**Fix:** Check `.env.local` for conflicts. Usually one variable name covers both features.

### Import Order / CSS Conflicts
**Symptom:** Styles look wrong on one feature.
**Cause:** Two agents imported CSS or Tailwind classes differently.
**Fix:** Usually resolves with a build. If not, check for conflicting className strings.
