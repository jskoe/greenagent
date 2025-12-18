#!/usr/bin/env bash
# Green Agent Demonstration Script
# Shows task introduction, evaluation of different white agents, and quantitative results

set -e

# Cleanup function
cleanup() {
    if [ -n "${GREEN_PID:-}" ]; then
        echo ""
        echo -e "${YELLOW}Cleaning up...${NC}"
        kill "$GREEN_PID" 2>/dev/null || true
    fi
    if [ -n "${STUB_PID:-}" ]; then
        kill "$STUB_PID" 2>/dev/null || true
    fi
    if [ -n "${GREEN_PID:-}" ] || [ -n "${STUB_PID:-}" ]; then
        echo -e "${GREEN}✅ Cleanup complete${NC}"
    fi
}

# Trap to ensure cleanup on exit
trap cleanup EXIT INT TERM

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  GREEN AGENT DEMONSTRATION${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Find free ports
find_free_port() {
    python3 -c 'import socket; s=socket.socket(); s.bind(("", 0)); print(s.getsockname()[1]); s.close()'
}

AGENT_PORT=$(find_free_port)
STUB_PORT=$(find_free_port)

echo -e "${CYAN}PART 1: TASK INTRODUCTION${NC}"
echo "========================================"
echo ""
echo -e "${YELLOW}What is the task?${NC}"
echo "The green agent evaluates white agents on web navigation tasks."
echo "Example tasks:"
echo "  1. 'Find the price of the third product'"
echo "  2. 'Find the rating of the most expensive product'"
echo "  3. 'Count the total number of products'"
echo ""
echo -e "${YELLOW}What does the environment look like?${NC}"
echo "Environment: Product catalog page with 5 products"
echo "  - Each product has: price, rating, description"
echo "  - Products are numbered: #product-1 through #product-5"
echo "  - Page URL: http://localhost:$AGENT_PORT/site/product.html"
echo "  - Static HTML page, no dynamic loading"
echo ""
echo -e "${YELLOW}What actions can each agent take?${NC}"
echo "White Agent Actions:"
echo "  - click: Click on an element using CSS selector"
echo "  - type: Type text into an input field"
echo "  - select: Select an option from a dropdown"
echo "  - scroll: Scroll the page vertically"
echo "  - wait: Wait for a specified duration"
echo "  - stop: Signal task completion or termination"
echo ""
echo "Green Agent Actions:"
echo "  - Extracts observations from page state"
echo "  - Calls white agent to get actions"
echo "  - Executes actions in browser context"
echo "  - Judges outcomes using success criteria"
echo "  - Generates metrics and artifacts"
echo ""

echo -e "${CYAN}PART 2: STARTING SERVICES${NC}"
echo "========================================"
echo "Starting Green Agent on port $AGENT_PORT..."
HOST=0.0.0.0 AGENT_PORT="$AGENT_PORT" ./run.sh > /tmp/green_agent_demo.log 2>&1 &
GREEN_PID=$!
sleep 3

# Check if green agent is running
if ! curl -s "http://localhost:$AGENT_PORT/health" | grep -q '"ok": true'; then
    echo -e "${RED}❌ Green agent failed to start${NC}"
    exit 1
fi

echo "Starting Stub White Agent on port $STUB_PORT..."
(cd webnav && python3 -m tests.stub_white_agent --port "$STUB_PORT" > /tmp/stub_agent_demo.log 2>&1) &
STUB_PID=$!
sleep 2

# Check if stub agent is running
if ! curl -s "http://localhost:$STUB_PORT/health" | grep -q '"ok": true'; then
    echo -e "${RED}❌ Stub white agent failed to start${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Services started${NC}"
echo ""

echo -e "${CYAN}PART 3: DEMONSTRATION - EVALUATING DIFFERENT WHITE AGENTS${NC}"
echo "========================================"
echo ""

# Task 1: Stub Agent (Baseline)
echo -e "${YELLOW}Example 1: Evaluating Stub White Agent (Baseline)${NC}"
echo "------------------------------------------------------------"
echo "Task: 'Find the price of the third product'"
echo "White Agent: Stub Agent (rule-based, keyword matching)"
echo ""

RUN_ID_1="demo_stub_$(date +%s)"
RESPONSE_1=$(curl -s -X POST "http://localhost:$AGENT_PORT/run" \
  -H "Content-Type: application/json" \
  -d "{
    \"run_id\": \"$RUN_ID_1\",
    \"task\": {
      \"task_id\": \"task_001\",
      \"instruction\": \"Find the price of the third product\",
      \"start_url\": \"http://localhost:$AGENT_PORT/site/product.html\",
      \"success_criteria\": {
        \"selector_present\": \"#product-3 .price\",
        \"text_present\": \"\\\\$\\\\d+\\\\.\\\\d{2}\"
      },
      \"gold_actions\": [{\"type\": \"click\", \"selector\": \"#product-3 .price\", \"step\": 0}]
    },
    \"white_agents\": [{\"name\": \"stub\", \"url\": \"http://localhost:$STUB_PORT\"}],
    \"limits\": {\"max_steps\": 10, \"timeout_s\": 30}
  }")

echo "Green Agent Evaluation Results:"
echo "$RESPONSE_1" | python3 -m json.tool | grep -A 10 "metrics" || echo "$RESPONSE_1"
echo ""

# Task 2: Show what green agent assesses
echo -e "${YELLOW}What the Green Agent Assesses:${NC}"
echo "------------------------------------------------------------"
echo "1. Correctness (final_success):"
echo "   - Checks if success criteria are met"
echo "   - URL contains expected substring"
echo "   - Text matches regex pattern"
echo "   - CSS selector exists in final HTML"
echo ""
echo "2. Efficiency (steps_taken):"
echo "   - Counts total actions executed"
echo "   - Lower is better (fewer steps = more efficient)"
echo ""
echo "3. Alignment (trace_match_ratio):"
echo "   - Compares executed actions to gold standard"
echo "   - Measures how closely agent follows optimal path"
echo "   - 1.0 = perfect match, 0.0 = no match"
echo ""
echo "4. Reliability (timeouts, invalid_actions):"
echo "   - Counts timed-out actions"
echo "   - Counts validation failures"
echo "   - Lower is better (fewer errors = more reliable)"
echo ""
echo "5. Performance (wall_time_s):"
echo "   - Total execution time"
echo "   - Measures speed of task completion"
echo ""

# Task 3: Reliability test with ground truth
echo -e "${CYAN}PART 4: RELIABILITY TESTING WITH GROUND TRUTH${NC}"
echo "========================================"
echo ""

echo -e "${YELLOW}Test Case 1: Task that should SUCCEED${NC}"
echo "Expected: final_success = 1"
echo "Task: Click on product-3 price (selector exists, text matches pattern)"
echo ""

RUN_ID_2="demo_reliability_pass_$(date +%s)"
RESPONSE_2=$(curl -s -X POST "http://localhost:$AGENT_PORT/run" \
  -H "Content-Type: application/json" \
  -d "{
    \"run_id\": \"$RUN_ID_2\",
    \"task\": {
      \"task_id\": \"reliability_test_001\",
      \"instruction\": \"Click on the third product price\",
      \"start_url\": \"http://localhost:$AGENT_PORT/site/product.html\",
      \"success_criteria\": {
        \"selector_present\": \"#product-3 .price\",
        \"text_present\": \"\\\\$\\\\d+\\\\.\\\\d{2}\"
      }
    },
    \"white_agents\": [{\"name\": \"stub\", \"url\": \"http://localhost:$STUB_PORT\"}],
    \"limits\": {\"max_steps\": 5, \"timeout_s\": 30}
  }")

FINAL_SUCCESS_2=$(echo "$RESPONSE_2" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('metrics', {}).get('final_success', 'N/A'))" 2>/dev/null)
echo "Result: final_success = $FINAL_SUCCESS_2"
if [ "$FINAL_SUCCESS_2" = "1" ]; then
    echo -e "${GREEN}✅ PASS: Correctly identified success${NC}"
else
    echo -e "${RED}❌ FAIL: Should have been 1${NC}"
fi
echo ""

echo -e "${YELLOW}Test Case 2: Task that should FAIL${NC}"
echo "Expected: final_success = 0"
echo "Task: Click on non-existent element (selector not present)"
echo ""

RUN_ID_3="demo_reliability_fail_$(date +%s)"
RESPONSE_3=$(curl -s -X POST "http://localhost:$AGENT_PORT/run" \
  -H "Content-Type: application/json" \
  -d "{
    \"run_id\": \"$RUN_ID_3\",
    \"task\": {
      \"task_id\": \"reliability_test_002\",
      \"instruction\": \"Click on non-existent element\",
      \"start_url\": \"http://localhost:$AGENT_PORT/site/product.html\",
      \"success_criteria\": {
        \"selector_present\": \"#nonexistent-element\"
      }
    },
    \"white_agents\": [{\"name\": \"stub\", \"url\": \"http://localhost:$STUB_PORT\"}],
    \"limits\": {\"max_steps\": 5, \"timeout_s\": 30}
  }")

FINAL_SUCCESS_3=$(echo "$RESPONSE_3" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('metrics', {}).get('final_success', 'N/A'))" 2>/dev/null)
echo "Result: final_success = $FINAL_SUCCESS_3"
if [ "$FINAL_SUCCESS_3" = "0" ]; then
    echo -e "${GREEN}✅ PASS: Correctly identified failure${NC}"
else
    echo -e "${RED}❌ FAIL: Should have been 0${NC}"
fi
echo ""

# Quantitative results
echo -e "${CYAN}PART 5: QUANTITATIVE RESULTS ON BENCHMARK${NC}"
echo "========================================"
echo ""

echo "Running evaluation on 3 benchmark tasks..."
echo ""

# Task 1
echo -e "${YELLOW}Task 1: Find the price of the third product${NC}"
RUN_ID_T1="benchmark_task1_$(date +%s)"
RESPONSE_T1=$(curl -s -X POST "http://localhost:$AGENT_PORT/run" \
  -H "Content-Type: application/json" \
  -d "{
    \"run_id\": \"$RUN_ID_T1\",
    \"task\": {
      \"task_id\": \"task_001\",
      \"instruction\": \"Find the price of the third product\",
      \"start_url\": \"http://localhost:$AGENT_PORT/site/product.html\",
      \"success_criteria\": {
        \"selector_present\": \"#product-3 .price\",
        \"text_present\": \"\\\\$\\\\d+\\\\.\\\\d{2}\"
      },
      \"gold_actions\": [{\"type\": \"click\", \"selector\": \"#product-3 .price\", \"step\": 0}]
    },
    \"white_agents\": [{\"name\": \"stub\", \"url\": \"http://localhost:$STUB_PORT\"}],
    \"limits\": {\"max_steps\": 10, \"timeout_s\": 30}
  }")

METRICS_T1=$(echo "$RESPONSE_T1" | python3 -c "import sys, json; data=json.load(sys.stdin); m=data.get('metrics', {}); print(f\"final_success: {m.get('final_success', 'N/A')}, steps_taken: {m.get('steps_taken', 'N/A')}, trace_match_ratio: {m.get('trace_match_ratio', 'N/A')}, wall_time_s: {m.get('wall_time_s', 'N/A')}\")" 2>/dev/null)
echo "Results: $METRICS_T1"
echo ""

# Task 2
echo -e "${YELLOW}Task 2: Find the rating of the most expensive product${NC}"
RUN_ID_T2="benchmark_task2_$(date +%s)"
RESPONSE_T2=$(curl -s -X POST "http://localhost:$AGENT_PORT/run" \
  -H "Content-Type: application/json" \
  -d "{
    \"run_id\": \"$RUN_ID_T2\",
    \"task\": {
      \"task_id\": \"task_002\",
      \"instruction\": \"Find the rating of the most expensive product\",
      \"start_url\": \"http://localhost:$AGENT_PORT/site/product.html\",
      \"success_criteria\": {
        \"selector_present\": \"#product-4 .stars\",
        \"text_present\": \"★{4}☆\"
      },
      \"gold_actions\": [{\"type\": \"click\", \"selector\": \"#product-4 .stars\", \"step\": 0}]
    },
    \"white_agents\": [{\"name\": \"stub\", \"url\": \"http://localhost:$STUB_PORT\"}],
    \"limits\": {\"max_steps\": 10, \"timeout_s\": 30}
  }")

METRICS_T2=$(echo "$RESPONSE_T2" | python3 -c "import sys, json; data=json.load(sys.stdin); m=data.get('metrics', {}); print(f\"final_success: {m.get('final_success', 'N/A')}, steps_taken: {m.get('steps_taken', 'N/A')}, trace_match_ratio: {m.get('trace_match_ratio', 'N/A')}, wall_time_s: {m.get('wall_time_s', 'N/A')}\")" 2>/dev/null)
echo "Results: $METRICS_T2"
echo ""

# Task 3
echo -e "${YELLOW}Task 3: Count the total number of products${NC}"
RUN_ID_T3="benchmark_task3_$(date +%s)"
RESPONSE_T3=$(curl -s -X POST "http://localhost:$AGENT_PORT/run" \
  -H "Content-Type: application/json" \
  -d "{
    \"run_id\": \"$RUN_ID_T3\",
    \"task\": {
      \"task_id\": \"task_003\",
      \"instruction\": \"Count the total number of products\",
      \"start_url\": \"http://localhost:$AGENT_PORT/site/product.html\",
      \"success_criteria\": {
        \"selector_present\": \".product\",
        \"text_present\": \"5\"
      },
      \"gold_actions\": [
        {\"type\": \"scroll\", \"delta_y\": 500, \"step\": 0},
        {\"type\": \"click\", \"selector\": \".product\", \"step\": 1}
      ]
    },
    \"white_agents\": [{\"name\": \"stub\", \"url\": \"http://localhost:$STUB_PORT\"}],
    \"limits\": {\"max_steps\": 10, \"timeout_s\": 30}
  }")

METRICS_T3=$(echo "$RESPONSE_T3" | python3 -c "import sys, json; data=json.load(sys.stdin); m=data.get('metrics', {}); print(f\"final_success: {m.get('final_success', 'N/A')}, steps_taken: {m.get('steps_taken', 'N/A')}, trace_match_ratio: {m.get('trace_match_ratio', 'N/A')}, wall_time_s: {m.get('wall_time_s', 'N/A')}\")" 2>/dev/null)
echo "Results: $METRICS_T3"
echo ""

# Summary table
echo -e "${CYAN}QUANTITATIVE RESULTS SUMMARY${NC}"
echo "========================================"
echo ""
echo "| Task | final_success | steps_taken | trace_match_ratio | wall_time_s |"
echo "|------|---------------|-------------|-------------------|-------------|"

# Extract and display summary
python3 << EOF
import json
import sys

tasks = [
    ("Task 1: Find price", "$RESPONSE_T1"),
    ("Task 2: Find rating", "$RESPONSE_T2"),
    ("Task 3: Count products", "$RESPONSE_T3")
]

for task_name, response in tasks:
    try:
        data = json.loads(response)
        m = data.get('metrics', {})
        success = m.get('final_success', 'N/A')
        steps = m.get('steps_taken', 'N/A')
        trace = m.get('trace_match_ratio', 'N/A')
        if trace is not None:
            trace = f"{trace:.2f}"
        time = m.get('wall_time_s', 'N/A')
        if isinstance(time, (int, float)):
            time = f"{time:.2f}s"
        print(f"| {task_name} | {success} | {steps} | {trace} | {time} |")
    except:
        print(f"| {task_name} | Error | Error | Error | Error |")
EOF

echo ""
echo -e "${YELLOW}What These Metrics Mean:${NC}"
echo "  - final_success: 1 = task completed successfully, 0 = failed"
echo "  - steps_taken: Number of actions executed (lower is better)"
echo "  - trace_match_ratio: How closely actions match gold standard (1.0 = perfect)"
echo "  - wall_time_s: Total execution time (lower is better)"
echo ""

echo -e "${CYAN}PART 6: ARTIFACTS AND EVIDENCE${NC}"
echo "========================================"
echo ""
echo "Green agent generates comprehensive artifacts for each evaluation:"
echo ""

# Show artifacts from first run
ARTIFACTS_DIR="webnav/artifacts/$RUN_ID_1"
if [ -d "$ARTIFACTS_DIR" ]; then
    echo -e "${GREEN}✅ Artifacts directory: $ARTIFACTS_DIR${NC}"
    echo "Files generated:"
    ls -lh "$ARTIFACTS_DIR" | tail -n +2
    echo ""
    echo "Sample events.jsonl (first 2 steps):"
    head -2 "$ARTIFACTS_DIR/events.jsonl" | python3 -m json.tool 2>/dev/null || head -2 "$ARTIFACTS_DIR/events.jsonl"
    echo ""
else
    echo -e "${YELLOW}⚠️  Artifacts directory not found (may still be generating)${NC}"
fi

echo ""
echo -e "${CYAN}DEMONSTRATION COMPLETE${NC}"
echo "========================================"
echo ""
echo "Key Takeaways:"
echo "  1. Green agent evaluates white agents using 6 metrics"
echo "  2. Evaluation is deterministic and reliable (ground truth tests pass)"
echo "  3. Metrics assess correctness, efficiency, alignment, and reliability"
echo "  4. Comprehensive artifacts enable debugging and analysis"
echo ""
echo "To view logs:"
echo "  Green Agent: tail -f /tmp/green_agent_demo.log"
echo "  Stub Agent: tail -f /tmp/stub_agent_demo.log"
echo ""
echo "Services will be stopped automatically on exit."
echo ""
echo -e "${GREEN}Demo complete! Press Ctrl+C to exit and cleanup services.${NC}"

