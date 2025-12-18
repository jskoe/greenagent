# Demo Quick Reference Card

## Commands to Run (In Order)

### Terminal 1: White Agent
```bash
python3 -m webnav.tests.stub_white_agent
```

### Terminal 2: Green Agent
```bash
HOST=0.0.0.0 AGENT_PORT=8080 ./run.sh
```

### Terminal 3: Test Commands

**Health Checks:**
```bash
curl http://localhost:9000/health
curl http://localhost:8080/health
```

**Run Task:**
```bash
curl -X POST http://localhost:8080/run \
  -H "Content-Type: application/json" \
  -d '{
    "run_id": "demo_001",
    "task": {
      "task_id": "demo_task",
      "instruction": "Click on the first product",
      "start_url": "http://localhost:8080/site/product.html"
    },
    "white_agents": [{"name": "stub", "url": "http://localhost:9000"}],
    "limits": {"max_steps": 5, "timeout_s": 30}
  }' | python3 -m json.tool
```

**View Artifacts:**
```bash
ls -lh artifacts/demo_001/
tail -20 artifacts/demo_001/logs.txt
head -3 artifacts/demo_001/events.jsonl | python3 -m json.tool
```

## Key Talking Points

1. **Green Agent = Evaluator** - Manages tasks, judges outcomes, generates artifacts
2. **White Agent = Actor** - Receives observations, returns actions
3. **HTTP Communication** - Agents talk via REST API
4. **Comprehensive Artifacts** - Logs, screenshots, traces, structured events
5. **Production Ready** - Works with any white agent implementing `/act`

## Timeline

- **0:00-0:30**: Intro & Overview
- **0:30-1:30**: Architecture
- **1:30-2:30**: Start Agents
- **2:30-4:00**: Run Task
- **4:00-5:00**: Show Artifacts

## What to Show

1. Project structure
2. Architecture diagram/code
3. Starting both agents
4. Health checks
5. Task execution
6. Generated artifacts
7. Logs and events

