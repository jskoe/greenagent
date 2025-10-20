# WebNav Green Agent

A FastAPI-based evaluation host for Mind2Web tasks with isolated browser contexts, deterministic judging, and artifact tracking.

## Quick Start

```bash
cd webnav
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Demo

```bash
curl -X POST http://localhost:8000/task \
  -H "Content-Type: application/json" \
  -d '{"task_id":"task_001"}'
```

## Features

- **Isolated Browser Contexts**: Fresh Playwright context per task
- **Deterministic Judging**: CSS selector + regex validation
- **Artifact Tracking**: HTML snapshots, screenshots, logs
- **Static Page Serving**: Localhost-served HTML
- **API-First Design**: Clean endpoints for external agents

## Architecture

Green agent evaluation host that:
1. Hosts deterministic web pages locally
2. Assigns tasks to white agents  
3. Supervises actions in isolated contexts
4. Judges outcomes with deterministic rules
5. Saves complete artifacts for debugging

Perfect for Mind2Web task evaluation and AgentBeats integration.