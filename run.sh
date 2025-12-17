#!/usr/bin/env bash
set -euo pipefail

HOST="${HOST:-0.0.0.0}"
PORT="${AGENT_PORT:-8080}"

# Change to webnav directory to ensure proper module resolution
cd "$(dirname "$0")/webnav" || exit 1

# Start the FastAPI server
exec uvicorn app.main:app --host "$HOST" --port "$PORT"

