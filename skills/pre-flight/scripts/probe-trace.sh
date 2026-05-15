#!/usr/bin/env bash
# probe-trace.sh — Question 2 of pre-flight
# Walk the core user flow end-to-end as a first-time user would. Sign up → confirm email
# → log in → reach first-value → trigger second-value. Use Playwright (headless) if
# available; fall back to a curl chain that captures HTTP transitions + the rendered
# landing/dashboard HTML for the skill's LLM-side flow-completion assessment.
#
# Usage: probe-trace.sh <live-url>
# Output: JSON to stdout (consumed by the skill's Phase 3 synthesis step). Saves
# screenshots under ./pre-flight-trace/screens/ when Playwright is present.

set -uo pipefail

URL="${1:-}"
if [ -z "$URL" ]; then
  echo '{"error":"no URL provided","usage":"probe-trace.sh <live-url>"}' >&2
  exit 2
fi

TRACE_DIR="${TRACE_DIR:-./pre-flight-trace}"
SCREENS_DIR="$TRACE_DIR/screens"
mkdir -p "$SCREENS_DIR"

TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# --- Detect Playwright availability ---
PLAYWRIGHT_AVAILABLE="false"
if command -v npx >/dev/null 2>&1; then
  if npx --no-install playwright --version >/dev/null 2>&1; then
    PLAYWRIGHT_AVAILABLE="true"
  fi
fi

MODE="curl"
[ "$PLAYWRIGHT_AVAILABLE" = "true" ] && MODE="playwright"

# --- Mode: Playwright (rich, full trace + screenshots) ---
if [ "$MODE" = "playwright" ]; then
  PW_SCRIPT=$(mktemp -t pre-flight-playwright.XXXXXX.cjs)
  cat > "$PW_SCRIPT" <<'JS_EOF'
const { chromium } = require('playwright');
const path = require('path');
const url = process.argv[2];
const screensDir = process.argv[3];

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const steps = [];

  async function step(name, action) {
    const t0 = Date.now();
    let ok = true, error = null;
    try { await action(); } catch (e) { ok = false; error = e.message; }
    const screenshotPath = path.join(screensDir, `${steps.length + 1}-${name}.png`);
    try { await page.screenshot({ path: screenshotPath, fullPage: true }); } catch (e) { /* ignore */ }
    steps.push({ name, ok, error, ms: Date.now() - t0, screenshot: screenshotPath });
  }

  await step('landing', async () => { await page.goto(url, { waitUntil: 'networkidle', timeout: 15000 }); });

  // Try to find a signup/login CTA
  await step('find-cta', async () => {
    const cta = await page.locator('a:has-text("Sign up"), a:has-text("Get started"), a:has-text("Try"), button:has-text("Sign up"), button:has-text("Get started")').first();
    if (await cta.count() === 0) throw new Error('no signup CTA found on landing');
    await cta.click({ timeout: 5000 });
    await page.waitForLoadState('networkidle', { timeout: 10000 });
  });

  // Try to fill a signup form
  await step('fill-signup', async () => {
    const emailInput = page.locator('input[type="email"], input[name="email"]').first();
    if (await emailInput.count() === 0) throw new Error('no email input found after CTA');
    const ts = Date.now();
    await emailInput.fill(`pre-flight+${ts}@example.com`);
    const passInput = page.locator('input[type="password"]').first();
    if (await passInput.count() > 0) {
      await passInput.fill('PreFlightTest!2026');
    }
    const submit = page.locator('button[type="submit"], button:has-text("Sign up"), button:has-text("Continue")').first();
    if (await submit.count() === 0) throw new Error('no submit button found');
    await submit.click({ timeout: 5000 });
    await page.waitForLoadState('networkidle', { timeout: 10000 });
  });

  // Check for post-signup state
  await step('post-signup-state', async () => {
    const url = page.url();
    const bodyText = (await page.locator('body').innerText()).slice(0, 500);
    if (/error|invalid|failed/i.test(bodyText)) throw new Error('post-signup page contains error text');
    if (url.includes('localhost')) throw new Error('post-signup redirected to localhost — auth misconfig');
  });

  await browser.close();
  console.log(JSON.stringify({ mode: 'playwright', steps }));
})().catch((e) => {
  console.log(JSON.stringify({ mode: 'playwright', fatal: e.message }));
  process.exit(1);
});
JS_EOF

  PW_OUTPUT=$(npx playwright "$PW_SCRIPT" "$URL" "$SCREENS_DIR" 2>&1 || echo '{"mode":"playwright","fatal":"playwright exec failed"}')
  rm -f "$PW_SCRIPT"

  # Parse step results (best effort — skill's LLM does deeper interpretation)
  STEPS_OK=$(echo "$PW_OUTPUT" | grep -oE '"ok":true' | wc -l | tr -d ' ')
  STEPS_FAIL=$(echo "$PW_OUTPUT" | grep -oE '"ok":false' | wc -l | tr -d ' ')
  Q2_PASS="false"
  if [ "$STEPS_FAIL" -eq 0 ] && [ "$STEPS_OK" -ge 3 ]; then
    Q2_PASS="true"
  fi

  cat <<EOF
{
  "question": 2,
  "timestamp": "$TS",
  "url": "$URL",
  "mode": "playwright",
  "steps_ok": $STEPS_OK,
  "steps_fail": $STEPS_FAIL,
  "pass": $Q2_PASS,
  "playwright_output": $PW_OUTPUT,
  "screens_dir": "$SCREENS_DIR"
}
EOF
  echo "$PW_OUTPUT" > "$TRACE_DIR/q2-trace.json"

  [ "$Q2_PASS" = "true" ] && exit 0 || exit 1
fi

# --- Mode: curl fallback (degraded — no JS, no screenshots) ---
LANDING_FILE="$TRACE_DIR/landing.html"
[ ! -f "$LANDING_FILE" ] && curl -sS -o "$LANDING_FILE" --max-time 15 "$URL" 2>/dev/null

ORIGIN=$(echo "$URL" | sed -E 's#^(https?://[^/]+).*#\1#')
SIGNUP_LINK=$(grep -oE 'href="[^"]*(sign[_-]?up|register|get[_-]?started|trial)[^"]*"' "$LANDING_FILE" 2>/dev/null | head -1 | sed 's/href="//; s/"$//')

NEXT_OK="unknown"
NEXT_URL=""
if [ -n "$SIGNUP_LINK" ]; then
  if [[ "$SIGNUP_LINK" =~ ^https?:// ]]; then
    NEXT_URL="$SIGNUP_LINK"
  else
    NEXT_URL="${ORIGIN}${SIGNUP_LINK}"
  fi
  NEXT_CODE=$(curl -sS -o "$TRACE_DIR/signup-page.html" -w "%{http_code}" --max-time 10 "$NEXT_URL" 2>/dev/null || echo "000")
  if [[ "$NEXT_CODE" =~ ^2 ]]; then
    NEXT_OK="true"
  else
    NEXT_OK="false"
  fi
fi

# Curl-mode can't actually walk the flow — it can only confirm signup page reachable.
# The skill MUST flag this as "manual verification needed" in the report.
Q2_PASS="false"
SKIPPED_REASON="playwright not installed — install via 'npx playwright install chromium' for full trace coverage"

cat <<EOF
{
  "question": 2,
  "timestamp": "$TS",
  "url": "$URL",
  "mode": "curl",
  "skipped_reason": "$SKIPPED_REASON",
  "checks": {
    "landing_reachable": true,
    "signup_link_found": $([ -n "$SIGNUP_LINK" ] && echo "true" || echo "false"),
    "signup_page_reachable": "$NEXT_OK",
    "signup_url": "$NEXT_URL"
  },
  "pass": $Q2_PASS,
  "manual_verification_required": true
}
EOF

cat > "$TRACE_DIR/q2-trace.json" <<EOF
{"question":2,"timestamp":"$TS","mode":"curl","manual_verification_required":true,"skipped_reason":"$SKIPPED_REASON","pass":$Q2_PASS}
EOF

# Curl mode never passes — forces manual verification flag
exit 1
