#!/bin/bash
# Test script to verify Cloudflare Tunnel is working

echo "🔍 Testing Cloudflare Tunnel Connection"
echo "========================================"
echo ""

# Check if tunnel is running
if ps aux | grep -q "[c]loudflared tunnel"; then
    echo "✅ Cloudflare tunnel process is running"
else
    echo "❌ Cloudflare tunnel process not found"
    exit 1
fi

# Check if local agent is running
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ Local agent is responding on port 8080"
else
    echo "❌ Local agent not responding on port 8080"
    echo "   Start it with: HOST=0.0.0.0 AGENT_PORT=8080 ./run.sh"
    exit 1
fi

echo ""
echo "🌐 Testing Public URL"
echo "--------------------"

# Prompt for domain
if [ -z "$1" ]; then
    echo "Usage: ./test-tunnel.sh project.yourdomain.com"
    echo ""
    read -p "Enter your full domain (e.g., project.yourdomain.com): " DOMAIN
else
    DOMAIN="$1"
fi

if [ -z "$DOMAIN" ]; then
    echo "❌ No domain provided"
    exit 1
fi

echo "Testing: https://$DOMAIN"
echo ""

# Test agent card endpoint
echo "1. Testing agent card endpoint..."
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "https://$DOMAIN/.well-known/agent-card.json")
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE/d')

if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ Agent card endpoint working!"
    echo "$BODY" | python3 -m json.tool 2>/dev/null | head -10 || echo "$BODY"
else
    echo "   ❌ Agent card endpoint failed (HTTP $HTTP_CODE)"
    echo "   Response: $BODY"
fi

echo ""

# Test health endpoint
echo "2. Testing health endpoint..."
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "https://$DOMAIN/health")
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE/d')

if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ Health endpoint working!"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
else
    echo "   ❌ Health endpoint failed (HTTP $HTTP_CODE)"
    echo "   Response: $BODY"
fi

echo ""
echo "========================================"
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Tunnel is working! Your Controller URL is:"
    echo "   https://$DOMAIN"
    echo ""
    echo "Use this URL in AgentBeats:"
    echo "   - Is assessor (green) agent?: ✅ Yes"
    echo "   - Controller URL: https://$DOMAIN"
else
    echo "❌ Tunnel test failed. Check:"
    echo "   1. Tunnel is running: ps aux | grep cloudflared"
    echo "   2. Local agent is running: curl http://localhost:8080/health"
    echo "   3. DNS is configured correctly in Cloudflare"
    echo "   4. Wait a few minutes for DNS propagation"
fi

