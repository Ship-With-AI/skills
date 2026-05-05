#!/usr/bin/env bash
# Install Paperclip — the open-source control plane this skill wraps.
# https://github.com/paperclipai/paperclip
#
# Idempotent: if Paperclip is already running, exits 0 without re-installing.

set -euo pipefail

# Check if Paperclip's API is responding on the default local port.
if curl -fsS -m 2 http://localhost:3100/api/health >/dev/null 2>&1; then
  echo "Paperclip already running on http://localhost:3100"
  exit 0
fi

# Verify Node.js 20+ and pnpm 9.15+ (Paperclip's stated minimums).
if ! command -v node >/dev/null 2>&1; then
  echo "Node.js is required (20+). Install from https://nodejs.org or via your package manager." >&2
  exit 1
fi

NODE_MAJOR=$(node -p "process.versions.node.split('.')[0]")
if [ "$NODE_MAJOR" -lt 20 ]; then
  echo "Node.js 20+ required (found v$NODE_MAJOR). Upgrade and re-run." >&2
  exit 1
fi

if ! command -v pnpm >/dev/null 2>&1; then
  echo "Installing pnpm via corepack..."
  corepack enable
  corepack prepare pnpm@latest --activate
fi

echo "Onboarding Paperclip (this creates ~/.paperclip and starts the local server)..."
npx paperclipai onboard --yes

# Verify the server came up.
sleep 3
if curl -fsS -m 5 http://localhost:3100/api/health >/dev/null 2>&1; then
  echo "Paperclip installed and running on http://localhost:3100"
  echo ""
  echo "Save your API key from the onboard output to PAPERCLIP_KEY env var:"
  echo "  export PAPERCLIP_KEY=<the-key-from-onboard>"
  exit 0
fi

echo "Paperclip onboard completed but server is not responding on :3100." >&2
echo "Check the onboard output for errors and try `npx paperclipai start` manually." >&2
exit 1
