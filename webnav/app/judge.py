import re
from urllib.parse import urlparse
from typing import Tuple, Optional, List, Dict, Any
from .models import TaskSpec, WhiteAgentResult, TaskMetrics, TaskEvidence


def judge_outcome(
    task_spec: TaskSpec,
    agent_result: WhiteAgentResult,
    final_html: str
) -> Tuple[bool, TaskMetrics, TaskEvidence]:
    """
    Judge whether a task was completed successfully based on deterministic rules.
    
    Args:
        task_spec: Original task specification
        agent_result: Result from the white agent execution
        final_html: Final HTML content of the page
        
    Returns:
        Tuple of (success, metrics, evidence)
    """
    # Check if the expected CSS selector exists in the final HTML
    css_selector_exists = _check_css_selector_exists(task_spec.expected.css, final_html)
    
    # Check if the answer text matches the expected regex pattern
    regex_match = _check_regex_match(task_spec.expected.regex, agent_result.answer_text)
    
    # Check if the final URL is on the expected domain
    on_task_domain = _check_domain_match(task_spec.start_url, agent_result.final_url)
    
    # Determine overall success
    success = css_selector_exists and regex_match and on_task_domain
    
    # Create metrics
    metrics = TaskMetrics(
        duration_sec=agent_result.duration_sec,
        step_count=len(agent_result.actions),
        on_task_domain=on_task_domain
    )
    
    # Create evidence
    evidence = TaskEvidence(
        matched_text=agent_result.answer_text if regex_match else None,
        final_url=agent_result.final_url,
        screenshot=""  # Will be filled in by the controller
    )
    
    return success, metrics, evidence


def _check_css_selector_exists(css_selector: str, html_content: str) -> bool:
    """
    Check if a CSS selector would match any element in the HTML.
    
    This is a simplified check that looks for the selector pattern in the HTML.
    For production use, a proper CSS selector engine should be used.
    """
    try:
        # Simple heuristic: check if the selector pattern appears in the HTML
        # This is not perfect but works for simple selectors like #product-3 .price
        
        if css_selector.startswith('#'):
            # ID selector
            element_id = css_selector[1:]
            if '.' in element_id:
                # Compound selector like #product-3 .price
                parts = element_id.split(' ', 1)
                element_id = parts[0]
                class_part = parts[1] if len(parts) > 1 else ""
                
                # Check for ID and class
                id_pattern = f'id="{element_id}"'
                if class_part.startswith('.'):
                    class_name = class_part[1:]
                    class_pattern = f'class="[^"]*{class_name}[^"]*"'
                    return id_pattern in html_content and re.search(class_pattern, html_content)
                else:
                    return id_pattern in html_content
            else:
                # Simple ID selector
                return f'id="{element_id}"' in html_content
        
        elif css_selector.startswith('.'):
            # Class selector
            class_name = css_selector[1:]
            class_pattern = f'class="[^"]*{class_name}[^"]*"'
            return bool(re.search(class_pattern, html_content))
        
        else:
            # Tag selector or other
            return css_selector in html_content
            
    except Exception:
        return False


def _check_regex_match(pattern: str, text: str) -> bool:
    """
    Check if text matches the given regex pattern.
    """
    try:
        return bool(re.search(pattern, text))
    except re.error:
        # Invalid regex pattern
        return False


def _check_domain_match(start_url: str, final_url: str) -> bool:
    """
    Check if the final URL is on the same domain as the start URL.
    """
    try:
        start_domain = urlparse(start_url).netloc
        final_domain = urlparse(final_url).netloc
        
        # For localhost, we're more lenient
        if 'localhost' in start_domain or '127.0.0.1' in start_domain:
            return 'localhost' in final_domain or '127.0.0.1' in final_domain
        
        return start_domain == final_domain
    except Exception:
        return False


def judge_final_success(task_spec: TaskSpec, final_html: str, final_url: str) -> bool:
    """
    Judge final success using success_criteria or legacy expected field.
    
    Args:
        task_spec: Task specification
        final_html: Final HTML content
        final_url: Final URL
        
    Returns:
        True if success criteria are met
    """
    # Use success_criteria if available (Mind2Web format)
    if task_spec.success_criteria:
        criteria = task_spec.success_criteria
        
        # Check URL contains
        if "url_contains" in criteria:
            if criteria["url_contains"] not in final_url:
                return False
        
        # Check text present
        if "text_present" in criteria:
            pattern = criteria["text_present"]
            if not _check_regex_match(pattern, final_html):
                return False
        
        # Check selector present
        if "selector_present" in criteria:
            selector = criteria["selector_present"]
            if not _check_css_selector_exists(selector, final_html):
                return False
        
        return True
    
    # Fall back to legacy expected field
    if task_spec.expected:
        return _check_css_selector_exists(task_spec.expected.css, final_html)
    
    return False


def compute_trace_match(
    executed_actions: List[Dict[str, Any]],
    gold_actions: List[Dict[str, Any]]
) -> float:
    """
    Compute trace match ratio between executed and gold actions.
    
    Args:
        executed_actions: List of executed actions
        gold_actions: List of gold standard actions
        
    Returns:
        Trace match ratio (0.0 to 1.0)
    """
    if not gold_actions or not executed_actions:
        return 0.0
    
    # Normalize gold actions by step index
    gold_by_step = {}
    for gold_action in gold_actions:
        step = gold_action.get("step", len(gold_by_step))
        gold_by_step[step] = gold_action
    
    matches = 0
    total_gold = len(gold_by_step)
    
    if total_gold == 0:
        return 0.0
    
    # Compare each gold action with executed actions
    for step_idx, gold_action in gold_by_step.items():
        if step_idx >= len(executed_actions):
            continue
        
        executed = executed_actions[step_idx]
        
        # Check if action type matches
        if executed.get("type") != gold_action.get("type"):
            continue
        
        # Check if target roughly matches
        if _actions_roughly_match(executed, gold_action):
            matches += 1
    
    return matches / total_gold if total_gold > 0 else 0.0


def _actions_roughly_match(executed: Dict[str, Any], gold: Dict[str, Any]) -> bool:
    """
    Check if two actions roughly match (same type and similar target).
    
    Args:
        executed: Executed action
        gold: Gold action
        
    Returns:
        True if actions roughly match
    """
    # Selector equality
    if executed.get("selector") == gold.get("selector"):
        return True
    
    # For click/type/select, check if selectors are similar
    action_type = executed.get("type")
    if action_type in ["click", "type", "select"]:
        exec_sel = executed.get("selector", "")
        gold_sel = gold.get("selector", "")
        
        # Normalize selectors (remove whitespace)
        exec_sel_norm = "".join(exec_sel.split())
        gold_sel_norm = "".join(gold_sel.split())
        
        if exec_sel_norm == gold_sel_norm:
            return True
        
        # Check if one selector contains the other (for partial matches)
        if exec_sel in gold_sel or gold_sel in exec_sel:
            return True
    
    # For scroll, check delta_y is similar
    if action_type == "scroll":
        exec_delta = executed.get("delta_y", 0)
        gold_delta = gold.get("delta_y", 0)
        return abs(exec_delta - gold_delta) < 100  # Within 100px
    
    return False


def validate_task_spec(task_spec: TaskSpec) -> bool:
    """
    Validate that a task specification is well-formed.
    
    Args:
        task_spec: Task specification to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        # Check required fields
        if not task_spec.id or not task_spec.start_url or not task_spec.instruction:
            return False
        
        # For legacy format, check expected field
        if task_spec.expected:
            if not task_spec.expected.css or not task_spec.expected.regex:
                return False
            
            # Validate regex pattern
            try:
                re.compile(task_spec.expected.regex)
            except re.error:
                return False
        
        # For Mind2Web format, check success_criteria
        elif task_spec.success_criteria:
            # At least one criterion must be present
            if not any(key in task_spec.success_criteria for key in ["url_contains", "text_present", "selector_present"]):
                return False
        
        # Validate limits
        if task_spec.limits.max_steps <= 0 or task_spec.limits.timeout_sec <= 0:
            return False
        
        return True
        
    except Exception:
        return False
