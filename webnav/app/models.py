from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class TaskLimits(BaseModel):
    max_steps: int = Field(default=20, description="Maximum number of steps allowed")
    timeout_sec: int = Field(default=60, description="Timeout in seconds")


class TaskExpected(BaseModel):
    css: str = Field(description="CSS selector to find the target element")
    regex: str = Field(description="Regex pattern to match the extracted text")


class TaskSpec(BaseModel):
    id: str = Field(description="Unique task identifier")
    start_url: str = Field(description="URL to start the task from")
    instruction: str = Field(description="Human-readable instruction for the task")
    expected: TaskExpected = Field(description="Expected outcome specification")
    limits: TaskLimits = Field(description="Task execution limits")


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


class ResetResponse(BaseModel):
    reset: bool = Field(description="Reset operation status")
