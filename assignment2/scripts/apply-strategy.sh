#!/usr/bin/env bash
# Usage: DB_PASSWORD='...' ./scripts/apply-strategy.sh rolling user/aceest-fitness:VERSION
set -euo pipefail
if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo "Usage: $0 {rolling|blue-green|canary|shadow|ab} STABLE_IMAGE [CANDIDATE_IMAGE]" >&2
  exit 2
fi
STRATEGY="$1"
STABLE_IMAGE="$2"
CANDIDATE_IMAGE="${3:-$2}"
case "$STRATEGY" in rolling|blue-green|canary|shadow|ab) ;; *) echo "Invalid strategy" >&2; exit 2;; esac
: "${DB_PASSWORD:?Export DB_PASSWORD (never commit it)}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NS="aceest-$STRATEGY"
if [[ "$STABLE_IMAGE" == *'__IMAGE__'* || "$CANDIDATE_IMAGE" == *'__IMAGE__'* ]]; then
  echo 'Use actual image names, not placeholders' >&2; exit 2
fi
kubectl create namespace "$NS" --dry-run=client -o yaml | kubectl apply -f -
kubectl -n "$NS" create secret generic aceest-db-secret \
  --from-literal="DB_PASSWORD=$DB_PASSWORD" --dry-run=client -o yaml | kubectl apply -f -
kubectl -n "$NS" apply -f "$ROOT/k8s/common/configmap.yaml"
kubectl -n "$NS" apply -f "$ROOT/k8s/common/postgres.yaml"
kubectl -n "$NS" rollout status statefulset/postgres --timeout=180s
# Escape shell replacement delimiters, then apply the resources as versioned YAML.
escaped_stable="${STABLE_IMAGE//|/\\|}"
escaped_candidate="${CANDIDATE_IMAGE//|/\\|}"
sed -e "s|__CANDIDATE_IMAGE__|$escaped_candidate|g" -e "s|__IMAGE__|$escaped_stable|g" \
  "$ROOT/k8s/strategies/$STRATEGY/manifest.yaml" | kubectl -n "$NS" apply -f -
case "$STRATEGY" in
  rolling) deployments=(aceest-app) ;;
  blue-green) deployments=(aceest-blue aceest-green) ;;
  canary) deployments=(aceest-stable aceest-canary) ;;
  shadow) deployments=(aceest-stable aceest-shadow) ;;
  ab) deployments=(aceest-stable aceest-variant-b) ;;
esac
for deployment in "${deployments[@]}"; do
  kubectl -n "$NS" rollout status "deployment/$deployment" --timeout=180s
done
echo "Deployment ready in namespace $NS. Ingress host is documented in README.md."
