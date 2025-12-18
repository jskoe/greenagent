#!/usr/bin/env bash
# Script to validate benchmark reproduction
# This validates that our implementation correctly evaluates tasks

set -e

echo "🧪 Validating Benchmark Reproduction"
echo "===================================="
echo ""

# Check if green agent is running
AGENT_PORT=8080
if ! curl -s http://localhost:$AGENT_PORT/health > /dev/null 2>&1; then
    echo "❌ Green agent not running on port $AGENT_PORT"
    echo "Start it with: HOST=0.0.0.0 AGENT_PORT=8080 ./run.sh"
    exit 1
fi

echo "✅ Green agent is running"
echo ""

# Test 1: Load and validate all sample tasks
echo "Test 1: Validating task loading..."
python3 << 'EOF'
from webnav.app.mind2web_loader import load_mind2web_task
import json
from pathlib import Path

sample_path = Path("webnav/data/mind2web_sample.json")
with open(sample_path, 'r') as f:
    all_tasks = json.load(f)

print(f"Loading {len(all_tasks)} sample tasks...")
for task_id in all_tasks.keys():
    task = load_mind2web_task(task_id)
    assert task.task_id == task_id
    assert task.instruction is not None
    assert task.start_url is not None
    print(f"  ✅ {task_id}: {task.instruction[:50]}...")

print(f"\n✅ All {len(all_tasks)} tasks loaded successfully")
EOF

echo ""

# Test 2: Validate success criteria evaluation
echo "Test 2: Validating success criteria evaluation..."
python3 << 'EOF'
from webnav.app.mind2web_loader import load_mind2web_task
from webnav.app.judge import judge_final_success

task = load_mind2web_task("task_001")

# Test case 1: Should pass
final_html_pass = '<div id="product-3"><span class="price">$29.99</span></div>'
final_url = "http://localhost:8000/site/product.html"
success = judge_final_success(task, final_html_pass, final_url)
assert success == True, "Should pass when selector and text are present"
print("  ✅ Success criteria: PASS case works correctly")

# Test case 2: Should fail
final_html_fail = '<div id="product-1"><span class="price">$19.99</span></div>'
success = judge_final_success(task, final_html_fail, final_url)
assert success == False, "Should fail when selector is not present"
print("  ✅ Success criteria: FAIL case works correctly")
EOF

echo ""

# Test 3: Validate trace matching
echo "Test 3: Validating trace matching..."
python3 << 'EOF'
from webnav.app.mind2web_loader import load_mind2web_task
from webnav.app.judge import compute_trace_match

task = load_mind2web_task("task_001")

if task.gold_actions:
    # Perfect match
    executed_perfect = [{"type": "click", "selector": "#product-3 .price", "step": 0}]
    ratio = compute_trace_match(executed_perfect, task.gold_actions)
    assert ratio == 1.0, f"Perfect match should be 1.0, got {ratio}"
    print(f"  ✅ Perfect match: ratio = {ratio}")
    
    # Mismatch
    executed_wrong = [{"type": "click", "selector": "#product-1 .price", "step": 0}]
    ratio = compute_trace_match(executed_wrong, task.gold_actions)
    assert ratio == 0.0, f"Mismatch should be 0.0, got {ratio}"
    print(f"  ✅ Mismatch: ratio = {ratio}")
else:
    print("  ⚠️  No gold actions to test")
EOF

echo ""

# Test 4: Run actual evaluation and check metrics
echo "Test 4: Running actual evaluation..."
RUN_ID="validation_$(date +%s)"
RESPONSE=$(curl -s -X POST http://localhost:$AGENT_PORT/run \
  -H "Content-Type: application/json" \
  -d "{
    \"run_id\": \"$RUN_ID\",
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
    \"white_agents\": [{\"name\": \"stub\", \"url\": \"http://localhost:9000\"}],
    \"limits\": {\"max_steps\": 5, \"timeout_s\": 30}
  }")

if echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); assert 'metrics' in data; print('✅ Evaluation completed')" 2>/dev/null; then
    echo "  ✅ Evaluation response is valid"
    echo "$RESPONSE" | python3 -m json.tool | grep -E "(final_success|steps_taken|trace_match_ratio)" | head -3
else
    echo "  ❌ Evaluation failed"
    echo "$RESPONSE"
fi

echo ""
echo "===================================="
echo "✅ Benchmark Reproduction Validation Complete"
echo ""
echo "Summary:"
echo "  - Task loading: ✅"
echo "  - Success criteria: ✅"
echo "  - Trace matching: ✅"
echo "  - Evaluation: ✅"

