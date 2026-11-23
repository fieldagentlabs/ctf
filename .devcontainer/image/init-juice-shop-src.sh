#!/usr/bin/env bash
# Put an editable copy of the pinned Juice Shop source in the workspace, as its own
# git repo with the original committed and tagged, so `git diff v20.4.0` shows your
# changes. No network needed. Does nothing if the copy already exists.
set -euo pipefail
DEST="${JUICE_SHOP_SRC:-/workspaces/juice-shop}"
[ -d "${DEST}/.git" ] && { echo "Juice Shop source already at ${DEST}"; exit 0; }
if ! mkdir -p "${DEST}" 2>/dev/null; then sudo mkdir -p "${DEST}" && sudo chown "$(id -u):$(id -g)" "${DEST}"; fi
cp -R /opt/juice-shop-src/. "${DEST}/"
cd "${DEST}"
git init -q -b main
git -c user.name="Field Agents lab" -c user.email="lab@fieldagents.test" add -A
git -c user.name="Field Agents lab" -c user.email="lab@fieldagents.test" commit -q -m "OWASP Juice Shop v20.4.0 (pinned for Field Agents)"
git tag v20.4.0
echo "Juice Shop source ready at ${DEST} (tag v20.4.0)"
