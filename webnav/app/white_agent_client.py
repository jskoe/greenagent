"""White agent HTTP client for A2A communication."""
import os
import asyncio
from typing import Dict, Any, Optional, Tuple
import httpx
from .models import WhiteAgentConfig


class WhiteAgentClient:
    """Client for calling remote white agents."""
    
    def __init__(self, default_timeout: int = 30):
        """
        Initialize white agent client.
        
        Args:
            default_timeout: Default timeout in seconds for agent calls
        """
        self.default_timeout = default_timeout
        self.act_path = os.getenv("WHITE_AGENT_ACT_PATH", "/act")
    
    async def call_agent(
        self,
        agent_config: WhiteAgentConfig,
        run_id: str,
        task_id: str,
        instruction: str,
        step_idx: int,
        observation: Dict[str, Any],
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Call a white agent to get the next action.
        
        Args:
            agent_config: White agent configuration
            run_id: Run identifier
            task_id: Task identifier
            instruction: Task instruction
            step_idx: Current step index
            observation: Current observation
            timeout: Optional timeout override
            
        Returns:
            Response dictionary with 'action', 'thoughts', 'info'
            
        Raises:
            TimeoutError: If call times out
            ValueError: If response is invalid
        """
        timeout = timeout or self.default_timeout
        
        # Build request URL
        base_url = agent_config.url.rstrip('/')
        url = f"{base_url}{self.act_path}"
        
        # Build payload
        payload = {
            "run_id": run_id,
            "task_id": task_id,
            "instruction": instruction,
            "step_idx": step_idx,
            "observation": observation,
            "action_space": {
                "allowed": ["click", "type", "select", "scroll", "wait", "stop"]
            }
        }
        
        # Make HTTP request
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                result = response.json()
                
                # Validate response structure
                if "action" not in result:
                    raise ValueError("White agent response missing 'action' field")
                
                return result
                
        except httpx.TimeoutException as e:
            raise TimeoutError(f"White agent call timed out after {timeout}s: {str(e)}")
        except httpx.HTTPStatusError as e:
            raise ValueError(f"White agent returned error status {e.response.status_code}: {str(e)}")
        except httpx.RequestError as e:
            raise ValueError(f"White agent request failed: {str(e)}")
        except ValueError as e:
            raise  # Re-raise validation errors
        except Exception as e:
            raise ValueError(f"Unexpected error calling white agent: {str(e)}")
    
    def validate_action(self, action: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate an action from a white agent.
        
        Args:
            action: Action dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(action, dict):
            return False, "Action must be a dictionary"
        
        action_type = action.get("type")
        if not action_type:
            return False, "Action missing 'type' field"
        
        allowed_types = ["click", "type", "select", "scroll", "wait", "stop"]
        if action_type not in allowed_types:
            return False, f"Invalid action type '{action_type}'. Allowed: {allowed_types}"
        
        # Type-specific validation
        if action_type == "click":
            if "selector" not in action:
                return False, "Click action missing 'selector' field"
        elif action_type == "type":
            if "selector" not in action:
                return False, "Type action missing 'selector' field"
            if "text" not in action:
                return False, "Type action missing 'text' field"
        elif action_type == "select":
            if "selector" not in action:
                return False, "Select action missing 'selector' field"
            if "value" not in action:
                return False, "Select action missing 'value' field"
        elif action_type == "scroll":
            if "delta_y" not in action:
                return False, "Scroll action missing 'delta_y' field"
        elif action_type == "wait":
            if "ms" not in action:
                return False, "Wait action missing 'ms' field"
        elif action_type == "stop":
            if "reason" not in action:
                return False, "Stop action missing 'reason' field"
        
        return True, None

