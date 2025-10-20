import asyncio
from typing import Dict, Optional
from playwright.async_api import BrowserContext
from .models import TaskSpec, Report, TaskRequest
from .browser import BrowserManager
from .white_stub import execute_task_with_limits
from .judge import judge_outcome, validate_task_spec
from .logging_utils import save_run_artifacts, load_task_spec, ensure_runs_directory


class TaskController:
    """Orchestrates the execution of tasks and manages browser resources."""
    
    def __init__(self):
        self.browser_manager: Optional[BrowserManager] = None
        self.tasks_cache: Dict[str, TaskSpec] = {}
        self._initialized = False
    
    async def initialize(self):
        """Initialize the controller and browser manager."""
        if not self._initialized:
            self.browser_manager = BrowserManager()
            await self.browser_manager.start()
            ensure_runs_directory()
            self._initialized = True
    
    async def reset(self):
        """Reset the controller and clean up all resources."""
        if self.browser_manager:
            await self.browser_manager.stop()
            self.browser_manager = None
        
        self.tasks_cache.clear()
        self._initialized = False
    
    async def execute_task(self, task_request: TaskRequest) -> Report:
        """
        Execute a task and return a complete report.
        
        Args:
            task_request: Task request containing task_id
            
        Returns:
            Report with execution results and metrics
            
        Raises:
            ValueError: If task_id is invalid or task execution fails
        """
        if not self._initialized:
            await self.initialize()
        
        task_id = task_request.task_id
        
        # Load task specification
        try:
            task_data = load_task_spec(task_id)
            task_spec = TaskSpec(**task_data)
        except (FileNotFoundError, KeyError, ValueError) as e:
            raise ValueError(f"Failed to load task '{task_id}': {str(e)}")
        
        # Validate task specification
        if not validate_task_spec(task_spec):
            raise ValueError(f"Invalid task specification for '{task_id}'")
        
        # Create a fresh browser context for this task
        context = await self.browser_manager.create_context()
        
        try:
            # Execute the task using the white agent stub
            agent_result = await execute_task_with_limits(context, task_spec)
            
            # Capture the final state of the page
            page = await context.new_page()
            await page.goto(task_spec.start_url, wait_until='domcontentloaded')
            final_html, final_url, screenshot_bytes = await self.browser_manager.capture_state(page)
            await page.close()
            
            # Judge the outcome
            success, metrics, evidence = judge_outcome(task_spec, agent_result, final_html)
            
            # Update evidence with screenshot path
            evidence.screenshot = f"runs/{task_id}/snap.png"
            
            # Create the report
            report = Report(
                task_id=task_id,
                success=success,
                metrics=metrics,
                evidence=evidence,
                logs=agent_result.actions
            )
            
            # Save artifacts to disk
            artifact_paths = save_run_artifacts(
                task_id=task_id,
                report=report,
                final_html=final_html,
                screenshot_bytes=screenshot_bytes,
                actions=agent_result.actions
            )
            
            return report
            
        except Exception as e:
            # Create a failure report
            report = Report(
                task_id=task_id,
                success=False,
                metrics={
                    "duration_sec": 0.0,
                    "step_count": 0,
                    "on_task_domain": False
                },
                evidence={
                    "matched_text": None,
                    "final_url": task_spec.start_url,
                    "screenshot": ""
                },
                logs=[f"error: {str(e)}"]
            )
            
            # Save failure artifacts
            try:
                save_run_artifacts(
                    task_id=task_id,
                    report=report,
                    final_html="<html><body>Error occurred</body></html>",
                    screenshot_bytes=b"",
                    actions=[f"error: {str(e)}"]
                )
            except Exception:
                pass  # Don't fail if we can't save artifacts
            
            raise ValueError(f"Task execution failed: {str(e)}")
            
        finally:
            # Always clean up the browser context
            await self.browser_manager.close_context(context)
    
    async def get_task_spec(self, task_id: str) -> TaskSpec:
        """
        Get a task specification by ID.
        
        Args:
            task_id: Task identifier
            
        Returns:
            TaskSpec object
            
        Raises:
            ValueError: If task_id is invalid
        """
        try:
            task_data = load_task_spec(task_id)
            return TaskSpec(**task_data)
        except (FileNotFoundError, KeyError, ValueError) as e:
            raise ValueError(f"Failed to load task '{task_id}': {str(e)}")
    
    def get_active_context_count(self) -> int:
        """Get the number of currently active browser contexts."""
        if self.browser_manager:
            return self.browser_manager.get_active_context_count()
        return 0


# Global controller instance
_controller: Optional[TaskController] = None


async def get_controller() -> TaskController:
    """Get the global task controller instance."""
    global _controller
    if _controller is None:
        _controller = TaskController()
        await _controller.initialize()
    return _controller


async def cleanup_controller():
    """Clean up the global task controller."""
    global _controller
    if _controller is not None:
        await _controller.reset()
        _controller = None
