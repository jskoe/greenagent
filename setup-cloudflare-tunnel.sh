#!/bin/bash
# Setup script for Cloudflare Tunnel deployment
# Run this on your deployment host after installing cloudflared

set -e

echo "🚀 Cloudflare Tunnel Setup for Green Agent"
echo "==========================================="
echo ""

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "❌ cloudflared not found. Please install it first:"
    echo "   Linux: curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared && chmod +x /usr/local/bin/cloudflared"
    echo "   macOS: brew install cloudflare/cloudflare/cloudflared"
    exit 1
fi

echo "✓ cloudflared found"

# Step 1: Login
echo ""
echo "Step 1: Authenticate with Cloudflare"
echo "This will open a browser window..."
read -p "Press Enter to continue..."
cloudflared tunnel login

# Step 2: Create tunnel
echo ""
echo "Step 2: Create tunnel"
read -p "Enter a name for your tunnel (e.g., greenagent): " TUNNEL_NAME
TUNNEL_NAME=${TUNNEL_NAME:-greenagent}

echo "Creating tunnel: $TUNNEL_NAME"
TUNNEL_OUTPUT=$(cloudflared tunnel create "$TUNNEL_NAME" 2>&1)
echo "$TUNNEL_OUTPUT"

# Extract tunnel ID (it's usually in the output)
TUNNEL_ID=$(echo "$TUNNEL_OUTPUT" | grep -oP 'Created tunnel \K[a-f0-9-]+' || echo "")
if [ -z "$TUNNEL_ID" ]; then
    echo "⚠️  Could not auto-detect tunnel ID. Please find it with: cloudflared tunnel list"
    read -p "Enter tunnel ID: " TUNNEL_ID
fi

echo "✓ Tunnel ID: $TUNNEL_ID"

# Step 3: Configure DNS
echo ""
echo "Step 3: Configure DNS"
read -p "Enter your domain/subdomain (e.g., greenagent.yourdomain.com): " HOSTNAME

echo "Creating DNS record..."
cloudflared tunnel route dns "$TUNNEL_NAME" "$HOSTNAME" || {
    echo "⚠️  DNS route creation failed. You may need to create it manually in Cloudflare DNS:"
    echo "   Type: CNAME"
    echo "   Name: $(echo $HOSTNAME | cut -d. -f1)"
    echo "   Target: $TUNNEL_ID.cfargotunnel.com"
    echo "   Proxy: Proxied (orange cloud)"
}

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
  - hostname: $HOSTNAME
    service: http://localhost:8080
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
echo "Next steps:"
echo "1. Start your agent controller:"
echo "   cd $(pwd)"
echo "   agentbeats run_ctrl"
echo ""
echo "2. In another terminal, start the tunnel:"
echo "   cloudflared tunnel run $TUNNEL_NAME"
echo ""
echo "3. Test your deployment:"
echo "   curl https://$HOSTNAME/.well-known/agent-card.json"
echo ""
echo "4. Use this URL for AgentBeats:"
echo "   https://$HOSTNAME"
echo ""

