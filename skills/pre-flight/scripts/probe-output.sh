#!/usr/bin/env bash
# probe-output.sh — Question 1 of pre-flight
# Test that the live URL returns 2xx, visible CTAs route correctly, and (if a signup form
# is present) that POSTing a synthetic email actually persists a user record.
#
# Usage: probe-output.sh <live-url>
# Output: JSON to stdout (consumed by the skill's Phase 3 synthesis step)
# Exit: 0 if Q1 passes, 1 if Q1 fails. Always emits JSON.

set -uo pipefail

URL="${1:-}"
if [ -z "$URL" ]; then
  echo '{"error":"no URL provided","usage":"probe-output.sh <live-url>"}' >&2
  exit 2
fi

TRACE_DIR="${TRACE_DIR:-./pre-flight-trace}"
mkdir -p "$TRACE_DIR"

TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
TEST_EMAIL="pre-flight+$(date +%s)@example.com"

# --- Probe 1: URL returns 2xx with HTML ---
HTTP_CODE=$(curl -sS -o "$TRACE_DIR/landing.html" -w "%{http_code}" --max-time 15 "$URL" 2>/dev/null || echo "000")
LANDING_BYTES=$(wc -c < "$TRACE_DIR/landing.html" 2>/dev/null | tr -d ' ' || echo "0")
URL_OK="false"
if [[ "$HTTP_CODE" =~ ^2 ]] && [ "$LANDING_BYTES" -gt 500 ]; then
  URL_OK="true"
fi

# --- Probe 2: extract visible href/action targets from landing page ---
ROUTES_CHECKED=()
ROUTES_OK="true"
if [ "$URL_OK" = "true" ]; then
  # Extract internal hrefs (same-origin, non-anchor)
  HOSTLESS_URL=$(echo "$URL" | sed -E 's#^https?://[^/]+##; s#/$##')
  ORIGIN=$(echo "$URL" | sed -E 's#^(https?://[^/]+).*#\1#')
  INTERNAL_HREFS=$(grep -oE 'href="(/[^"#]+|'"$ORIGIN"'/[^"#]+)"' "$TRACE_DIR/landing.html" 2>/dev/null \
    | sed -E 's/^href="//; s/"$//; s#^'"$ORIGIN"'##' \
    | sort -u | head -10)

  while IFS= read -r route; do
    [ -z "$route" ] && continue
    full_url="${ORIGIN}${route}"
    route_code=$(curl -sS -o /dev/null -w "%{http_code}" --max-time 10 "$full_url" 2>/dev/null || echo "000")
    ROUTES_CHECKED+=("$route:$route_code")
    [[ ! "$route_code" =~ ^[23] ]] && ROUTES_OK="false"
  done <<< "$INTERNAL_HREFS"
fi

# --- Probe 3: find a signup form, POST synthetic email, check for persistence signal ---
SIGNUP_TESTED="false"
SIGNUP_OK="unknown"
if [ "$URL_OK" = "true" ]; then
  SIGNUP_ACTION=$(grep -oE '<form[^>]*action="[^"]*"' "$TRACE_DIR/landing.html" 2>/dev/null \
    | head -1 \
    | grep -oE 'action="[^"]*"' \
    | sed 's/action="//; s/"$//')
  if [ -n "$SIGNUP_ACTION" ]; then
    if [[ "$SIGNUP_ACTION" =~ ^https?:// ]]; then
      SIGNUP_URL="$SIGNUP_ACTION"
    elif [[ "$SIGNUP_ACTION" =~ ^/ ]]; then
      SIGNUP_URL="${ORIGIN}${SIGNUP_ACTION}"
    else
      SIGNUP_URL=""
    fi
    if [ -n "$SIGNUP_URL" ]; then
      SIGNUP_RESPONSE=$(curl -sS -X POST \
        -H "Content-Type: application/x-www-form-urlencoded" \
        --data-urlencode "email=$TEST_EMAIL" \
        --max-time 15 \
        -w "\n--HTTP_CODE:%{http_code}" \
        "$SIGNUP_URL" 2>/dev/null || echo "")
      SIGNUP_CODE=$(echo "$SIGNUP_RESPONSE" | grep -oE 'HTTP_CODE:[0-9]+' | sed 's/HTTP_CODE://')
      SIGNUP_BODY=$(echo "$SIGNUP_RESPONSE" | sed '/--HTTP_CODE:/d')
      SIGNUP_TESTED="true"
      # Heuristic: 2xx + body containing user_id|userId|id|token|confirm = looks persisted
      if [[ "$SIGNUP_CODE" =~ ^2 ]] && echo "$SIGNUP_BODY" | grep -qiE '(user[_-]?id|"id":|token|confirm|verification|sent)'; then
        SIGNUP_OK="true"
      else
        SIGNUP_OK="false"
      fi
    fi
  fi
fi

# --- Verdict ---
Q1_PASS="false"
if [ "$URL_OK" = "true" ] && [ "$ROUTES_OK" = "true" ] && [ "$SIGNUP_OK" != "false" ]; then
  Q1_PASS="true"
fi

# --- JSON output ---
ROUTES_JSON=$(printf '%s\n' "${ROUTES_CHECKED[@]}" | awk 'BEGIN{print "["} NR>1{print ","} {split($0,a,":"); printf "{\"route\":\"%s\",\"http\":%s}", a[1], a[2]} END{print "]"}' | tr -d '\n')

cat <<EOF
{
  "question": 1,
  "timestamp": "$TS",
  "url": "$URL",
  "checks": {
    "url_returns_2xx": $URL_OK,
    "http_code": "$HTTP_CODE",
    "landing_bytes": $LANDING_BYTES,
    "internal_routes_ok": $ROUTES_OK,
    "internal_routes": $ROUTES_JSON,
    "signup_tested": $SIGNUP_TESTED,
    "signup_persisted": "$SIGNUP_OK",
    "synthetic_email": "$TEST_EMAIL"
  },
  "pass": $Q1_PASS,
  "trace_files": {
    "landing_html": "$TRACE_DIR/landing.html"
  }
}
EOF

# Persist same JSON to disk
cat > "$TRACE_DIR/q1-output.json" <<EOF
{"question":1,"timestamp":"$TS","url":"$URL","url_returns_2xx":$URL_OK,"http_code":"$HTTP_CODE","internal_routes_ok":$ROUTES_OK,"signup_tested":$SIGNUP_TESTED,"signup_persisted":"$SIGNUP_OK","pass":$Q1_PASS}
EOF

[ "$Q1_PASS" = "true" ] && exit 0 || exit 1
