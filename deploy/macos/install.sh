#!/bin/bash
# Install/update NOUS OS local production services on macOS.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TEMPLATES_DIR="$REPO_ROOT/deploy/macos/launchagents"
INSTALL_DIR="$HOME/Library/LaunchAgents"
CLOUDFLARED_CONFIG_SRC="$REPO_ROOT/deploy/cloudflare/nous-os-backend.yml.template"
CLOUDFLARED_CONFIG_DST="$HOME/.cloudflared/nous-os-backend.yml"
UID_NUM=$(id -u)
GUI_DOMAIN="gui/${UID_NUM}"

mkdir -p "$INSTALL_DIR" "$HOME/.cloudflared" "$REPO_ROOT/logs"

PYTHON_BIN="${NOUS_OS_PYTHON:-python3.11}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    echo "[install] Python 3.11 is required; set NOUS_OS_PYTHON to its executable."
    exit 1
fi
"$PYTHON_BIN" -m venv "$REPO_ROOT/.venv"
"$REPO_ROOT/.venv/bin/pip" install -e "$REPO_ROOT"

sed "s|{{HOME}}|$HOME|g" "$CLOUDFLARED_CONFIG_SRC" > "$CLOUDFLARED_CONFIG_DST"
echo "[install] wrote $CLOUDFLARED_CONFIG_DST"

DEFAULT_SERVICES=(webbackend cloudflared)

if [[ $# -gt 0 ]]; then
    SERVICES=("$@")
else
    SERVICES=("${DEFAULT_SERVICES[@]}")
fi

echo "[install] REPO_ROOT=$REPO_ROOT"
echo "[install] services: ${SERVICES[*]}"

for short in "${SERVICES[@]}"; do
    full="com.nousos.$short"
    template="$TEMPLATES_DIR/$full.plist"
    target="$INSTALL_DIR/$full.plist"

    if [[ ! -f "$template" ]]; then
        echo "[install] missing template: $template"
        exit 1
    fi

    sed "s|{{REPO_ROOT}}|$REPO_ROOT|g; s|{{HOME}}|$HOME|g" "$template" > "$target"
    echo "[install] wrote $target"

    launchctl bootout "$GUI_DOMAIN" "$target" 2>/dev/null || true
    launchctl bootstrap "$GUI_DOMAIN" "$target"
    launchctl kickstart -k "$GUI_DOMAIN/$full" || true
done

echo "[install] done. Verify with: launchctl list | grep com.nousos"
launchctl list | grep com.nousos || true
