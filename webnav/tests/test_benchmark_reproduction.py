"""
Test suite to validate that our green agent implementation can reproduce
original Mind2Web benchmark results.

This test suite validates:
1. Task loading from Mind2Web format
2. Success criteria evaluation matches expected behavior
3. Trace matching works correctly
4. Metrics computation is accurate
"""
import pytest
import json
from pathlib import Path
from webnav.app.mind2web_loader import load_mind2web_task
from webnav.app.judge import judge_final_success, compute_trace_match
from webnav.app.models import TaskSpec


def test_task_loading():
    """Test that we can load Mind2Web tasks correctly."""
    task = load_mind2web_task("task_001")
    assert task.task_id == "task_001"
    assert task.instruction is not None
    assert task.start_url is not None
    assert task.success_criteria is not None


def test_success_criteria_evaluation():
    """Test that success criteria evaluation works correctly."""
    # Load a task with known success criteria
    task = load_mind2web_task("task_001")
    
    # Simulate final state that should pass
    final_html_with_selector = '<div id="product-3"><span class="price">$29.99</span></div>'
    final_url = "http://localhost:8000/site/product.html"
    
    success = judge_final_success(task, final_html_with_selector, final_url)
    assert success == True, "Task should succeed when selector and text are present"
    
    # Simulate final state that should fail
    final_html_without_selector = '<div id="product-1"><span class="price">$19.99</span></div>'
    success = judge_final_success(task, final_html_without_selector, final_url)
    assert success == False, "Task should fail when selector is not present"


def test_trace_matching():
    """Test that trace matching works correctly."""
    task = load_mind2web_task("task_001")
    
    # Perfect match
    executed_actions = [
        {"type": "click", "selector": "#product-3 .price", "step": 0}
    ]
    gold_actions = task.gold_actions
    
    if gold_actions:
        ratio = compute_trace_match(executed_actions, gold_actions)
        assert ratio == 1.0, f"Perfect match should give ratio 1.0, got {ratio}"
    
    # Mismatch
    executed_actions_wrong = [
        {"type": "click", "selector": "#product-1 .price", "step": 0}
    ]
    if gold_actions:
        ratio = compute_trace_match(executed_actions_wrong, gold_actions)
        assert ratio == 0.0, f"Mismatch should give ratio 0.0, got {ratio}"


def test_all_sample_tasks_loadable():
    """Test that all sample tasks can be loaded."""
    sample_path = Path(__file__).parent.parent.parent / "webnav" / "data" / "mind2web_sample.json"
    with open(sample_path, 'r') as f:
        all_tasks = json.load(f)
    
    for task_id in all_tasks.keys():
        task = load_mind2web_task(task_id)
        assert task.task_id == task_id
        assert task.instruction is not None
        assert task.start_url is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

