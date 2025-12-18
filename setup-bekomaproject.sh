#!/usr/bin/env bash
# Setup Cloudflare Tunnel for bekomaproject.xyz

set -e

DOMAIN="bekomaproject.xyz"
TUNNEL_NAME="greenagent"
LOCAL_PORT="8080"

echo "🌐 Cloudflare Tunnel Setup for $DOMAIN"
echo "========================================="
echo ""

# Check prerequisites
if ! command -v cloudflared &> /dev/null; then
    echo "❌ cloudflared not found. Please install it first:"
    echo "   macOS: brew install cloudflare/cloudflare/cloudflared"
    exit 1
fi

echo "✓ cloudflared found"
echo ""

# Step 1: Login
echo "Step 1: Authenticate with Cloudflare"
echo "This will open a browser window..."
read -p "Press Enter to continue..."
cloudflared tunnel login

# Step 2: Create tunnel
echo ""
echo "Step 2: Create tunnel"
echo "Creating tunnel: $TUNNEL_NAME"
TUNNEL_OUTPUT=$(cloudflared tunnel create "$TUNNEL_NAME" 2>&1)
echo "$TUNNEL_OUTPUT"

# Extract tunnel ID
TUNNEL_ID=$(echo "$TUNNEL_OUTPUT" | grep -oP 'Created tunnel \K[a-f0-9-]+' || echo "")
if [ -z "$TUNNEL_ID" ]; then
    echo "⚠️  Could not auto-detect tunnel ID."
    echo "Listing tunnels..."
    cloudflared tunnel list
    read -p "Enter tunnel ID: " TUNNEL_ID
fi

echo "✓ Tunnel ID: $TUNNEL_ID"

# Step 3: Configure DNS
echo ""
echo "Step 3: Configure DNS for $DOMAIN"
echo "Creating DNS record..."
if cloudflared tunnel route dns "$TUNNEL_NAME" "$DOMAIN"; then
    echo "✓ DNS record created"
else
    echo "⚠️  DNS route creation failed. You may need to create it manually in Cloudflare DNS:"
    echo "   Type: CNAME"
    echo "   Name: @ (or root domain)"
    echo "   Target: $TUNNEL_ID.cfargotunnel.com"
    echo "   Proxy: Proxied (orange cloud)"
    read -p "Press Enter after creating the DNS record manually..."
fi

# Step 4: Create config file
echo ""
echo "Step 4: Create configuration file"

CONFIG_DIR="$HOME/.cloudflared"
CONFIG_FILE="$CONFIG_DIR/config.yml"
CREDS_FILE="$CONFIG_DIR/$TUNNEL_ID.json"

mkdir -p "$CONFIG_DIR"

cat > "$CONFIG_FILE" <<EOF
tunnel: $TUNNEL_ID
credentials-file: $CREDS_FILE

ingress:
  - hostname: $DOMAIN
    service: http://localhost:$LOCAL_PORT
  - service: http_status:404
EOF

echo "✓ Configuration file created at: $CONFIG_FILE"
echo ""
echo "Configuration:"
cat "$CONFIG_FILE"

# Step 5: Instructions
echo ""
echo "✅ Setup complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Next steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Start your agent with your domain:"
echo "   cd $(pwd)"
echo "   CLOUDRUN_HOST=https://$DOMAIN HOST=0.0.0.0 AGENT_PORT=$LOCAL_PORT ./run.sh"
echo ""
echo "2. In another terminal, start the tunnel:"
echo "   cloudflared tunnel run $TUNNEL_NAME"
echo ""
echo "3. Wait a minute for DNS to propagate, then test:"
echo "   curl https://$DOMAIN/.well-known/agent-card.json"
echo ""
echo "4. Use this URL in AgentBeats:"
echo "   https://$DOMAIN"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To run the tunnel in the background:"
echo "  cloudflared tunnel run $TUNNEL_NAME > /tmp/cloudflared.log 2>&1 &"
echo ""

