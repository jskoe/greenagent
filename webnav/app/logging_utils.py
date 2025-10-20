import os
import json
from pathlib import Path
from typing import Dict, Any, List
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
