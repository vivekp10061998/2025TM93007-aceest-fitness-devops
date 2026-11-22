#!/usr/bin/env bash
# Usage: ./scripts/smoke-test.sh http://127.0.0.1:8000
set -euo pipefail
BASE_URL="${1:-http://127.0.0.1:8000}"
curl --fail --silent --show-error "$BASE_URL/health/ready" | grep -q 'ready'
curl --fail --silent --show-error "$BASE_URL/api/version" | grep -q 'ACEest Fitness'
curl --fail --silent --show-error "$BASE_URL/api/programs" | grep -q 'fat-loss'
echo "Smoke test passed for $BASE_URL"
