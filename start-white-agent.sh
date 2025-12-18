#!/bin/bash
# Start the LLM-powered white agent server

# Default configuration
export LLM_PROVIDER=${LLM_PROVIDER:-"openai"}
export WHITE_AGENT_PORT=${WHITE_AGENT_PORT:-9000}
export WHITE_AGENT_HOST=${WHITE_AGENT_HOST:-"0.0.0.0"}

# Check for API key
if [ "$LLM_PROVIDER" = "openai" ]; then
    if [ -z "$OPENAI_API_KEY" ]; then
        echo "Error: OPENAI_API_KEY environment variable is required"
        echo "Set it with: export OPENAI_API_KEY=your_key_here"
        exit 1
    fi
elif [ "$LLM_PROVIDER" = "anthropic" ]; then
    if [ -z "$ANTHROPIC_API_KEY" ]; then
        echo "Error: ANTHROPIC_API_KEY environment variable is required"
        echo "Set it with: export ANTHROPIC_API_KEY=your_key_here"
        exit 1
    fi
fi

echo "Starting LLM White Agent Server..."
echo "Provider: $LLM_PROVIDER"
echo "Port: $WHITE_AGENT_PORT"
echo "Model: ${LLM_MODEL:-default}"

cd "$(dirname "$0")/webnav" || exit 1
python3 -m app.white_agent_server

