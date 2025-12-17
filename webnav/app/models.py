from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class TaskLimits(BaseModel):
    max_steps: int = Field(default=20, description="Maximum number of steps allowed")
    timeout_sec: int = Field(default=60, description="Timeout in seconds")


class TaskExpected(BaseModel):
    css: str = Field(description="CSS selector to find the target element")
    regex: str = Field(description="Regex pattern to match the extracted text")


class TaskAssets(BaseModel):
    snapshot_path: Optional[str] = Field(default=None, description="Path to snapshot file")
    har_path: Optional[str] = Field(default=None, description="Path to HAR file")
    trace_path: Optional[str] = Field(default=None, description="Path to trace file")


class TaskSpec(BaseModel):
    id: str = Field(description="Unique task identifier")
    start_url: str = Field(description="URL to start the task from")
    instruction: str = Field(description="Human-readable instruction for the task")
    expected: Optional[TaskExpected] = Field(default=None, description="Expected outcome specification (legacy)")
    limits: TaskLimits = Field(default_factory=TaskLimits, description="Task execution limits")
    # Mind2Web fields
    benchmark: Optional[str] = Field(default=None, description="Benchmark name")
    split: Optional[str] = Field(default=None, description="Dataset split (train/test/val)")
    index: Optional[int] = Field(default=None, description="Task index in dataset")
    assets: Optional[TaskAssets] = Field(default=None, description="Task assets")
    gold_actions: Optional[List[Dict[str, Any]]] = Field(default=None, description="Gold standard actions for trace matching")
    success_criteria: Optional[Dict[str, Any]] = Field(default=None, description="Success criteria (url_contains, text_present, selector_present)")


class TaskRequest(BaseModel):
    task_id: str = Field(description="ID of the task to execute")


class TaskMetrics(BaseModel):
    duration_sec: float = Field(description="Total execution time in seconds")
    step_count: int = Field(description="Number of steps taken")
    on_task_domain: bool = Field(description="Whether final URL is on the expected domain")


class TaskEvidence(BaseModel):
    matched_text: Optional[str] = Field(description="Text that matched the expected pattern")
    final_url: str = Field(description="Final URL after task execution")
    screenshot: str = Field(description="Path to saved screenshot")


class Report(BaseModel):
    task_id: str = Field(description="Task identifier")
    success: bool = Field(description="Whether the task was completed successfully")
    metrics: TaskMetrics = Field(description="Execution metrics")
    evidence: TaskEvidence = Field(description="Evidence of task completion")
    logs: List[str] = Field(description="List of action logs")


class WhiteAgentResult(BaseModel):
    answer_text: str = Field(description="Extracted answer text")
    evidence_selector: str = Field(description="CSS selector used to extract the answer")
    actions: List[str] = Field(description="List of actions performed")
    final_url: str = Field(description="Final URL after execution")
    duration_sec: float = Field(description="Execution duration in seconds")


class HealthResponse(BaseModel):
    ok: bool = Field(description="Service health status")
    version: Optional[str] = Field(default="1.0.0", description="Service version")


class ResetResponse(BaseModel):
    reset: bool = Field(description="Reset operation status")


# AgentBeats v2 /run endpoint models
class RunTaskSpec(BaseModel):
    task_id: str = Field(description="Task identifier")
    benchmark: str = Field(default="mind2web", description="Benchmark name")
    split: Optional[str] = Field(default=None, description="Dataset split (train/test/val)")
    index: Optional[int] = Field(default=None, description="Task index in dataset")
    instruction: str = Field(description="Task instruction")
    start_url: str = Field(description="Starting URL")
    assets: Optional[TaskAssets] = Field(default=None, description="Task assets")


class WhiteAgentConfig(BaseModel):
    name: str = Field(description="White agent name")
    url: str = Field(description="White agent URL")


class RunLimits(BaseModel):
    max_steps: int = Field(default=20, description="Maximum number of steps")
    timeout_s: int = Field(default=300, description="Timeout in seconds")


class RunRequest(BaseModel):
    run_id: str = Field(description="Unique run identifier")
    task: RunTaskSpec = Field(description="Task specification")
    white_agents: List[WhiteAgentConfig] = Field(description="List of white agents to use")
    limits: RunLimits = Field(default_factory=RunLimits, description="Execution limits")


class RunMetrics(BaseModel):
    final_success: int = Field(description="Final success (0 or 1)")
    steps_taken: int = Field(description="Number of steps taken")
    trace_match_ratio: Optional[float] = Field(default=None, description="Trace match ratio if gold actions available")
    wall_time_s: float = Field(description="Wall clock time in seconds")
    timeouts: int = Field(default=0, description="Number of timeouts")
    invalid_actions: int = Field(default=0, description="Number of invalid actions")


class RunArtifacts(BaseModel):
    log_path: str = Field(description="Path to log file")
    trace_zip: Optional[str] = Field(default=None, description="Path to trace zip")
    screenshots_dir: str = Field(description="Path to screenshots directory")
    playwright_trace: Optional[str] = Field(default=None, description="Path to Playwright trace")


class RunResponse(BaseModel):
    run_id: str = Field(description="Run identifier")
    task_id: str = Field(description="Task identifier")
    success: bool = Field(description="Whether the run was successful")
    metrics: RunMetrics = Field(description="Execution metrics")
    artifacts: RunArtifacts = Field(description="Artifact paths")
    error: Optional[str] = Field(default=None, description="Error message if failed")
