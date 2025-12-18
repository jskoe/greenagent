#!/usr/bin/env bash
# Diagnostic script to test agent detection like AgentBeats controller does

echo "🔍 Testing Agent Detection (AgentBeats Controller Simulation)"
echo "============================================================"
echo ""

# Find agent port
AGENT_PORT=$(lsof -i -P 2>/dev/null | grep LISTEN | grep uvicorn | head -1 | awk '{print $9}' | cut -d: -f2)
if [ -z "$AGENT_PORT" ]; then
    echo "❌ No agent found running"
    exit 1
fi

echo "Agent found on port: $AGENT_PORT"
echo ""

# Test 1: Health endpoint
echo "Test 1: Health Endpoint"
echo "----------------------"
HEALTH=$(curl -s http://localhost:$AGENT_PORT/health 2>&1)
if echo "$HEALTH" | grep -q '"ok"'; then
    echo "✓ Health endpoint works"
    echo "$HEALTH" | python3 -m json.tool 2>/dev/null || echo "$HEALTH"
else
    echo "✗ Health endpoint failed"
    echo "$HEALTH"
fi
echo ""

# Test 2: Status endpoint
echo "Test 2: Status Endpoint"
echo "----------------------"
STATUS=$(curl -s http://localhost:$AGENT_PORT/status 2>&1)
if echo "$STATUS" | python3 -c "import sys, json; json.load(sys.stdin)" 2>/dev/null; then
    echo "✓ Status endpoint returns valid JSON"
    echo "$STATUS" | python3 -m json.tool
    STATUS_VALUE=$(echo "$STATUS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null)
    READY_VALUE=$(echo "$STATUS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('ready', False))" 2>/dev/null)
    echo ""
    echo "Status value: $STATUS_VALUE"
    echo "Ready value: $READY_VALUE"
    if [ "$STATUS_VALUE" = "running" ] && [ "$READY_VALUE" = "True" ]; then
        echo "✓ Status indicates agent is running and ready"
    else
        echo "⚠️  Status might not indicate readiness correctly"
    fi
else
    echo "✗ Status endpoint failed or invalid JSON"
    echo "$STATUS"
fi
echo ""

# Test 3: Agent Card endpoint
echo "Test 3: Agent Card Endpoint"
echo "--------------------------"
CARD=$(curl -s http://localhost:$AGENT_PORT/.well-known/agent-card.json 2>&1)
if echo "$CARD" | python3 -c "import sys, json; json.load(sys.stdin)" 2>/dev/null; then
    echo "✓ Agent card returns valid JSON"
    echo "$CARD" | python3 -m json.tool | head -20
    echo ""
    
    # Check required fields
    echo "Field checks:"
    NAME=$(echo "$CARD" | python3 -c "import sys, json; print(json.load(sys.stdin).get('name', 'MISSING'))" 2>/dev/null)
    BASE_URL=$(echo "$CARD" | python3 -c "import sys, json; print(json.load(sys.stdin).get('base_url', 'MISSING'))" 2>/dev/null)
    URL=$(echo "$CARD" | python3 -c "import sys, json; print(json.load(sys.stdin).get('url', 'MISSING'))" 2>/dev/null)
    CARD_STATUS=$(echo "$CARD" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'MISSING'))" 2>/dev/null)
    READY=$(echo "$CARD" | python3 -c "import sys, json; print(json.load(sys.stdin).get('ready', 'MISSING'))" 2>/dev/null)
    
    echo "  name: $NAME"
    echo "  base_url: $BASE_URL"
    echo "  url: $URL"
    echo "  status: $CARD_STATUS"
    echo "  ready: $READY"
    echo ""
    
    if [ "$CARD_STATUS" = "running" ] && [ "$READY" = "True" ]; then
        echo "✓ Agent card indicates running and ready"
    else
        echo "⚠️  Agent card might not indicate readiness correctly"
    fi
    
    # Check for double https
    if echo "$BASE_URL" | grep -q "https://https://"; then
        echo "❌ Double https:// detected in base_url!"
    fi
    if echo "$URL" | grep -q "https://https://"; then
        echo "❌ Double https:// detected in url!"
    fi
else
    echo "✗ Agent card failed or invalid JSON"
    echo "$CARD"
fi
echo ""

# Test 4: Simulate controller proxy request
echo "Test 4: Simulated Controller Proxy Request"
echo "------------------------------------------"
PROXY_CARD=$(curl -s -H "X-Forwarded-Host: bekomaproject.xyz" -H "X-Forwarded-Proto: https" http://localhost:$AGENT_PORT/.well-known/agent-card.json 2>&1)
if echo "$PROXY_CARD" | python3 -c "import sys, json; json.load(sys.stdin)" 2>/dev/null; then
    echo "✓ Agent card accessible through proxy headers"
    PROXY_BASE_URL=$(echo "$PROXY_CARD" | python3 -c "import sys, json; print(json.load(sys.stdin).get('base_url', 'MISSING'))" 2>/dev/null)
    echo "  base_url with proxy headers: $PROXY_BASE_URL"
else
    echo "✗ Agent card not accessible through proxy headers"
    echo "$PROXY_CARD"
fi
echo ""

echo "============================================================"
echo "Summary:"
echo "  Agent Port: $AGENT_PORT"
echo "  Health: $(curl -s http://localhost:$AGENT_PORT/health 2>&1 | grep -q '"ok"' && echo 'Working' || echo 'Failed')"
echo "  Status: $(curl -s http://localhost:$AGENT_PORT/status 2>&1 | python3 -c 'import sys, json; print(json.load(sys.stdin).get("status", "unknown"))' 2>/dev/null || echo 'Failed')"
echo "  Agent Card: $(curl -s http://localhost:$AGENT_PORT/.well-known/agent-card.json 2>&1 | python3 -c 'import sys, json; print("Valid" if "name" in json.load(sys.stdin) else "Invalid")' 2>/dev/null || echo 'Failed')"
echo ""

