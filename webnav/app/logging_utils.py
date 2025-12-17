import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from .models import Report


def save_run_artifacts(
    task_id: str,
    report: Report,
    final_html: str,
    screenshot_bytes: bytes,
    actions: List[str]
) -> Dict[str, str]:
    """
    Save all artifacts from a task run to disk.
    
    Args:
        task_id: Unique task identifier
        report: Task execution report
        final_html: Final HTML content of the page
        screenshot_bytes: Screenshot image bytes
        actions: List of actions performed during execution
        
    Returns:
        Dictionary mapping artifact names to file paths
    """
    # Create runs directory structure
    runs_dir = Path("runs")
    task_dir = runs_dir / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    
    artifact_paths = {}
    
    # Save report JSON
    report_path = task_dir / "report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report.model_dump(), f, indent=2, ensure_ascii=False)
    artifact_paths['report'] = str(report_path)
    
    # Save final HTML
    html_path = task_dir / "final.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(final_html)
    artifact_paths['html'] = str(html_path)
    
    # Save screenshot
    screenshot_path = task_dir / "snap.png"
    with open(screenshot_path, 'wb') as f:
        f.write(screenshot_bytes)
    artifact_paths['screenshot'] = str(screenshot_path)
    
    # Save actions log
    actions_path = task_dir / "actions.log"
    with open(actions_path, 'w', encoding='utf-8') as f:
        for i, action in enumerate(actions, 1):
            f.write(f"{i:03d}: {action}\n")
    artifact_paths['actions'] = str(actions_path)
    
    return artifact_paths


def load_task_spec(task_id: str, tasks_file: str = "data/tasks.json") -> Dict[str, Any]:
    """
    Load a task specification from the tasks JSON file.
    
    Args:
        task_id: Task identifier to load
        tasks_file: Path to the tasks JSON file
        
    Returns:
        Task specification dictionary
        
    Raises:
        FileNotFoundError: If tasks file doesn't exist
        KeyError: If task_id not found in tasks file
        json.JSONDecodeError: If tasks file is invalid JSON
    """
    tasks_path = Path(tasks_file)
    
    if not tasks_path.exists():
        raise FileNotFoundError(f"Tasks file not found: {tasks_file}")
    
    with open(tasks_path, 'r', encoding='utf-8') as f:
        tasks_data = json.load(f)
    
    if task_id not in tasks_data:
        raise KeyError(f"Task '{task_id}' not found in tasks file")
    
    return tasks_data[task_id]


def list_available_tasks(tasks_file: str = "data/tasks.json") -> List[str]:
    """
    List all available task IDs from the tasks file.
    
    Args:
        tasks_file: Path to the tasks JSON file
        
    Returns:
        List of task IDs
        
    Raises:
        FileNotFoundError: If tasks file doesn't exist
        json.JSONDecodeError: If tasks file is invalid JSON
    """
    tasks_path = Path(tasks_file)
    
    if not tasks_path.exists():
        raise FileNotFoundError(f"Tasks file not found: {tasks_file}")
    
    with open(tasks_path, 'r', encoding='utf-8') as f:
        tasks_data = json.load(f)
    
    return list(tasks_data.keys())


def cleanup_run_artifacts(task_id: str) -> bool:
    """
    Clean up artifacts for a specific task run.
    
    Args:
        task_id: Task identifier
        
    Returns:
        True if cleanup was successful, False otherwise
    """
    try:
        task_dir = Path("runs") / task_id
        if task_dir.exists():
            import shutil
            shutil.rmtree(task_dir)
            return True
        return False
    except Exception:
        return False


def get_run_artifacts(task_id: str) -> Dict[str, str]:
    """
    Get paths to existing artifacts for a task run.
    
    Args:
        task_id: Task identifier
        
    Returns:
        Dictionary mapping artifact names to file paths (empty if no artifacts exist)
    """
    task_dir = Path("runs") / task_id
    
    if not task_dir.exists():
        return {}
    
    artifacts = {}
    
    # Check for each expected artifact
    expected_files = {
        'report': 'report.json',
        'html': 'final.html',
        'screenshot': 'snap.png',
        'actions': 'actions.log'
    }
    
    for artifact_name, filename in expected_files.items():
        file_path = task_dir / filename
        if file_path.exists():
            artifacts[artifact_name] = str(file_path)
    
    return artifacts


def ensure_runs_directory():
    """Ensure the runs directory exists."""
    runs_dir = Path("runs")
    runs_dir.mkdir(exist_ok=True)


def ensure_artifacts_directory(run_id: str) -> Path:
    """Ensure the artifacts directory for a run_id exists."""
    artifacts_dir = Path("artifacts") / run_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    return artifacts_dir


def save_run_events(
    run_id: str,
    events: List[Dict[str, Any]]
) -> str:
    """
    Save events to events.jsonl file.
    
    Args:
        run_id: Run identifier
        events: List of event dictionaries
        
    Returns:
        Path to events.jsonl file
    """
    artifacts_dir = ensure_artifacts_directory(run_id)
    events_path = artifacts_dir / "events.jsonl"
    
    with open(events_path, 'w', encoding='utf-8') as f:
        for event in events:
            f.write(json.dumps(event, ensure_ascii=False) + '\n')
    
    return str(events_path)


def save_screenshot(
    run_id: str,
    step_idx: int,
    screenshot_bytes: bytes
) -> str:
    """
    Save a screenshot for a specific step.
    
    Args:
        run_id: Run identifier
        step_idx: Step index
        screenshot_bytes: Screenshot image bytes
        
    Returns:
        Path to screenshot file
    """
    artifacts_dir = ensure_artifacts_directory(run_id)
    screens_dir = artifacts_dir / "screens"
    screens_dir.mkdir(exist_ok=True)
    
    screenshot_path = screens_dir / f"step_{step_idx:03d}.png"
    with open(screenshot_path, 'wb') as f:
        f.write(screenshot_bytes)
    
    return str(screenshot_path)


def save_playwright_trace(
    run_id: str,
    trace_path: str
) -> Optional[str]:
    """
    Save Playwright trace file (if tracing was enabled).
    
    Args:
        run_id: Run identifier
        trace_path: Path to Playwright trace file
        
    Returns:
        Path to trace zip file, or None if not available
    """
    if not trace_path or not Path(trace_path).exists():
        return None
    
    artifacts_dir = ensure_artifacts_directory(run_id)
    trace_dest = artifacts_dir / "pwtrace.zip"
    
    import shutil
    shutil.copy2(trace_path, trace_dest)
    
    return str(trace_dest)


def save_run_log(
    run_id: str,
    log_lines: List[str]
) -> str:
    """
    Save consolidated log file.
    
    Args:
        run_id: Run identifier
        log_lines: List of log lines
        
    Returns:
        Path to log file
    """
    artifacts_dir = ensure_artifacts_directory(run_id)
    log_path = artifacts_dir / "log.txt"
    
    with open(log_path, 'w', encoding='utf-8') as f:
        for line in log_lines:
            f.write(line + '\n')
    
    return str(log_path)


def create_event_record(
    step_idx: int,
    observation_hash: str,
    action: Dict[str, Any],
    execution_result: Dict[str, Any],
    url: str
) -> Dict[str, Any]:
    """
    Create an event record for events.jsonl.
    
    Args:
        step_idx: Step index
        observation_hash: Hash of observation
        action: Action that was requested
        execution_result: Result of action execution
        url: URL after action
        
    Returns:
        Event record dictionary
    """
    return {
        "step_idx": step_idx,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "observation_hash": observation_hash,
        "action": action,
        "execution_result": execution_result,
        "url": url
    }
