#!/usr/bin/env bash
# Deploy your edited Juice Shop server code, or put the original back.
#   deploy-shop            copy server code from $JUICE_SHOP_SRC, recompile, restart
#   deploy-shop --original restore the pinned original code, recompile, restart
# Server code only (routes/, lib/, models/, data/, views/, server.ts, app.ts); the
# frontend is prebuilt. Restarting clears solved challenges.
set -euo pipefail
SRC="${JUICE_SHOP_SRC:-/workspaces/juice-shop}"
[ "${1:-}" = "--original" ] && SRC=/opt/juice-shop-src
[ -d "${SRC}/routes" ] || { echo "No Juice Shop source at ${SRC}" >&2; exit 1; }

cd /opt/juice-shop
for d in routes lib models data views; do
  [ -d "${SRC}/${d}" ] && cp -R "${SRC}/${d}/." "${d}/"
done
cp "${SRC}/server.ts" "${SRC}/app.ts" .

echo "Compiling server code (type errors from missing dev packages are expected and ignored)..."
tsc >/tmp/deploy-shop-tsc.log 2>&1 || true
[ -f build/server.js ] || { echo "Compile produced no build/server.js; see /tmp/deploy-shop-tsc.log" >&2; exit 1; }
exec restart-shop
