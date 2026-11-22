#!/usr/bin/env bash
# Creates a real versioned web image. Login to Docker Hub separately to push.
set -euo pipefail
if [[ $# -ne 1 ]]; then echo "Usage: $0 YOUR_DOCKERHUB_USERNAME/aceest-fitness" >&2; exit 2; fi
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="$(cat "$ROOT/VERSION")"
TAG="$1:$VERSION"
docker build --target test -t aceest-local-test "$ROOT"
docker run --rm aceest-local-test pytest -q tests
docker build --target runtime --build-arg "APP_VERSION=$VERSION" -t "$TAG" "$ROOT"
echo "Created $TAG. To publish: docker push $TAG"
