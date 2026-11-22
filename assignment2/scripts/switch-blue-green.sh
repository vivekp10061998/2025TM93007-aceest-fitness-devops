#!/usr/bin/env bash
# Switch live Service between ready blue and green deployments.
set -euo pipefail
SLOT="${1:-}"
if [[ "$SLOT" != blue && "$SLOT" != green ]]; then
  echo "Usage: $0 blue|green" >&2
  exit 2
fi
kubectl -n aceest-blue-green rollout status "deployment/aceest-$SLOT" --timeout=180s
kubectl -n aceest-blue-green patch service aceest-service --type merge \
  -p "{\"spec\":{\"selector\":{\"app\":\"aceest-web\",\"variant\":\"$SLOT\"}}}"
echo "Live traffic now points to $SLOT. Use the other slot for rollback."
