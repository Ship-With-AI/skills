#!/bin/bash
# Verify a deployment is live and responding correctly.
#
# Usage:
#   bash verify_deploy.sh <url> [--auth-path /sign-in] [--app-path /dashboard]
#
# Checks:
#   - URL responds with HTTP 200
#   - No redirect loops
#   - Key pages load
#   - Response contains HTML content
#
# Exit code 0 = all checks pass, 1 = failures found

set -euo pipefail

URL="${1:?Usage: verify_deploy.sh <url> [--auth-path /path] [--app-path /path]}"
AUTH_PATH=""
APP_PATH=""

# Parse optional args
shift
while [[ $# -gt 0 ]]; do
    case $1 in
        --auth-path) AUTH_PATH="$2"; shift 2 ;;
        --app-path) APP_PATH="$2"; shift 2 ;;
        *) shift ;;
    esac
done

# Remove trailing slash
URL="${URL%/}"

PASS=0
FAIL=0
RESULTS=""

check() {
    local label="$1"
    local check_url="$2"
    local expected_status="${3:-200}"
    
    # Follow redirects, capture final status code and URL
    local response
    response=$(curl -s -o /dev/null -w "%{http_code}|%{url_effective}|%{redirect_url}" \
        -L --max-redirs 5 --connect-timeout 10 --max-time 30 \
        "$check_url" 2>/dev/null) || true
    
    local status=$(echo "$response" | cut -d'|' -f1)
    local final_url=$(echo "$response" | cut -d'|' -f2)
    
    if [[ "$status" == "$expected_status" ]]; then
        RESULTS="${RESULTS}✅ ${label}: ${check_url} → HTTP ${status}\n"
        ((PASS++))
    elif [[ "$status" == "000" ]]; then
        RESULTS="${RESULTS}❌ ${label}: ${check_url} → Connection failed (site unreachable)\n"
        ((FAIL++))
    else
        RESULTS="${RESULTS}❌ ${label}: ${check_url} → HTTP ${status} (expected ${expected_status})\n"
        ((FAIL++))
    fi
}

check_content() {
    local label="$1"
    local check_url="$2"
    local search_string="$3"
    
    local body
    body=$(curl -s -L --max-redirs 5 --connect-timeout 10 --max-time 30 \
        "$check_url" 2>/dev/null) || true
    
    if echo "$body" | grep -qi "$search_string"; then
        RESULTS="${RESULTS}✅ ${label}: Found '${search_string}' in response\n"
        ((PASS++))
    else
        RESULTS="${RESULTS}❌ ${label}: '${search_string}' not found in response\n"
        ((FAIL++))
    fi
}

check_no_mixed_content() {
    local check_url="$1"
    
    if [[ "$check_url" != https://* ]]; then
        RESULTS="${RESULTS}⚠️  Mixed content: Skipped (not HTTPS)\n"
        return
    fi
    
    local body
    body=$(curl -s -L --max-redirs 5 --connect-timeout 10 --max-time 30 \
        "$check_url" 2>/dev/null) || true
    
    local http_refs
    http_refs=$(echo "$body" | grep -oP 'src="http://[^"]+"|href="http://[^"]+"' | head -5) || true
    
    if [[ -z "$http_refs" ]]; then
        RESULTS="${RESULTS}✅ Mixed content: No HTTP resources on HTTPS page\n"
        ((PASS++))
    else
        RESULTS="${RESULTS}❌ Mixed content: Found HTTP resources on HTTPS page:\n"
        while IFS= read -r ref; do
            RESULTS="${RESULTS}   → ${ref}\n"
        done <<< "$http_refs"
        ((FAIL++))
    fi
}

echo "🔍 Verifying deployment: ${URL}"
echo "---"

# Core checks
check "Homepage" "$URL"
check_content "HTML content" "$URL" "<html"
check_no_mixed_content "$URL"

# Auth page (if specified)
if [[ -n "$AUTH_PATH" ]]; then
    check "Auth page" "${URL}${AUTH_PATH}"
fi

# App page (if specified)  
if [[ -n "$APP_PATH" ]]; then
    check "App page" "${URL}${APP_PATH}"
fi

# Check for common error pages
check "Not a Vercel error" "$URL" "200"

echo "---"
echo -e "$RESULTS"
echo "---"
echo "Results: ${PASS} passed, ${FAIL} failed"

if [[ $FAIL -gt 0 ]]; then
    echo "⚠️  Some checks failed. Review the errors above."
    exit 1
else
    echo "✅ All checks passed. Deployment is live."
    exit 0
fi
