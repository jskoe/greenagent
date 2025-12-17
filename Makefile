.PHONY: install dev test_run clean

install:
	cd webnav && pip install -r requirements.txt
	cd webnav && playwright install chromium

dev:
	cd webnav && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

test_run:
	@echo "Starting stub white agent..."
	cd webnav && python -m tests.stub_white_agent &
	@sleep 2
	@echo "Running test evaluation..."
	@curl -X POST http://localhost:8000/run \
		-H "Content-Type: application/json" \
		-d '{"run_id":"test_001","task":{"task_id":"task_001","benchmark":"mind2web","instruction":"Find the price of the third product","start_url":"http://localhost:8000/site/product.html"},"white_agents":[{"name":"stub","url":"http://localhost:9000"}],"limits":{"max_steps":10,"timeout_s":60}}' | python -m json.tool
	@pkill -f stub_white_agent || true

clean:
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf webnav/runs/* webnav/artifacts/* 2>/dev/null || true

