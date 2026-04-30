#!/usr/bin/env bash
# Install Archon — the open-source harness builder this skill wraps.
# https://github.com/coleam00/Archon
#
# Idempotent: if archon is already on PATH, exits 0 without re-installing.

set -euo pipefail

if command -v archon >/dev/null 2>&1; then
  echo "Archon already installed at $(command -v archon)"
  exit 0
fi

echo "Installing Archon..."

# Try the official one-shot installer first.
if curl -fsSL https://archon.diy/install | bash; then
  if command -v archon >/dev/null 2>&1; then
    echo "Archon installed: $(command -v archon)"
    exit 0
  fi
fi

# Fall back to Homebrew on macOS if the official installer didn't expose archon on PATH.
if [[ "$OSTYPE" == "darwin"* ]] && command -v brew >/dev/null 2>&1; then
  echo "Falling back to Homebrew..."
  brew install coleam00/archon/archon
  if command -v archon >/dev/null 2>&1; then
    echo "Archon installed via Homebrew: $(command -v archon)"
    exit 0
  fi
fi

echo "Archon install failed via both methods." >&2
echo "Please install manually: https://github.com/coleam00/Archon#getting-started" >&2
exit 1
