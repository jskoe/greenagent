# Cloudflare Tunnel Quick Start Guide

Quick reference for deploying Green Agent with Cloudflare Tunnel.

## Prerequisites Checklist

- [ ] Domain managed by Cloudflare
- [ ] Host/server to run the agent (VPS, local machine, etc.)
- [ ] Cloudflare account

## Quick Setup (5 minutes)

### 1. Install cloudflared

**Linux:**
```bash
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared
```

**macOS:**
```bash
brew install cloudflare/cloudflare/cloudflared
```

**Windows:**
Download from: https://github.com/cloudflare/cloudflared/releases

### 2. Run Setup Script

```bash
./setup-cloudflare-tunnel.sh
```

Or follow manual steps below.

### 3. Manual Setup (if not using script)

```bash
# Step 1: Login
cloudflared tunnel login

# Step 2: Create tunnel
cloudflared tunnel create greenagent

# Step 3: Add DNS route (replace with your domain)
cloudflared tunnel route dns greenagent greenagent.yourdomain.com

# Step 4: Create config file at ~/.cloudflared/config.yml
# (Use cloudflared-config.example.yml as template)

# Step 5: Run tunnel
cloudflared tunnel run greenagent
```

### 4. Start Your Agent

In a separate terminal:
```bash
cd /path/to/greenagent
pip install earthshaker
agentbeats run_ctrl
```

### 5. Test

```bash
curl https://greenagent.yourdomain.com/.well-known/agent-card.json
```

### 6. Use in AgentBeats

- **Is assessor (green) agent?**: ✅ Yes
- **Controller URL**: `https://greenagent.yourdomain.com`

## Running in Background

### Using systemd (Linux)

```bash
# Create service file
sudo nano /etc/systemd/system/greenagent-tunnel.service

# Add:
[Unit]
Description=Cloudflare Tunnel for Green Agent
After=network.target

[Service]
Type=simple
User=youruser
ExecStart=/usr/local/bin/cloudflared tunnel run greenagent
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable greenagent-tunnel
sudo systemctl start greenagent-tunnel
sudo systemctl status greenagent-tunnel
```

### Using tmux/screen

```bash
# Start tmux session
tmux new -s greenagent

# Start tunnel
cloudflared tunnel run greenagent

# Detach: Ctrl+B then D
# Reattach: tmux attach -t greenagent
```

## Troubleshooting

### Tunnel not connecting
- Check config file syntax: `cloudflared tunnel validate`
- Verify credentials file exists and is readable
- Check DNS record is correctly set

### Agent not accessible
- Verify agent controller is running on localhost:8080
- Check firewall isn't blocking localhost connections
- Test locally: `curl http://localhost:8080/health`

### DNS not resolving
- Wait a few minutes for DNS propagation
- Verify DNS record in Cloudflare dashboard
- Check tunnel status: `cloudflared tunnel info greenagent`

## Configuration File Location

- **Linux/macOS**: `~/.cloudflared/config.yml`
- **Windows**: `%USERPROFILE%\.cloudflared\config.yml`

## Support

- Cloudflare Tunnel docs: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/
- AgentBeats docs: https://docs.agentbeats.org/

