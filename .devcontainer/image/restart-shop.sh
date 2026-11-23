#!/usr/bin/env bash
# Restart Juice Shop with whatever code is deployed. Clears all solved challenges.
set -euo pipefail
pkill -f "node build/app.js" 2>/dev/null || true
for _ in $(seq 1 30); do curl -fs http://localhost:3000 >/dev/null 2>&1 || break; sleep 1; done
exec start-shop
