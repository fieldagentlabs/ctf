#!/usr/bin/env bash
# Start the lab: Juice Shop on :3000, the nginx front on :80 (if installed), and
# the K7 canary on :8081 (if installed). Safe to run more than once.
# Restarting Juice Shop clears solved challenges.
set -euo pipefail

READY_URL=http://localhost:3000/rest/admin/application-version
LOG=/tmp/juice-shop.log

for host in shop.fieldagents.test canary.fieldagents.test; do
  grep -q " ${host}\$" /etc/hosts || echo "127.0.0.1 ${host}" | sudo tee -a /etc/hosts >/dev/null
done

if command -v nginx >/dev/null 2>&1 && ! pgrep -x nginx >/dev/null; then
  sudo nginx
fi
if [ -x /usr/local/bin/canary ] && ! pgrep -f "/usr/local/bin/canary" >/dev/null; then
  setsid nohup /usr/local/bin/canary >/dev/null 2>&1 < /dev/null &
fi

if curl -fs "${READY_URL}" >/dev/null 2>&1; then
  echo "Juice Shop is already running on http://localhost:3000"
  exit 0
fi

cd /opt/juice-shop
# setsid detaches Juice Shop from this script's session: Codespaces kills a
# lifecycle command's processes when it finishes, and plain nohup is not enough.
setsid nohup node build/app.js >"${LOG}" 2>&1 < /dev/null &

for _ in $(seq 1 90); do
  if curl -fs "${READY_URL}" >/dev/null 2>&1; then
    echo "Juice Shop is up on http://localhost:3000"
    command -v nginx >/dev/null 2>&1 && echo "Through the nginx front (logged): http://shop.fieldagents.test"
    exit 0
  fi
  sleep 2
done

echo "Juice Shop did not start within 3 minutes. Log: ${LOG}" >&2
tail -n 30 "${LOG}" >&2 || true
exit 1
