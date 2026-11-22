#!/usr/bin/env bash
# Roll back progressive traffic using native Kubernetes and ingress controls.
set -euo pipefail
case "${1:-}" in
  rolling)
    kubectl -n aceest-rolling rollout undo deployment/aceest-app
    kubectl -n aceest-rolling rollout status deployment/aceest-app --timeout=180s
    ;;
  blue-green)
    "$(dirname "$0")/switch-blue-green.sh" "${2:-blue}"
    ;;
  canary)
    kubectl -n aceest-canary annotate ingress aceest-canary nginx.ingress.kubernetes.io/canary-weight='0' --overwrite
    ;;
  shadow)
    kubectl -n aceest-shadow annotate ingress aceest-primary nginx.ingress.kubernetes.io/mirror-target- || true
    ;;
  ab)
    kubectl -n aceest-ab delete ingress aceest-variant-b --ignore-not-found
    ;;
  *)
    echo "Usage: $0 {rolling|blue-green|canary|shadow|ab} [previous-blue-green-slot]" >&2
    exit 2
    ;;
esac
