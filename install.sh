#!/usr/bin/env bash
set -euo pipefail
# One-line installer for claude-keepalive
# Usage: curl -fsSL https://raw.githubusercontent.com/fabiocicerchia/claude-keepalive/main/install.sh | bash

DEST="${DEST:-$HOME/.local/bin}"
mkdir -p "$DEST"
curl -fsSL "https://raw.githubusercontent.com/fabiocicerchia/claude-keepalive/main/claude-keepalive.py" \
  -o "$DEST/claude-keepalive"
chmod +x "$DEST/claude-keepalive"

echo "claude-keepalive installed to $DEST/claude-keepalive"
case ":$PATH:" in
  *":$DEST:"*) ;;
  *) echo "Add $DEST to your PATH to run it as 'claude-keepalive'." ;;
esac
