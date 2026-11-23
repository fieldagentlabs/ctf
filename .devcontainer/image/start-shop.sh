#!/usr/bin/env bash
# Start Juice Shop in the background and wait until it answers.
# Safe to run more than once. Restarting Juice Shop clears solved challenges.
set -euo pipefail

HOST=shop.fieldagents.test
READY_URL=http://localhost:3000/rest/admin/application-version
LOG=/tmp/juice-shop.log

grep -q " ${HOST}\$" /etc/hosts || echo "127.0.0.1 ${HOST}" | sudo tee -a /etc/hosts >/dev/null

if curl -fs "${READY_URL}" >/dev/null 2>&1; then
  echo "Juice Shop is already running on http://localhost:3000"
  exit 0
fi

cd /opt/juice-shop
nohup node build/app.js >"${LOG}" 2>&1 &

for _ in $(seq 1 90); do
  if curl -fs "${READY_URL}" >/dev/null 2>&1; then
    echo "Juice Shop is up on http://localhost:3000 (also http://${HOST}:3000)"
    exit 0
  fi
  sleep 2
done

echo "Juice Shop did not start within 3 minutes. Log: ${LOG}" >&2
tail -n 30 "${LOG}" >&2 || true
exit 1
