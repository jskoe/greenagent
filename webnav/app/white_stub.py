import time
import asyncio
from typing import List
from playwright.async_api import BrowserContext, Page
from .models import WhiteAgentResult, TaskSpec


async def execute_task(
    context: BrowserContext,
    task_spec: TaskSpec
) -> WhiteAgentResult:
    """
    Execute a task using the white agent stub.
    
    This is a simple stub that performs DOM extraction based on the expected CSS selector.
    In a real implementation, this would be replaced with an external agent API call.
    
    Args:
        context: Browser context to use for navigation
        task_spec: Task specification containing URL, instruction, and expected outcome
        
    Returns:
        WhiteAgentResult with extracted answer and execution details
    """
    start_time = time.time()
    actions = []
    
    try:
        # Create a new page
        page = await context.new_page()
        actions.append(f"Created new page")
        
        # Navigate to start URL
        await page.goto(task_spec.start_url, wait_until='domcontentloaded')
        actions.append(f"goto {task_spec.start_url}")
        
        # Wait for page to be fully loaded
        await page.wait_for_load_state('networkidle')
        actions.append("wait for page load")
        
        # Extract text using the expected CSS selector
        try:
            # Check if this is a counting task
            if "count" in task_spec.instruction.lower():
                # Count elements matching the selector
                elements = await page.query_selector_all(task_spec.expected.css)
                answer_text = str(len(elements))
                actions.append(f"count {task_spec.expected.css} => {answer_text}")
            else:
                # Regular text extraction
                element = await page.wait_for_selector(task_spec.expected.css, timeout=5000)
                if element:
                    answer_text = await element.text_content()
                    answer_text = answer_text.strip() if answer_text else ""
                    actions.append(f"extract {task_spec.expected.css} => {answer_text}")
                else:
                    answer_text = ""
                    actions.append(f"extract {task_spec.expected.css} => (not found)")
        except Exception as e:
            answer_text = ""
            actions.append(f"extract {task_spec.expected.css} => (error: {str(e)})")
        
        # Get final URL
        final_url = page.url
        
        # Close the page
        await page.close()
        actions.append("close page")
        
    except Exception as e:
        # Handle any errors during execution
        actions.append(f"error: {str(e)}")
        answer_text = ""
        final_url = task_spec.start_url  # Fallback to start URL
    
    # Calculate duration
    duration_sec = time.time() - start_time
    
    return WhiteAgentResult(
        answer_text=answer_text,
        evidence_selector=task_spec.expected.css,
        actions=actions,
        final_url=final_url,
        duration_sec=duration_sec
    )


async def execute_task_with_limits(
    context: BrowserContext,
    task_spec: TaskSpec
) -> WhiteAgentResult:
    """
    Execute a task with timeout and step limits enforced.
    
    Args:
        context: Browser context to use for navigation
        task_spec: Task specification with limits
        
    Returns:
        WhiteAgentResult with execution details
    """
    # For the MVP, we'll implement a simple timeout using asyncio.wait_for
    try:
        result = await asyncio.wait_for(
            execute_task(context, task_spec),
            timeout=task_spec.limits.timeout_sec
        )
        
        # Check step count limit (actions list length)
        if len(result.actions) > task_spec.limits.max_steps:
            result.actions.append(f"exceeded max_steps limit ({task_spec.limits.max_steps})")
        
        return result
        
    except asyncio.TimeoutError:
        # Return a result indicating timeout
        return WhiteAgentResult(
            answer_text="",
            evidence_selector=task_spec.expected.css,
            actions=[f"timeout after {task_spec.limits.timeout_sec}s"],
            final_url=task_spec.start_url,
            duration_sec=task_spec.limits.timeout_sec
        )
