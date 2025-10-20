# WebNav Green Agent

A FastAPI-based evaluation host that runs Mind2Web tasks in isolated Playwright browser contexts, supervises a white agent stub, judges outcomes with deterministic rules, and returns structured JSON reports with saved artifacts.

## Features

- **Isolated Browser Contexts**: Each task runs in a fresh Playwright browser context
- **Deterministic Judging**: CSS selector + regex matching for reproducible results
- **Artifact Tracking**: Saves HTML snapshots, screenshots, and action logs
- **Simple White Agent**: DOM extraction stub for MVP demonstration
- **Static Page Serving**: Localhost-served HTML for reliability

## Prerequisites

- Python 3.11+
- Playwright browser binaries

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/joshkoe/greenagent.git
   cd greenagent/webnav
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```

## Running the Service

Start the FastAPI server:
```bash
cd webnav
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The service will be available at `http://localhost:8000`

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```
Response:
```json
{"ok": true}
```

### Reset Controller
```bash
curl -X POST http://localhost:8000/reset
```
Response:
```json
{"reset": true}
```

### Execute Task
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

Tasks are defined in `data/tasks.json`. The current demo includes one task:

- **task_001**: Find the price of the third product on the product catalog page

## Artifacts

Each task run saves artifacts to `runs/{task_id}/`:

- `report.json`: Complete execution report
- `final.html`: Final HTML snapshot
- `snap.png`: Screenshot of the page
- `actions.log`: Step-by-step action log

## Testing the Demo

1. Start the server:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

2. Test health endpoint:
   ```bash
   curl http://localhost:8000/health
   ```

3. Execute the demo task:
   ```bash
   curl -X POST http://localhost:8000/task \
     -H "Content-Type: application/json" \
     -d '{"task_id":"task_001"}'
   ```

4. Verify artifacts were saved:
   ```bash
   ls runs/task_001/
   ```

5. Run the task again to verify clean resets and reproducibility

## Project Structure

```
webnav/
├── app/
│   ├── main.py          # FastAPI application
│   ├── browser.py       # Playwright browser management
│   ├── controller.py    # Task orchestration
│   ├── judge.py         # Rule-based outcome validation
│   ├── white_stub.py    # Stub white agent implementation
│   ├── models.py        # Pydantic models
│   └── logging_utils.py # Artifact saving and logging
├── data/
│   └── tasks.json       # Task specifications
├── sites/
│   └── product.html     # Static demo page
├── requirements.txt     # Python dependencies
└── README.md           # This file
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

## Future Enhancements

- Multiple task types and configurations
- External white agent integration
- Advanced judging with LLM evaluation
- AgentBeats leaderboard integration
- Multi-agent tournament support

## License

MIT License - see LICENSE file for details.
