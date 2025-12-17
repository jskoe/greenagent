# ngrok Quick Start Guide

The simplest way to deploy your Green Agent for AgentBeats!

## Prerequisites

- ngrok account (free tier works great)
- Your agent running locally

## Quick Setup (2 minutes)

### 1. Install ngrok

**macOS:**
```bash
brew install ngrok/ngrok/ngrok
```

**Linux:**
```bash
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok
```

**Windows:**
Download from: https://ngrok.com/download

### 2. Authenticate

```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

Get your auth token from: https://dashboard.ngrok.com/get-started/your-authtoken

### 3. Reserve a Domain (Optional but Recommended)

1. Go to: https://dashboard.ngrok.com/cloud-edge/domains
2. Click "Reserve Domain"
3. Choose a name (e.g., `greenagent.ngrok-free.dev`)
4. Note: Free tier includes one reserved domain

### 4. Start Your Agent

```bash
cd /path/to/greenagent
HOST=0.0.0.0 AGENT_PORT=8080 ./run.sh
```

Keep this running in one terminal.

### 5. Start ngrok Tunnel

**With reserved domain:**
```bash
ngrok http 8080 --domain=your-domain.ngrok-free.dev
```

**Or use dynamic domain (changes each time):**
```bash
ngrok http 8080
```

### 6. Test Your Public URL

```bash
# Replace with your actual ngrok domain
curl https://your-domain.ngrok-free.dev/.well-known/agent-card.json
curl https://your-domain.ngrok-free.dev/health
```

### 7. Use in AgentBeats

- Visit: https://agentbeats.org
- Fill out the form:
  - **Is assessor (green) agent?**: ✅ Yes
  - **Controller URL**: `https://your-domain.ngrok-free.dev`

## Troubleshooting

### ngrok shows "offline"
- Make sure your local agent is running on port 8080
- Check: `curl http://localhost:8080/health`

### Domain not found
- If using reserved domain, make sure it matches exactly
- Check: `ngrok config check`

### Connection refused
- Verify agent is running: `ps aux | grep run.sh`
- Check port 8080 is not in use: `lsof -ti:8080`

## Keeping ngrok Running

### Using tmux/screen

```bash
# Start tmux session
tmux new -s ngrok

# Start ngrok
ngrok http 8080 --domain=your-domain.ngrok-free.dev

# Detach: Ctrl+B then D
# Reattach: tmux attach -t ngrok
```

### Using background process

```bash
nohup ngrok http 8080 --domain=your-domain.ngrok-free.dev > /tmp/ngrok.log 2>&1 &
```

## Benefits of ngrok

- ✅ **Free tier available** with reserved domain
- ✅ **No domain purchase needed** - use ngrok domains
- ✅ **HTTPS automatically** provided
- ✅ **Works from local machine** - no VPS required
- ✅ **Simple setup** - just two commands
- ✅ **Perfect for testing** and development

## Free Tier Limits

- 1 reserved domain
- Dynamic domains (change each restart)
- Sufficient bandwidth for testing
- Perfect for AgentBeats integration!

For production with your own domain, consider Cloudflare Tunnel (see DEPLOYMENT.md).

