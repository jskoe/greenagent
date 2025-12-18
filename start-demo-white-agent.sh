#!/usr/bin/env bash
# Start demo white agent with verbose logging

set -e

echo "🚀 Starting Demo White Agent Server"
echo "===================================="
echo ""

# Check for API key
if [ -z "$OPENAI_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  Warning: No API key found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY"
    echo ""
fi

# Set defaults
export LLM_PROVIDER="${LLM_PROVIDER:-openai}"
export LLM_MODEL="${LLM_MODEL:-}"
export LLM_TEMPERATURE="${LLM_TEMPERATURE:-0.1}"
export LLM_MAX_TOKENS="${LLM_MAX_TOKENS:-500}"
export WHITE_AGENT_PORT="${WHITE_AGENT_PORT:-9000}"
export WHITE_AGENT_HOST="${WHITE_AGENT_HOST:-0.0.0.0}"

echo "Configuration:"
echo "  Provider: $LLM_PROVIDER"
echo "  Model: ${LLM_MODEL:-default}"
echo "  Port: $WHITE_AGENT_PORT"
echo "  Host: $WHITE_AGENT_HOST"
echo ""

cd "$(dirname "$0")/webnav" || exit 1

echo "Starting server..."
echo ""

python3 -m app.demo_white_agent

