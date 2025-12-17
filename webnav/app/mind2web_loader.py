"""Mind2Web task loader module."""
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from .models import TaskSpec, TaskAssets, TaskLimits


def load_mind2web_task(task_id: str, data_dir: Optional[str] = None) -> TaskSpec:
    """
    Load a Mind2Web task from data directory or local sample file.
    
    Args:
        task_id: Task identifier
        data_dir: Optional directory path to Mind2Web data (from MIND2WEB_DATA_DIR env var)
        
    Returns:
        TaskSpec object
        
    Raises:
        FileNotFoundError: If task file not found
        ValueError: If task data is invalid
    """
    # Try to load from MIND2WEB_DATA_DIR first
    if data_dir:
        task_path = Path(data_dir) / f"{task_id}.json"
        if task_path.exists():
            with open(task_path, 'r', encoding='utf-8') as f:
                task_data = json.load(f)
            return _parse_mind2web_task(task_data)
    
    # Fall back to local sample file
    sample_path = Path(__file__).parent.parent / "data" / "mind2web_sample.json"
    if sample_path.exists():
        with open(sample_path, 'r', encoding='utf-8') as f:
            all_tasks = json.load(f)
        
        if task_id in all_tasks:
            return _parse_mind2web_task(all_tasks[task_id])
    
    raise FileNotFoundError(f"Task '{task_id}' not found in Mind2Web data")


def _parse_mind2web_task(task_data: Dict[str, Any]) -> TaskSpec:
    """Parse Mind2Web task data into TaskSpec."""
    # Extract assets if present
    assets = None
    if "assets" in task_data and task_data["assets"]:
        assets_data = task_data["assets"]
        assets = TaskAssets(
            snapshot_path=assets_data.get("snapshot_path"),
            har_path=assets_data.get("har_path"),
            trace_path=assets_data.get("trace_path")
        )
    
    # Extract limits (default if not present)
    limits = TaskLimits(
        max_steps=task_data.get("limits", {}).get("max_steps", 20),
        timeout_sec=task_data.get("limits", {}).get("timeout_s", 300)
    )
    
    # Build TaskSpec
    task_spec = TaskSpec(
        id=task_data.get("task_id", task_data.get("id", "")),
        start_url=task_data["start_url"],
        instruction=task_data["instruction"],
        expected=None,  # Mind2Web tasks may not have expected field
        limits=limits,
        benchmark=task_data.get("benchmark", "mind2web"),
        split=task_data.get("split"),
        index=task_data.get("index"),
        assets=assets,
        gold_actions=task_data.get("gold_actions"),
        success_criteria=task_data.get("success_criteria")
    )
    
    return task_spec


def load_task_from_run_request(task_data: Dict[str, Any]) -> TaskSpec:
    """
    Load a task from a RunRequest task specification.
    
    Args:
        task_data: Task data from RunRequest
        
    Returns:
        TaskSpec object
    """
    # Extract assets if present
    assets = None
    if task_data.get("assets"):
        assets_data = task_data["assets"]
        assets = TaskAssets(
            snapshot_path=assets_data.get("snapshot_path"),
            har_path=assets_data.get("har_path"),
            trace_path=assets_data.get("trace_path")
        )
    
    # Build TaskSpec
    task_spec = TaskSpec(
        id=task_data["task_id"],
        start_url=task_data["start_url"],
        instruction=task_data["instruction"],
        expected=None,
        limits=TaskLimits(max_steps=20, timeout_sec=300),  # Defaults, will be overridden by RunLimits
        benchmark=task_data.get("benchmark", "mind2web"),
        split=task_data.get("split"),
        index=task_data.get("index"),
        assets=assets,
        gold_actions=None,  # May be provided separately
        success_criteria=None  # May be provided separately
    )
    
    return task_spec

