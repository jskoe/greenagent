import asyncio
import time
import os
from typing import Dict, Optional, List, Any
from playwright.async_api import BrowserContext, Page
from .models import (
    TaskSpec, Report, TaskRequest, RunRequest, RunResponse, RunMetrics, RunArtifacts,
    WhiteAgentConfig
)
from .browser import BrowserManager
from .white_stub import execute_task_with_limits
from .judge import judge_outcome, validate_task_spec, judge_final_success, compute_trace_match
from .logging_utils import (
    save_run_artifacts, load_task_spec, ensure_runs_directory,
    ensure_artifacts_directory, save_run_events, save_screenshot, save_playwright_trace,
    save_run_log, create_event_record
)
from .mind2web_loader import load_task_from_run_request
from .observation import extract_observation, compute_observation_hash
from .white_agent_client import WhiteAgentClient
from .action_executor import ActionExecutor


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
        
        # Clean up temp trace files
        import glob
        import os
        temp_traces = glob.glob("/tmp/trace_*.zip")
        for trace_file in temp_traces:
            try:
                os.remove(trace_file)
            except Exception:
                pass
    
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
    
    async def run_evaluation(self, run_request: RunRequest) -> RunResponse:
        """
        Run an evaluation with white agent orchestration.
        
        Args:
            run_request: Run request with task, white agents, and limits
            
        Returns:
            RunResponse with metrics and artifacts
        """
        if not self._initialized:
            await self.initialize()
        
        run_id = run_request.run_id
        task_data = run_request.task
        white_agents = run_request.white_agents
        limits = run_request.limits
        
        start_time = time.time()
        executed_actions = []
        events = []
        log_lines = []
        timeouts = 0
        invalid_actions = 0
        error = None
        
        # Load task spec
        try:
            task_spec = load_task_from_run_request(task_data.model_dump())
            task_spec.limits.max_steps = limits.max_steps
            task_spec.limits.timeout_sec = limits.timeout_s
        except Exception as e:
            error = f"Failed to load task: {str(e)}"
            return _create_error_response(run_id, task_data.task_id, error, start_time)
        
        # Create browser context with tracing
        context = None
        page = None
        trace_path = None
        
        try:
            context = await self.browser_manager.create_context()
            
            # Enable Playwright tracing
            trace_file = f"/tmp/trace_{run_id}.zip"
            await context.tracing.start(screenshots=True, snapshots=True)
            
            page = await context.new_page()
            
            # Navigate to start URL
            try:
                await page.goto(task_spec.start_url, wait_until='domcontentloaded', timeout=30000)
                log_lines.append(f"[{run_id}] Navigated to {task_spec.start_url}")
            except Exception as e:
                error = f"Failed to navigate to start URL: {str(e)}"
                return _create_error_response(run_id, task_data.task_id, error, start_time)
            
            # Initialize clients
            white_agent_client = WhiteAgentClient()
            action_executor = ActionExecutor()
            
            # Select first white agent (simple strategy for now)
            selected_agent = white_agents[0] if white_agents else None
            if not selected_agent:
                error = "No white agents provided"
                return _create_error_response(run_id, task_data.task_id, error, start_time)
            
            # Execution loop
            step_idx = 0
            stopped = False
            stop_reason = None
            
            while step_idx < limits.max_steps and not stopped:
                try:
                    # Extract observation
                    screenshot_path = None
                    try:
                        screenshot_bytes = await page.screenshot(full_page=True)
                        screenshot_path = save_screenshot(run_id, step_idx, screenshot_bytes)
                    except Exception:
                        pass  # Screenshot optional
                    
                    observation = await extract_observation(page, screenshot_path)
                    obs_hash = compute_observation_hash(observation)
                    
                    # Call white agent
                    try:
                        agent_response = await white_agent_client.call_agent(
                            agent_config=selected_agent,
                            run_id=run_id,
                            task_id=task_data.task_id,
                            instruction=task_data.instruction,
                            step_idx=step_idx,
                            observation=observation,
                            timeout=30
                        )
                        
                        action = agent_response.get("action", {})
                        
                        # Validate action
                        is_valid, validation_error = white_agent_client.validate_action(action)
                        if not is_valid:
                            invalid_actions += 1
                            log_lines.append(f"[{run_id}] Step {step_idx}: Invalid action - {validation_error}")
                            executed_actions.append({
                                "type": action.get("type", "unknown"),
                                "error": validation_error
                            })
                            
                            # Record event
                            events.append(create_event_record(
                                step_idx=step_idx,
                                observation_hash=obs_hash,
                                action=action,
                                execution_result={"success": False, "error": validation_error},
                                url=page.url
                            ))
                            
                            step_idx += 1
                            continue
                        
                        # Check for stop action
                        if action.get("type") == "stop":
                            stopped = True
                            stop_reason = action.get("reason", "done")
                            log_lines.append(f"[{run_id}] Step {step_idx}: Stop action - {stop_reason}")
                            executed_actions.append(action)
                            
                            events.append(create_event_record(
                                step_idx=step_idx,
                                observation_hash=obs_hash,
                                action=action,
                                execution_result={"success": True, "stop_reason": stop_reason},
                                url=page.url
                            ))
                            break
                        
                        # Execute action
                        execution_result = await action_executor.execute_action(page, action)
                        executed_actions.append(action)
                        
                        log_lines.append(
                            f"[{run_id}] Step {step_idx}: {action.get('type')} - "
                            f"{'success' if execution_result['success'] else 'failed'}"
                        )
                        
                        if not execution_result["success"]:
                            log_lines.append(f"[{run_id}] Step {step_idx}: Error - {execution_result.get('error')}")
                        
                        # Record event
                        events.append(create_event_record(
                            step_idx=step_idx,
                            observation_hash=obs_hash,
                            action=action,
                            execution_result=execution_result,
                            url=execution_result.get("url", page.url)
                        ))
                        
                        step_idx += 1
                        
                    except TimeoutError as e:
                        timeouts += 1
                        log_lines.append(f"[{run_id}] Step {step_idx}: Timeout calling white agent - {str(e)}")
                        step_idx += 1
                        if timeouts >= 3:  # Stop after 3 timeouts
                            stopped = True
                            stop_reason = "too_many_timeouts"
                    except Exception as e:
                        log_lines.append(f"[{run_id}] Step {step_idx}: Error calling white agent - {str(e)}")
                        step_idx += 1
                        if step_idx >= limits.max_steps:
                            stopped = True
                            stop_reason = "max_steps_reached"
                
                except Exception as e:
                    log_lines.append(f"[{run_id}] Step {step_idx}: Unexpected error - {str(e)}")
                    step_idx += 1
                    if step_idx >= limits.max_steps:
                        stopped = True
                        stop_reason = "max_steps_reached"
            
            # Stop tracing and save
            try:
                await context.tracing.stop(path=trace_file)
                trace_path = trace_file
            except Exception:
                pass
            
            # Capture final state
            final_html = await page.content()
            final_url = page.url
            
            # Judge final success
            final_success = judge_final_success(task_spec, final_html, final_url)
            
            # Compute trace match if gold actions available
            trace_match_ratio = None
            if task_spec.gold_actions:
                trace_match_ratio = compute_trace_match(executed_actions, task_spec.gold_actions)
            
            # Compute metrics
            wall_time_s = time.time() - start_time
            metrics = RunMetrics(
                final_success=1 if final_success else 0,
                steps_taken=step_idx,
                trace_match_ratio=trace_match_ratio,
                wall_time_s=wall_time_s,
                timeouts=timeouts,
                invalid_actions=invalid_actions
            )
            
            # Save artifacts
            events_path = save_run_events(run_id, events)
            log_path = save_run_log(run_id, log_lines)
            screenshots_dir = str(ensure_artifacts_directory(run_id) / "screens")
            playwright_trace = save_playwright_trace(run_id, trace_path)
            
            artifacts = RunArtifacts(
                log_path=log_path,
                trace_zip=None,  # Could add trace.zip if needed
                screenshots_dir=screenshots_dir,
                playwright_trace=playwright_trace
            )
            
            return RunResponse(
                run_id=run_id,
                task_id=task_data.task_id,
                success=final_success,
                metrics=metrics,
                artifacts=artifacts,
                error=None
            )
            
        except Exception as e:
            error = f"Evaluation failed: {str(e)}"
            log_lines.append(f"[{run_id}] Error: {error}")
            return _create_error_response(run_id, task_data.task_id, error, start_time)
        
        finally:
            # Cleanup
            if page:
                try:
                    await page.close()
                except Exception:
                    pass
            if context:
                await self.browser_manager.close_context(context)


def _create_error_response(
    run_id: str,
    task_id: str,
    error: str,
    start_time: float
) -> RunResponse:
    """Create an error response."""
    wall_time_s = time.time() - start_time
    
    # Save error log
    try:
        log_path = save_run_log(run_id, [f"[{run_id}] Error: {error}"])
        screenshots_dir = str(ensure_artifacts_directory(run_id) / "screens")
    except Exception:
        log_path = f"artifacts/{run_id}/log.txt"
        screenshots_dir = f"artifacts/{run_id}/screens"
    
    metrics = RunMetrics(
        final_success=0,
        steps_taken=0,
        trace_match_ratio=None,
        wall_time_s=wall_time_s,
        timeouts=0,
        invalid_actions=0
    )
    
    artifacts = RunArtifacts(
        log_path=log_path,
        trace_zip=None,
        screenshots_dir=screenshots_dir,
        playwright_trace=None
    )
    
    return RunResponse(
        run_id=run_id,
        task_id=task_id,
        success=False,
        metrics=metrics,
        artifacts=artifacts,
        error=error
    )


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
