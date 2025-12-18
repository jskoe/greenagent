# 5-Minute Demo Video Script

## Overview
This script outlines a 5-minute demo video showing the Green & White Agent system working together.

---

## Timeline Breakdown

### 0:00 - 0:30 (30 seconds) - Introduction & Overview

**What to show:**
- Screen showing the project structure
- Brief explanation of what we're building

**Script:**
> "Today I'm demonstrating a Green Agent system that orchestrates White Agents to complete web navigation tasks. The Green Agent acts as an evaluator, while White Agents perform the actual actions. Let me show you how they work together."

**Visual:**
- Show project directory structure
- Highlight key files: `run.sh`, `webnav/app/main.py`, `webnav/tests/stub_white_agent.py`

---

### 0:30 - 1:30 (60 seconds) - Architecture Explanation

**What to show:**
- Diagram or code showing the architecture
- Explain the flow

**Script:**
> "The system has three main components: First, the Green Agent - a FastAPI server that manages task execution, judges outcomes, and generates artifacts. Second, White Agents - external services that receive observations and return actions. Third, the orchestration layer that coordinates between them."

**Visual:**
- Show a simple diagram or code structure:
  ```
  Green Agent (Port 8080)
    ↓
  Observes page state
    ↓
  Calls White Agent (Port 9000)
    ↓
  Receives action
    ↓
  Executes action
    ↓
  Judges outcome
  ```

**Code to show:**
- Quick look at `webnav/app/main.py` - the `/run` endpoint
- Quick look at `webnav/tests/stub_white_agent.py` - the `/act` endpoint

---

### 1:30 - 2:30 (60 seconds) - Starting the System

**What to show:**
- Terminal windows starting both agents
- Health checks

**Script:**
> "Let's start the system. First, I'll start the stub white agent on port 9000. This is a simple test agent that returns deterministic actions. Then I'll start the green agent on port 8080, which will orchestrate the task execution."

**Visual:**
- Terminal 1: `python3 -m webnav.tests.stub_white_agent`
- Show it starting and listening on port 9000
- Terminal 2: `HOST=0.0.0.0 AGENT_PORT=8080 ./run.sh`
- Show it starting and listening on port 8080

**Health checks:**
```bash
# Terminal 3
curl http://localhost:9000/health
curl http://localhost:8080/health
```

**Script:**
> "Both agents are now running. The white agent is ready to receive action requests, and the green agent is ready to orchestrate tasks."

---

### 2:30 - 4:00 (90 seconds) - Running a Task

**What to show:**
- Prepare the task JSON
- Send the `/run` request
- Show the execution in real-time (or explain what's happening)
- Show the response

**Script:**
> "Now let's run a task. I'll send a request to the green agent with a task specification. The task is to click on the first product in a product catalog page."

**Visual:**
- Show the task JSON:
```json
{
  "run_id": "demo_001",
  "task": {
    "task_id": "demo_task",
    "instruction": "Click on the first product",
    "start_url": "http://localhost:8080/site/product.html"
  },
  "white_agents": [{"name": "stub", "url": "http://localhost:9000"}],
  "limits": {"max_steps": 5, "timeout_s": 30}
}
```

**Send the request:**
```bash
curl -X POST http://localhost:8080/run \
  -H "Content-Type: application/json" \
  -d @demo_task.json | python3 -m json.tool
```

**While it's running, explain:**
> "The green agent is now: First, loading the start URL in a browser. Second, extracting an observation of the current page state. Third, sending that observation to the white agent. Fourth, receiving an action back. Fifth, executing that action. This loop continues until the task is complete or a limit is reached."

**Show the response:**
- Highlight key fields: `status`, `success`, `metrics`, `artifacts`

**Script:**
> "The task completed successfully! We can see the metrics showing it took 3 steps and about 2 seconds. The final success is true, meaning the task was completed correctly."

---

### 4:00 - 5:00 (60 seconds) - Artifacts & Results

**What to show:**
- Navigate to artifacts directory
- Show generated files
- Explain what each artifact contains
- Quick look at some content

**Script:**
> "The green agent generates comprehensive artifacts for each run. Let's look at what was created."

**Visual:**
```bash
ls -lh artifacts/demo_001/
```

**Show files:**
- `logs.txt` - Execution logs
- `screenshot.png` - Final page screenshot
- `trace.zip` - Playwright trace (can be opened in Playwright Inspector)
- `events.jsonl` - Structured event log

**Script:**
> "The logs show the step-by-step execution. The screenshot shows the final state of the page. The trace file can be opened in Playwright Inspector to replay the entire session. And the events.jsonl file contains structured data about each step - observations, actions, and outcomes."

**Quick look at logs:**
```bash
tail -20 artifacts/demo_001/logs.txt
```

**Quick look at events:**
```bash
head -3 artifacts/demo_001/events.jsonl | python3 -m json.tool
```

**Script:**
> "This demonstrates a complete evaluation pipeline: task specification, agent orchestration, action execution, outcome judging, and artifact generation. The system is ready for production use with real white agents."

---

## Production Tips

### Before Recording:
1. **Test everything first** - Run the demo script to ensure it works
2. **Prepare terminal windows** - Have 3 terminals ready
3. **Prepare the task JSON** - Have `demo_task.json` ready
4. **Clear artifacts** - Start with a clean `artifacts/` directory
5. **Test the product page** - Make sure `http://localhost:8080/site/product.html` loads

### During Recording:
1. **Speak clearly** - Explain what you're doing as you do it
2. **Show, don't tell** - Let the code/terminal speak for itself
3. **Pause for effect** - Give viewers time to read what's on screen
4. **Highlight important parts** - Use cursor or zoom to highlight key elements
5. **Keep it smooth** - Avoid typos, have commands ready to paste

### Editing Tips:
1. **Add text overlays** - Label terminal windows (White Agent, Green Agent, etc.)
2. **Zoom on important parts** - Zoom in on JSON responses, artifacts
3. **Add transitions** - Smooth transitions between sections
4. **Add background music** - Subtle, non-distracting music
5. **Add captions** - Optional but helpful

---

## Alternative: Screen Recording Script

If you want to automate the recording, here's a script that does everything:

```bash
#!/bin/bash
# demo_recording.sh - Automated demo recording

# Start recording (using asciinema or similar)
# asciinema rec demo.cast

# Start white agent
python3 -m webnav.tests.stub_white_agent &
WHITE_PID=$!

# Start green agent
HOST=0.0.0.0 AGENT_PORT=8080 ./run.sh &
GREEN_PID=$!

sleep 3

# Health checks
echo "=== Health Checks ==="
curl http://localhost:9000/health
curl http://localhost:8080/health

# Run task
echo "=== Running Task ==="
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

# Show artifacts
echo "=== Generated Artifacts ==="
ls -lh artifacts/demo_001/
echo ""
echo "=== Logs Preview ==="
tail -20 artifacts/demo_001/logs.txt
echo ""
echo "=== Events Preview ==="
head -3 artifacts/demo_001/events.jsonl | python3 -m json.tool

# Cleanup
kill $WHITE_PID $GREEN_PID
```

---

## Key Points to Emphasize

1. **Separation of Concerns**: Green agent evaluates, white agents act
2. **HTTP-based Communication**: Agents communicate via REST API
3. **Comprehensive Artifacts**: Logs, screenshots, traces, structured events
4. **Deterministic Judging**: Success criteria based on selectors and text
5. **Production Ready**: Works with any white agent that implements the `/act` endpoint

---

## Demo Checklist

- [ ] Test the demo script works
- [ ] Prepare terminal windows
- [ ] Prepare task JSON file
- [ ] Clear artifacts directory
- [ ] Test product page loads
- [ ] Record introduction
- [ ] Record architecture explanation
- [ ] Record starting agents
- [ ] Record running task
- [ ] Record showing artifacts
- [ ] Edit and add overlays
- [ ] Add background music (optional)
- [ ] Export final video

