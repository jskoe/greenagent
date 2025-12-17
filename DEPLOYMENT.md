# AgentBeats Deployment Guide

This guide walks you through deploying the Green Agent to AgentBeats following the [official integration guide](https://docs.agentbeats.org/Blogs/blog-3/).

## Prerequisites

- Python 3.11+
- Playwright browser binaries
- (For containerized deployment) Docker or Google Cloud SDK

## Quick Start

### 1. Local Testing with AgentBeats Controller

1. Install the AgentBeats controller:
   ```bash
   pip install earthshaker
   ```

2. Start the controller:
   ```bash
   agentbeats run_ctrl
   ```

3. The controller will:
   - Automatically detect and launch your agent via `./run.sh`
   - Expose a management UI (typically at `http://localhost:8080`)
   - Provide a proxy URL to access your agent
   - Allow resetting the agent between runs

4. Test the agent card endpoint:
   ```bash
   curl http://localhost:8080/.well-known/agent-card.json
   ```

### 2. Deployment Options

#### Option A: ngrok (Simplest - Recommended for Quick Start)

Cloudflare Tunnel allows you to securely expose your agent running on any host (VPS, local machine, container service) without opening firewall ports.

**Prerequisites:**
- A domain managed by Cloudflare (or add one first)
- A host to run your agent (VPS, local machine, or container service)
- Cloudflare account

**Steps:**

1. **Deploy your agent on a host:**
   
   On your deployment host (VPS, container, etc.):
   ```bash
   # Clone your repo
   git clone https://github.com/jskoe/greenagent.git
   cd greenagent
   
   # Set up Python environment
   cd webnav
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   playwright install chromium
   
   # Install AgentBeats controller
   pip install earthshaker
   
   # Make run.sh executable
   chmod +x ../run.sh
   ```

2. **Install Cloudflare Tunnel:**
   ```bash
   # Download cloudflared (Linux example)
   curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
   chmod +x /usr/local/bin/cloudflared
   
   # Or on macOS:
   brew install cloudflare/cloudflare/cloudflared
   
   # Or on Windows:
   # Download from: https://github.com/cloudflare/cloudflared/releases
   ```

3. **Authenticate with Cloudflare:**
   ```bash
   cloudflared tunnel login
   ```
   This opens a browser window to authenticate with your Cloudflare account.

4. **Create a tunnel:**
   ```bash
   cloudflared tunnel create greenagent
   ```
   Note the tunnel ID that's displayed.

5. **Create tunnel configuration:**
   
   Create/edit `~/.cloudflared/config.yml`:
   ```yaml
   tunnel: <YOUR_TUNNEL_ID>
   credentials-file: /home/user/.cloudflared/<TUNNEL_ID>.json

   ingress:
     - hostname: greenagent.yourdomain.com
       service: http://localhost:8080
     - service: http_status:404
   ```
   
   Replace:
   - `<YOUR_TUNNEL_ID>` with your actual tunnel ID
   - `greenagent.yourdomain.com` with your desired subdomain
   - `/home/user/.cloudflared/<TUNNEL_ID>.json` with the actual path to your credentials file

6. **Create DNS record:**
   ```bash
   cloudflared tunnel route dns greenagent greenagent.yourdomain.com
   ```
   Or manually add a CNAME record in Cloudflare DNS:
   - Type: CNAME
   - Name: greenagent
   - Target: <TUNNEL_ID>.cfargotunnel.com
   - Proxy: Proxied (orange cloud)

7. **Run the tunnel (and agent):**
   
   You have two options:
   
   **Option A: Run as separate processes** (recommended for production):
   ```bash
   # Terminal 1: Start the agent
   cd /path/to/greenagent
   agentbeats run_ctrl
   
   # Terminal 2: Start the tunnel
   cloudflared tunnel run greenagent
   ```
   
   **Option B: Use a process manager like systemd** (Linux):
   
   Create `/etc/systemd/system/greenagent-tunnel.service`:
   ```ini
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
   ```
   
   Then:
   ```bash
   sudo systemctl enable greenagent-tunnel
   sudo systemctl start greenagent-tunnel
   ```

8. **Verify deployment:**
   ```bash
   curl https://greenagent.yourdomain.com/.well-known/agent-card.json
   ```

**Controller URL for AgentBeats:**
```
https://greenagent.yourdomain.com
```

**Benefits:**
- ✅ No need to open firewall ports
- ✅ Free SSL/TLS certificate
- ✅ DDoS protection
- ✅ Works from any host (home, VPS, etc.)
- ✅ Simple setup

#### Option B: Google Cloud Run

1. **Prepare for Build**:
   - Ensure `requirements.txt` exists at repo root (includes both controller and agent deps)
   - Ensure `Procfile` exists with: `web: agentbeats run_ctrl`
   - Ensure `run.sh` is executable

2. **Build and Deploy**:
   ```bash
   # Build using Google Cloud Buildpacks
   gcloud builds submit --pack image=gcr.io/YOUR_PROJECT_ID/greenagent
   
   # Deploy to Cloud Run
   gcloud run deploy greenagent \
     --image gcr.io/YOUR_PROJECT_ID/greenagent \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

3. **Verify Deployment**:
   ```bash
   # Get the service URL
   SERVICE_URL=$(gcloud run services describe greenagent --format='value(status.url)')
   
   # Test agent card
   curl $SERVICE_URL/.well-known/agent-card.json
   ```

#### Option C: Other Container Services

You can also deploy to:
- **Railway**: `railway up` (supports Procfile)
- **Render**: Connect GitHub repo, use Procfile
- **Fly.io**: `fly launch` (supports Dockerfile or Buildpacks)
- **DigitalOcean App Platform**: Connect GitHub, auto-detects Procfile

All of these work well with the existing `Procfile` configuration.

### 3. Publish on AgentBeats Platform

1. Visit [AgentBeats](https://agentbeats.org)
2. Fill out the publish form with:
   - **Is assessor (green) agent?**: ✅ Yes (check this box)
   - **Controller URL**: 
     - ngrok: `https://your-domain.ngrok-free.dev` (easiest!)
     - Cloudflare Tunnel: `https://greenagent.yourdomain.com`
     - Cloud Run: `https://greenagent-xxxxx.run.app`
     - Other: Your public deployment URL
   - **Agent Name**: Green Agent (or your preferred name)
   - **Description**: (Optional) Description of your agent
3. Submit the form
4. Your agent is now discoverable and ready for assessments!

## Architecture

```
┌─────────────────┐
│ AgentBeats      │
│ Controller      │─── Manages agent lifecycle
│ (earthshaker)   │─── Provides management UI
└────────┬────────┘─── Proxies requests
         │
         │ runs ./run.sh
         │
         ▼
┌─────────────────┐
│ Green Agent      │
│ (FastAPI)       │─── Listens on $HOST:$AGENT_PORT
│                 │─── Implements /run, /health, etc.
└─────────────────┘
```

## Environment Variables

The controller automatically sets these when launching the agent:
- `HOST`: Host to bind to (default: `0.0.0.0`)
- `AGENT_PORT`: Port to listen on (default: `8080`)

Your `run.sh` script uses these to start the agent.

## Troubleshooting

### Agent not starting
- Check that `run.sh` is executable: `chmod +x run.sh`
- Verify the script path in `run.sh` is correct
- Check controller logs for errors

### Port conflicts
- The controller manages port allocation
- Ensure no other services are using the expected ports

### Dependencies missing
- For containerized builds, ensure `requirements.txt` at root includes all dependencies
- Run `pip freeze > requirements.txt` if using Google Buildpacks (as recommended in docs)

### Playwright browsers
- Playwright browsers must be installed in the container
- Add to your Dockerfile or ensure buildpack handles it:
  ```dockerfile
  RUN playwright install chromium
  ```

## Security Considerations

⚠️ **Important**: Publicly deployed agents without authentication are vulnerable to DoS attacks.

Consider:
- Adding authentication/rate limiting
- Using Cloud Run's authentication features
- Monitoring API usage and costs

## Next Steps

Once deployed:
- Run assessments through the AgentBeats platform
- View results and metrics in the dashboard
- Share your agent with the community

For more details, see the [AgentBeats documentation](https://docs.agentbeats.org/Blogs/blog-3/).

