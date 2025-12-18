#!/usr/bin/env bash
# Manual step-by-step Cloudflare Tunnel setup for bekomaproject.xyz

set -e

DOMAIN="bekomaproject.xyz"
TUNNEL_NAME="greenagent"
LOCAL_PORT="8080"

echo "🌐 Cloudflare Tunnel Setup for $DOMAIN"
echo "========================================="
echo ""

# Step 1: Login
echo "Step 1: Login to Cloudflare"
echo "This will open a browser window..."
echo "Select your domain: $DOMAIN"
echo ""
read -p "Press Enter to start login..."
cloudflared tunnel login

echo ""
echo "✓ Login complete!"
echo ""

# Step 2: Create tunnel
echo "Step 2: Create tunnel"
echo "Creating tunnel: $TUNNEL_NAME"
TUNNEL_OUTPUT=$(cloudflared tunnel create "$TUNNEL_NAME" 2>&1)
echo "$TUNNEL_OUTPUT"

# Extract tunnel ID
TUNNEL_ID=$(echo "$TUNNEL_OUTPUT" | grep -oP 'Created tunnel \K[a-f0-9-]+' || echo "")
if [ -z "$TUNNEL_ID" ]; then
    echo ""
    echo "⚠️  Could not auto-detect tunnel ID."
    echo "Listing existing tunnels..."
    cloudflared tunnel list
    echo ""
    read -p "Enter tunnel ID (or press Enter to use existing tunnel): " TUNNEL_ID
    if [ -z "$TUNNEL_ID" ]; then
        echo "Using existing tunnel name: $TUNNEL_NAME"
        TUNNEL_ID="$TUNNEL_NAME"
    fi
fi

echo "✓ Tunnel ID: $TUNNEL_ID"
echo ""

# Step 3: Configure DNS
echo "Step 3: Configure DNS for $DOMAIN"
echo "Creating DNS record..."
if cloudflared tunnel route dns "$TUNNEL_NAME" "$DOMAIN"; then
    echo "✓ DNS record created"
else
    echo ""
    echo "⚠️  DNS route creation failed. You may need to create it manually:"
    echo ""
    echo "In Cloudflare Dashboard:"
    echo "  1. Go to DNS settings for $DOMAIN"
    echo "  2. Add a CNAME record:"
    echo "     Type: CNAME"
    echo "     Name: @ (or leave blank for root domain)"
    echo "     Target: $TUNNEL_ID.cfargotunnel.com"
    echo "     Proxy: Proxied (orange cloud) ✓"
    echo ""
    read -p "Press Enter after creating the DNS record..."
fi

echo ""

# Step 4: Create config file
echo "Step 4: Create configuration file"

CONFIG_DIR="$HOME/.cloudflared"
CONFIG_FILE="$CONFIG_DIR/config.yml"
mkdir -p "$CONFIG_DIR"

# Find the credentials file
CREDS_FILE=$(find "$CONFIG_DIR" -name "*.json" -type f | head -1)
if [ -z "$CREDS_FILE" ]; then
    CREDS_FILE="$CONFIG_DIR/$TUNNEL_ID.json"
fi

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
echo ""

# Step 5: Validate
echo "Step 5: Validate configuration"
if cloudflared tunnel validate; then
    echo "✓ Configuration is valid"
else
    echo "⚠️  Configuration validation failed. Check the config file."
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Next steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Start your agent:"
echo "   CLOUDRUN_HOST=https://$DOMAIN HOST=0.0.0.0 AGENT_PORT=$LOCAL_PORT ./run.sh"
echo ""
echo "2. In another terminal, start the tunnel:"
echo "   cloudflared tunnel run $TUNNEL_NAME"
echo ""
echo "3. Test your domain:"
echo "   curl https://$DOMAIN/.well-known/agent-card.json"
echo ""
echo "4. Use in AgentBeats:"
echo "   https://$DOMAIN"
echo ""

