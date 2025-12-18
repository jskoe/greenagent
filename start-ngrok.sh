#!/usr/bin/env bash
# Script to start ngrok with proper headers to bypass warning page

PORT="${AGENT_PORT:-8080}"

echo "🚀 Starting ngrok tunnel on port $PORT..."
echo "   This will bypass ngrok's free tier warning page"

ngrok http "$PORT" \
  --request-header-add "ngrok-skip-browser-warning:true" \
  --log stdout

