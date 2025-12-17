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

### 2. Containerized Deployment (Google Cloud Run)

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

### 3. Publish on AgentBeats Platform

1. Visit [AgentBeats](https://agentbeats.org)
2. Fill out the publish form with:
   - **Controller URL**: Your public Cloud Run URL (or other deployment URL)
   - **Agent Name**: Green Agent
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

