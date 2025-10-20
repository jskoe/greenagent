import re
from urllib.parse import urlparse
from typing import Tuple, Optional
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
        
        if not task_spec.expected.css or not task_spec.expected.regex:
            return False
        
        # Validate regex pattern
        try:
            re.compile(task_spec.expected.regex)
        except re.error:
            return False
        
        # Validate limits
        if task_spec.limits.max_steps <= 0 or task_spec.limits.timeout_sec <= 0:
            return False
        
        return True
        
    except Exception:
        return False
