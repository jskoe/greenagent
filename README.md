# Green Agent (AgentBeats v2 Compatible)

A production-ready AgentBeats v2-compatible Green Agent that runs Mind2Web tasks in isolated Playwright browser contexts, orchestrates remote white agents, judges outcomes with deterministic rules, and returns structured JSON reports with comprehensive artifacts.

## Features

- **AgentBeats v2 Compatible**: Full compatibility with AgentBeats v2 controller and packaging requirements
- **Mind2Web Integration**: Load and evaluate Mind2Web tasks with gold action trace matching
- **White Agent Orchestration**: HTTP-based A2A communication with remote white agents
- **Isolated Browser Contexts**: Each task runs in a fresh Playwright browser context with tracing
- **Deterministic Judging**: CSS selector + regex matching and success criteria for reproducible results
- **Comprehensive Artifacts**: Saves events.jsonl, screenshots, Playwright traces, and logs organized by run_id
- **Action Execution**: Supports click, type, select, scroll, wait, and stop actions
- **Backward Compatible**: Maintains existing `/task` endpoint while adding new `/run` endpoint

## Prerequisites

- Python 3.11+
- Playwright browser binaries

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/joshkoe/greenagent.git
   cd greenagent
   ```

2. Install Python dependencies:
   ```bash
   cd webnav
   pip install -r requirements.txt
   ```

3. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```

4. (Optional) Install AgentBeats controller for local testing:
   ```bash
   pip install earthshaker
   ```

## Running the Service

### AgentBeats v2 Deployment

For AgentBeats v2 deployment, use the `run.sh` script:
```bash
HOST=0.0.0.0 AGENT_PORT=8080 ./run.sh
```

The service will be available at `http://$HOST:$AGENT_PORT`

### Local Development

Start the FastAPI server locally:
```bash
cd webnav
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Or use the Makefile:
```bash
make dev
```

The service will be available at `http://localhost:8000`

## Environment Variables

- `HOST`: Server host (default: `0.0.0.0`)
- `AGENT_PORT`: Server port (default: `8080`)
- `MIND2WEB_DATA_DIR`: Path to Mind2Web data directory (optional, falls back to local sample)
- `WHITE_AGENT_ACT_PATH`: Path for white agent `/act` endpoint (default: `/act`)

## API Endpoints

### Agent Card (AgentBeats v2)
```bash
curl http://localhost:8000/.well-known/agent-card.json
```
Returns agent metadata, capabilities, and endpoints for AgentBeats discovery.

### Health Check
```bash
curl http://localhost:8000/health
```
Response:
```json
{"ok": true, "version": "1.0.0"}
```

### Reset Controller
```bash
curl -X POST http://localhost:8000/reset
```
Response:
```json
{"reset": true}
```

### Run Evaluation (AgentBeats v2 - Primary Endpoint)
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "run_id": "run_001",
    "task": {
      "task_id": "task_001",
      "benchmark": "mind2web",
      "split": "train",
      "instruction": "Find the price of the third product",
      "start_url": "http://localhost:8000/site/product.html"
    },
    "white_agents": [
      {"name": "agent1", "url": "http://localhost:9000"}
    ],
    "limits": {
      "max_steps": 20,
      "timeout_s": 300
    }
  }'
```

Response:
```json
{
  "run_id": "run_001",
  "task_id": "task_001",
  "success": true,
  "metrics": {
    "final_success": 1,
    "steps_taken": 5,
    "trace_match_ratio": 0.8,
    "wall_time_s": 12.5,
    "timeouts": 0,
    "invalid_actions": 0
  },
  "artifacts": {
    "log_path": "artifacts/run_001/log.txt",
    "trace_zip": null,
    "screenshots_dir": "artifacts/run_001/screens/",
    "playwright_trace": "artifacts/run_001/pwtrace.zip"
  },
  "error": null
}
```

### Execute Task (Legacy - Backward Compatible)
```bash
curl -X POST http://localhost:8000/task \
  -H "Content-Type: application/json" \
  -d '{"task_id":"task_001"}'
```

Response:
```json
{
  "task_id": "task_001",
  "success": true,
  "metrics": {
    "duration_sec": 1.2,
    "step_count": 4,
    "on_task_domain": true
  },
  "evidence": {
    "matched_text": "$299.99",
    "final_url": "http://localhost:8000/site/product.html",
    "screenshot": "runs/task_001/snap.png"
  },
  "logs": [
    "Created new page",
    "goto http://localhost:8000/site/product.html",
    "wait for page load",
    "extract #product-3 .price => $299.99",
    "close page"
  ]
}
```

## Static Files

The service serves static HTML files from the `sites/` directory at the `/site/` route:

- Product catalog: `http://localhost:8000/site/product.html`

## Task Configuration

### Legacy Format
Tasks are defined in `data/tasks.json` for backward compatibility.

### Mind2Web Format
Mind2Web tasks are defined in `data/mind2web_sample.json` or loaded from `MIND2WEB_DATA_DIR`. Each task includes:
- `task_id`: Unique identifier
- `instruction`: Task instruction
- `start_url`: Starting URL
- `gold_actions`: Optional gold standard actions for trace matching
- `success_criteria`: Success criteria (url_contains, text_present, selector_present)

## Artifacts

### `/run` Endpoint Artifacts
Each run saves artifacts to `artifacts/{run_id}/`:

- `events.jsonl`: One JSON line per step with observation hash, action, result, timestamp, URL
- `log.txt`: Consolidated log file
- `screens/`: Directory with screenshots per step (`step_000.png`, `step_001.png`, ...)
- `pwtrace.zip`: Playwright trace file (if tracing enabled)

### Legacy `/task` Endpoint Artifacts
Legacy tasks save artifacts to `runs/{task_id}/`:

- `report.json`: Complete execution report
- `final.html`: Final HTML snapshot
- `snap.png`: Screenshot of the page
- `actions.log`: Step-by-step action log

## Testing

### Quick Test with Makefile
```bash
make install    # Install dependencies
make dev        # Start server
make test_run   # Run test evaluation with stub white agent
```

### Manual Testing

1. Start the server:
   ```bash
   make dev
   # Or: cd webnav && uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

2. Start stub white agent (in another terminal):
   ```bash
   cd webnav && python -m tests.stub_white_agent
   ```

3. Test `/run` endpoint:
   ```bash
   curl -X POST http://localhost:8000/run \
     -H "Content-Type: application/json" \
     -d '{
       "run_id": "test_001",
       "task": {
         "task_id": "task_001",
         "benchmark": "mind2web",
         "instruction": "Find the price of the third product",
         "start_url": "http://localhost:8000/site/product.html"
       },
       "white_agents": [{"name": "stub", "url": "http://localhost:9000"}],
       "limits": {"max_steps": 10, "timeout_s": 60}
     }'
   ```

4. Verify artifacts were saved:
   ```bash
   ls artifacts/test_001/
   cat artifacts/test_001/events.jsonl
   ```

5. Test legacy `/task` endpoint:
   ```bash
   curl -X POST http://localhost:8000/task \
     -H "Content-Type: application/json" \
     -d '{"task_id":"task_001"}'
   ```

## Project Structure

```
greenagent/
├── run.sh                    # AgentBeats v2 entrypoint script
├── Makefile                  # Development commands
├── README.md                 # This file
└── webnav/
    ├── app/
    │   ├── main.py           # FastAPI application with /run endpoint
    │   ├── browser.py        # Playwright browser management
    │   ├── controller.py     # Task orchestration + run_evaluation()
    │   ├── judge.py          # Rule-based outcome validation + trace matching
    │   ├── models.py         # Pydantic models (RunRequest/Response, etc.)
    │   ├── logging_utils.py  # Artifact saving (events.jsonl, traces)
    │   ├── mind2web_loader.py # Mind2Web task loader
    │   ├── observation.py    # Observation extraction for white agents
    │   ├── white_agent_client.py # HTTP client for white agent A2A calls
    │   ├── action_executor.py # Action execution (click, type, etc.)
    │   └── white_stub.py     # Legacy stub (backward compatibility)
    ├── data/
    │   ├── tasks.json        # Legacy task specifications
    │   └── mind2web_sample.json # Mind2Web sample tasks
    ├── tests/
    │   └── stub_white_agent.py # Stub white agent for testing
    ├── sites/
    │   └── product.html      # Static demo page
    └── requirements.txt       # Python dependencies
```

## Key Design Decisions

- **Browser Isolation**: Every task execution creates a fresh Playwright context
- **Deterministic Judging**: CSS selector + regex matching for reproducible results
- **Artifact Tracking**: Complete evidence saved for debugging and validation
- **Simple White Agent**: DOM extraction only for MVP demonstration
- **Static Pages**: Localhost-served HTML eliminates network dependencies

## Success Criteria

- All three endpoints return expected responses
- Task execution completes in <5 seconds
- Artifacts saved correctly in `runs/{task_id}/`
- Running task twice produces identical success results
- No browser contexts left open after execution

## Troubleshooting

- **Port already in use**: Change the port in the uvicorn command or kill existing processes
- **Playwright browser issues**: Run `playwright install chromium` again
- **Permission errors**: Ensure write permissions for the `runs/` directory
- **Task not found**: Verify `data/tasks.json` exists and contains the task_id

## AgentBeats v2 Compatibility

This agent is fully compatible with AgentBeats v2 and ready for deployment:

- ✅ `run.sh` script with `HOST` and `AGENT_PORT` env vars
- ✅ `GET /.well-known/agent-card.json` endpoint
- ✅ `GET /health` endpoint with version
- ✅ `POST /reset` endpoint for cleanup
- ✅ `POST /run` endpoint with full evaluation pipeline
- ✅ Mind2Web task loading
- ✅ White agent orchestration via HTTP
- ✅ Comprehensive artifact generation (events.jsonl, traces, screenshots)
- ✅ Deterministic judging with trace matching
- ✅ Structured metrics and error reporting
- ✅ `Procfile` for containerized deployment

### Deploying to AgentBeats

Follow the [AgentBeats integration guide](https://docs.agentbeats.org/Blogs/blog-3/) to deploy:

**Quick Start with ngrok (Easiest):**

1. **Start your agent locally:**
   ```bash
   HOST=0.0.0.0 AGENT_PORT=8080 ./run.sh
   ```

2. **Start ngrok tunnel:**
   ```bash
   ngrok http 8080 --domain=your-domain.ngrok-free.dev
   ```
   (Or use `ngrok http 8080` for a free dynamic domain)

3. **Publish on AgentBeats:**
   - Visit [AgentBeats platform](https://agentbeats.org)
   - Fill out the form:
     - **Is assessor (green) agent?**: ✅ Yes
     - **Controller URL**: `https://your-domain.ngrok-free.dev`
   - Your agent is now live!

**Alternative: Local Testing with Controller**:
   ```bash
   pip install earthshaker
   agentbeats run_ctrl
   ```
   This starts the AgentBeats controller which manages your agent via `run.sh`.

**Alternative: Containerized Deployment** (e.g., Google Cloud Run):
   ```bash
   # The Procfile defines: web: agentbeats run_ctrl
   # Build using Google Cloud Buildpacks:
   gcloud builds submit --pack image=gcr.io/PROJECT_ID/greenagent
   gcloud run deploy greenagent --image gcr.io/PROJECT_ID/greenagent
   ```

For more deployment options (Cloudflare Tunnel, etc.), see [DEPLOYMENT.md](DEPLOYMENT.md).

## White Agent Protocol

White agents must implement a `POST /act` endpoint (configurable via `WHITE_AGENT_ACT_PATH`) that accepts:

```json
{
  "run_id": "string",
  "task_id": "string",
  "instruction": "string",
  "step_idx": 0,
  "observation": {
    "url": "string",
    "title": "string",
    "dom_summary": [...]
  },
  "action_space": {
    "allowed": ["click", "type", "select", "scroll", "wait", "stop"]
  }
}
```

And returns:

```json
{
  "action": {
    "type": "click",
    "selector": "css or xpath",
    "confidence": 0.8
  },
  "thoughts": "optional",
  "info": {}
}
```

## Future Enhancements

- Offline replay mode (snapshot/HAR/MHTML loading)
- Multi-agent tournament support
- Advanced LLM-based judging
- Real-time progress streaming

## License

MIT License - see LICENSE file for details.
