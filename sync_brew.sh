#!/usr/bin/env zsh
set -euo pipefail

WORKSPACE="${DE_WORKSPACE:-$HOME/de_workspace}"
BREWFILE="$WORKSPACE/Brewfile"

echo "=================================================="
echo " Synchronizing Enterprise Workstation via Homebrew "
echo "=================================================="

if [ ! -f "$BREWFILE" ]; then
    echo "[ERROR] Brewfile not found at $BREWFILE"
    exit 1
fi

echo "==> Executing brew bundle..."
brew bundle --file="$BREWFILE"

echo ""
echo "==> Verifying dependency compliance..."
brew bundle check --file="$BREWFILE"

echo ""
echo "==> Purging stale installer caches and orphaned dependencies..."
brew cleanup --prune=all

echo "=================================================="
echo "[SUCCESS] Workstation synchronized and optimized."
