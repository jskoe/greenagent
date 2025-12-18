#!/usr/bin/env bash
# Complete demo script showing white agent framework and task completion

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  WHITE AGENT DEMONSTRATION${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Find free ports
find_free_port() {
    python3 -c 'import socket; s=socket.socket(); s.bind(("", 0)); print(s.getsockname()[1]); s.close()'
}

AGENT_PORT=$(find_free_port)
WHITE_AGENT_PORT=$(find_free_port)

echo -e "${YELLOW}Step 1: Starting Services${NC}"
echo "----------------------------------------"
echo "Starting Green Agent on port $AGENT_PORT..."
HOST=0.0.0.0 AGENT_PORT="$AGENT_PORT" ./run.sh > /tmp/green_agent.log 2>&1 &
GREEN_PID=$!
sleep 3

echo "Starting Demo White Agent on port $WHITE_AGENT_PORT..."
cd webnav && python3 -m app.demo_white_agent > /tmp/demo_white_agent.log 2>&1 &
WHITE_PID=$!
sleep 2

echo -e "${GREEN}✅ Services started${NC}"
echo ""

echo -e "${YELLOW}Step 2: Task Introduction${NC}"
echo "----------------------------------------"
echo "Task: Find the price of the third product"
echo "Environment: Product catalog page with 5 products"
echo "Available Actions: click, type, select, scroll, wait, stop"
echo ""

echo -e "${YELLOW}Step 3: Agent Framework${NC}"
echo "----------------------------------------"
echo "Framework: LLM-based reactive agent"
echo "Decision Pipeline:"
echo "  1. Receive observation (URL, title, DOM elements)"
echo "  2. Analyze task instruction"
echo "  3. Identify relevant elements"
echo "  4. Select action"
echo "  5. Return action with reasoning"
echo ""

echo -e "${YELLOW}Step 4: Running Task${NC}"
echo "----------------------------------------"
RUN_ID="demo_$(date +%s)"
echo "Run ID: $RUN_ID"
echo ""

echo "Sending request to green agent..."
RESPONSE=$(curl -s -X POST "http://localhost:$AGENT_PORT/run" \
  -H "Content-Type: application/json" \
  -d "{
    \"run_id\": \"$RUN_ID\",
    \"task\": {
      \"task_id\": \"demo_task_001\",
      \"instruction\": \"Find the price of the third product\",
      \"start_url\": \"http://localhost:$AGENT_PORT/site/product.html\",
      \"success_criteria\": {
        \"selector_present\": \"#product-3 .price\",
        \"text_present\": \"\\\\$\\\\d+\\\\.\\\\d{2}\"
      },
      \"gold_actions\": [{\"type\": \"click\", \"selector\": \"#product-3 .price\", \"step\": 0}]
    },
    \"white_agents\": [{\"name\": \"demo\", \"url\": \"http://localhost:$WHITE_AGENT_PORT\"}],
    \"limits\": {\"max_steps\": 10, \"timeout_s\": 30}
  }")

echo ""
echo "Response:"
echo "$RESPONSE" | python3 -m json.tool
echo ""

echo -e "${YELLOW}Step 5: White Agent Logs${NC}"
echo "----------------------------------------"
echo "Showing white agent reasoning (last 50 lines):"
tail -50 /tmp/demo_white_agent.log
echo ""

echo -e "${YELLOW}Step 6: Evaluation Results${NC}"
echo "----------------------------------------"
METRICS=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(json.dumps(data.get('metrics', {}), indent=2))" 2>/dev/null)
if [ -n "$METRICS" ]; then
    echo "$METRICS"
else
    echo "Metrics not available in response"
fi
echo ""

echo -e "${YELLOW}Step 7: Artifacts${NC}"
echo "----------------------------------------"
ARTIFACTS_DIR="webnav/artifacts/$RUN_ID"
if [ -d "$ARTIFACTS_DIR" ]; then
    echo "Artifacts saved to: $ARTIFACTS_DIR"
    echo "Files:"
    ls -lh "$ARTIFACTS_DIR" | tail -n +2
    echo ""
    echo "Events (first 3 steps):"
    head -3 "$ARTIFACTS_DIR/events.jsonl" | python3 -m json.tool 2>/dev/null || head -3 "$ARTIFACTS_DIR/events.jsonl"
else
    echo "Artifacts directory not found"
fi
echo ""

echo -e "${GREEN}Demo Complete!${NC}"
echo ""
echo "To view logs:"
echo "  Green Agent: tail -f /tmp/green_agent.log"
echo "  White Agent: tail -f /tmp/demo_white_agent.log"
echo ""
echo "To stop services:"
echo "  kill $GREEN_PID $WHITE_PID"

