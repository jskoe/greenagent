#!/usr/bin/env bash
# Demo test script for Green & White Agent functionality

set -e

echo "🧪 Green & White Agent Demo Test"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check dependencies
echo "Step 1: Checking dependencies..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python3 found${NC}"
echo ""

# Step 2: Start stub white agent
echo "Step 2: Starting stub white agent..."
if lsof -i :9000 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Port 9000 already in use (stub white agent might be running)${NC}"
else
    cd "$(dirname "$0")"
    python3 -m webnav.tests.stub_white_agent > /tmp/stub_white_agent.log 2>&1 &
    STUB_PID=$!
    echo "Started stub white agent (PID: $STUB_PID)"
    sleep 2
fi

# Check if stub white agent is responding
if curl -s http://localhost:9000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Stub white agent is running on port 9000${NC}"
else
    echo -e "${RED}❌ Stub white agent not responding${NC}"
    exit 1
fi
echo ""

# Step 3: Start green agent
echo "Step 3: Starting green agent..."
AGENT_PORT=8080
if lsof -i :$AGENT_PORT > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Port $AGENT_PORT already in use (agent might be running)${NC}"
    # Try to find the actual port
    AGENT_PORT=$(lsof -i -P 2>/dev/null | grep LISTEN | grep uvicorn | head -1 | awk '{print $9}' | cut -d: -f2)
    if [ -z "$AGENT_PORT" ]; then
        AGENT_PORT=8080
    fi
    echo "Using agent on port: $AGENT_PORT"
else
    cd "$(dirname "$0")"
    HOST=0.0.0.0 AGENT_PORT=$AGENT_PORT ./run.sh > /tmp/green_agent.log 2>&1 &
    AGENT_PID=$!
    echo "Started green agent (PID: $AGENT_PID) on port $AGENT_PORT"
    sleep 3
fi

# Check if green agent is responding
if curl -s http://localhost:$AGENT_PORT/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Green agent is running on port $AGENT_PORT${NC}"
else
    echo -e "${RED}❌ Green agent not responding${NC}"
    exit 1
fi
echo ""

# Step 4: Test health endpoints
echo "Step 4: Testing health endpoints..."
echo "Green agent health:"
curl -s http://localhost:$AGENT_PORT/health | python3 -m json.tool
echo ""
echo "White agent health:"
curl -s http://localhost:9000/health | python3 -m json.tool
echo ""

# Step 5: Test /run endpoint
echo "Step 5: Testing /run endpoint with demo task..."
RUN_ID="demo_$(date +%s)"
cat > /tmp/demo_task.json << EOF
{
  "run_id": "$RUN_ID",
  "task": {
    "task_id": "demo_task_001",
    "benchmark": "mind2web",
    "split": "train",
    "index": 0,
    "instruction": "Click on the first product",
    "start_url": "http://localhost:$AGENT_PORT/site/product.html",
    "success_criteria": {
      "url_contains": "product",
      "selector_present": "body"
    }
  },
  "white_agents": [
    {
      "name": "stub_agent",
      "url": "http://localhost:9000"
    }
  ],
  "limits": {
    "max_steps": 5,
    "timeout_s": 30
  }
}
EOF

echo "Sending /run request..."
RESPONSE=$(curl -s -X POST http://localhost:$AGENT_PORT/run \
  -H "Content-Type: application/json" \
  -d @/tmp/demo_task.json \
  --max-time 60)

if echo "$RESPONSE" | python3 -c "import sys, json; json.load(sys.stdin)" 2>/dev/null; then
    echo -e "${GREEN}✅ /run endpoint returned valid JSON${NC}"
    echo "$RESPONSE" | python3 -m json.tool | head -30
else
    echo -e "${RED}❌ /run endpoint failed${NC}"
    echo "$RESPONSE"
    exit 1
fi
echo ""

# Step 6: Check artifacts
echo "Step 6: Checking generated artifacts..."
sleep 2  # Give artifacts time to be written

# Check both possible artifact locations
ARTIFACT_DIR=""
if [ -d "artifacts/$RUN_ID" ]; then
    ARTIFACT_DIR="artifacts/$RUN_ID"
elif [ -d "webnav/artifacts/$RUN_ID" ]; then
    ARTIFACT_DIR="webnav/artifacts/$RUN_ID"
else
    # Try to find it
    ARTIFACT_DIR=$(find . -type d -name "$RUN_ID" -path "*/artifacts/*" 2>/dev/null | head -1)
fi

if [ -n "$ARTIFACT_DIR" ] && [ -d "$ARTIFACT_DIR" ]; then
    echo -e "${GREEN}✅ Artifacts directory created: $ARTIFACT_DIR${NC}"
    echo "Artifacts:"
    ls -lh "$ARTIFACT_DIR/" | tail -n +2
    echo ""
    # Show log preview if available
    if [ -f "$ARTIFACT_DIR/log.txt" ]; then
        echo "Log preview (last 10 lines):"
        tail -10 "$ARTIFACT_DIR/log.txt"
    elif [ -f "$ARTIFACT_DIR/logs.txt" ]; then
        echo "Log preview (last 10 lines):"
        tail -10 "$ARTIFACT_DIR/logs.txt"
    fi
else
    echo -e "${YELLOW}⚠️  Artifacts directory not found${NC}"
    echo "Checking for artifacts in different locations:"
    find . -type d -name "*$RUN_ID*" 2>/dev/null | head -5
fi
echo ""

# Step 7: Summary
echo "=================================="
echo -e "${GREEN}✅ Demo Test Complete!${NC}"
echo ""
echo "Summary:"
echo "  - Stub white agent: Running on port 9000"
echo "  - Green agent: Running on port $AGENT_PORT"
echo "  - /run endpoint: Working"
if [ -n "$ARTIFACT_DIR" ]; then
    echo "  - Artifacts: Generated in $ARTIFACT_DIR/"
else
    echo "  - Artifacts: Check webnav/artifacts/ or artifacts/ directories"
fi
echo ""
echo "To view logs:"
echo "  - Green agent: tail -f /tmp/green_agent.log"
echo "  - White agent: tail -f /tmp/stub_white_agent.log"
echo ""
echo "To stop agents:"
echo "  - Kill green agent: pkill -f 'uvicorn.*app.main:app'"
echo "  - Kill white agent: pkill -f 'stub_white_agent'"

