# WebNav Green Agent Demo Guide

## Quick Demo (2 minutes)

### 1. Start the Service
```bash
cd webnav
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Test Health Check
```bash
curl http://localhost:8000/health
```
**Expected:** `{"ok": true}`

### 3. View Product Catalog
```bash
curl http://localhost:8000/site/product.html
```
**Expected:** HTML product catalog with 5 products

### 4. Execute Task
```bash
curl -X POST http://localhost:8000/task \
  -H "Content-Type: application/json" \
  -d '{"task_id":"task_001"}'
```
**Expected:** JSON report with `"success": true` and `"matched_text": "$299.99"`

### 5. Verify Artifacts
```bash
ls runs/task_001/
```
**Expected:** `report.json`, `final.html`, `snap.png`, `actions.log`

### 6. Test Reset & Reproducibility
```bash
curl -X POST http://localhost:8000/reset
curl -X POST http://localhost:8000/task \
  -H "Content-Type: application/json" \
  -d '{"task_id":"task_001"}'
```
**Expected:** Same successful result

## Demo Talking Points

### What is WebNav?
- **Green Agent**: Evaluation host that supervises white agents
- **Mind2Web Integration**: Converts static tasks to live, reproducible assessments
- **Deterministic Judging**: CSS selector + regex matching (no LLM required)
- **Artifact Tracking**: Complete evidence trail for debugging

### Key Architecture Decisions
1. **Browser Isolation**: Fresh Playwright context per task prevents state leakage
2. **Static Pages**: Localhost-served HTML eliminates network flakiness
3. **Rule-Based Judging**: Reproducible pass/fail decisions
4. **API-First Design**: Clean endpoints ready for external agent integration

### What This Enables
- **AgentBeats Integration**: Structured reports ready for leaderboards
- **External Agent Testing**: Any white agent can plug in via API
- **Reproducible Evaluation**: Same task produces identical results
- **Debugging Support**: Complete artifacts for failure analysis

## Browser Demo (Optional)

Open these URLs in your browser:
- **Service Info**: http://localhost:8000/
- **Product Catalog**: http://localhost:8000/site/product.html
- **API Docs**: http://localhost:8000/docs

## Troubleshooting

- **Port 8000 in use**: Kill existing processes or change port
- **Playwright issues**: Run `playwright install chromium`
- **Task not found**: Check `data/tasks.json` exists
- **Permission errors**: Ensure write access to `runs/` directory
