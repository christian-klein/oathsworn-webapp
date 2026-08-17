#!/usr/bin/env bash
#
# setup.sh - Build the self-contained oathsworn-webapp Docker container image.
#
# Environment / Arguments:
#   INCLUDE_GERMAN_LANG=true ./setup.sh
#   ./setup.sh --german
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GERMAN_FLAG="${INCLUDE_GERMAN_LANG:-false}"

for arg in "$@"; do
    if [[ "$arg" == "--german" ]] || [[ "$arg" == "--include-german" ]]; then
        GERMAN_FLAG="true"
    fi
done

if [[ "$GERMAN_FLAG" == "true" ]]; then
    echo "Building oathsworn-webapp container image (German language enabled)..."
else
    echo "Building oathsworn-webapp container image..."
fi

docker build \
    --build-arg INCLUDE_GERMAN_LANG="$GERMAN_FLAG" \
    -t oathsworn-webapp \
    "$SCRIPT_DIR"

echo ""
echo "============================================================"
echo "===                    Build complete                    ==="
echo "============================================================"
echo "Run the application with Docker Compose:"
echo "  docker compose up -d               # http://localhost:8080"
echo ""
echo "Or run directly with Docker:"
echo "  docker run -d -p 8080:8080 --name oathsworn-webapp oathsworn-webapp"
echo ""
