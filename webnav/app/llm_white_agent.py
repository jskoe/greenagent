"""LLM-based white agent for intelligent web navigation."""
import os
import json
import logging
from typing import Dict, Any, Optional, List
from openai import AsyncOpenAI
import anthropic

logger = logging.getLogger(__name__)


class LLMWhiteAgent:
    """LLM-powered white agent that makes intelligent navigation decisions."""
    
    def __init__(
        self,
        provider: str = "openai",
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 500
    ):
        """
        Initialize LLM white agent.
        
        Args:
            provider: LLM provider ("openai" or "anthropic")
            model: Model name (defaults based on provider)
            api_key: API key (defaults to env var)
            temperature: Sampling temperature (lower = more deterministic)
            max_tokens: Max tokens for response
        """
        self.provider = provider.lower()
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Set defaults based on provider
        if model is None:
            if self.provider == "openai":
                self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            elif self.provider == "anthropic":
                self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022")
            else:
                raise ValueError(f"Unknown provider: {provider}")
        else:
            self.model = model
        
        # Initialize client
        if self.provider == "openai":
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required")
            self.client = AsyncOpenAI(api_key=api_key)
        elif self.provider == "anthropic":
            api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable is required")
            self.client = anthropic.AsyncAnthropic(api_key=api_key)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    async def decide_action(
        self,
        instruction: str,
        step_idx: int,
        observation: Dict[str, Any],
        action_space: Dict[str, Any],
        run_id: Optional[str] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Decide on the next action using LLM.
        
        Args:
            instruction: Task instruction
            step_idx: Current step index
            observation: Current page observation
            action_space: Available action types
            run_id: Optional run identifier
            task_id: Optional task identifier
            
        Returns:
            Dictionary with 'action', 'thoughts', 'info'
        """
        # Build prompt
        prompt = self._build_prompt(instruction, step_idx, observation, action_space)
        
        try:
            if self.provider == "openai":
                response = await self._call_openai(prompt)
            elif self.provider == "anthropic":
                response = await self._call_anthropic(prompt)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
            
            # Parse response
            action_data = self._parse_response(response)
            return action_data
            
        except Exception as e:
            logger.error(f"Error in LLM decision: {str(e)}", exc_info=True)
            # Fallback to safe action
            return {
                "action": {
                    "type": "stop",
                    "reason": f"LLM error: {str(e)}"
                },
                "thoughts": f"Error occurred: {str(e)}",
                "info": {"error": True, "provider": self.provider}
            }
    
    def _build_prompt(
        self,
        instruction: str,
        step_idx: int,
        observation: Dict[str, Any],
        action_space: Dict[str, Any]
    ) -> str:
        """Build the prompt for the LLM."""
        url = observation.get("url", "")
        title = observation.get("title", "")
        dom_summary = observation.get("dom_summary", [])
        
        # Format DOM summary
        dom_elements = []
        for elem in dom_summary[:50]:  # Limit to first 50 elements
            selector = elem.get("selector", "")
            tag = elem.get("tag", "")
            text = elem.get("text", "").strip()[:100]  # Truncate text
            elem_type = elem.get("type", "")
            
            if selector:
                dom_elements.append(f"- {tag} ({elem_type}): selector='{selector}' text='{text}'")
        
        dom_text = "\n".join(dom_elements) if dom_elements else "No interactive elements found"
        
        allowed_actions = action_space.get("allowed", [])
        
        prompt = f"""You are a web navigation agent. Your task is to analyze the current web page and decide on the next action to complete the given instruction.

TASK INSTRUCTION: {instruction}

CURRENT PAGE:
- URL: {url}
- Title: {title}
- Step: {step_idx}

AVAILABLE ELEMENTS ON PAGE:
{dom_text}

AVAILABLE ACTIONS:
{', '.join(allowed_actions)}

ACTION FORMATS:
- click: {{"type": "click", "selector": "css_selector"}}
- type: {{"type": "type", "selector": "css_selector", "text": "text to type"}}
- select: {{"type": "select", "selector": "css_selector", "value": "option_value"}}
- scroll: {{"type": "scroll", "delta_y": 500}}
- wait: {{"type": "wait", "ms": 1000}}
- stop: {{"type": "stop", "reason": "task completed or cannot proceed"}}

INSTRUCTIONS:
1. Analyze the task instruction and current page state
2. Identify the best element to interact with based on the instruction
3. Choose the appropriate action type
4. Use the exact CSS selector from the available elements
5. If the task is complete or you cannot proceed, use "stop" action
6. If you need to see more content, use "scroll" action
7. Return ONLY valid JSON in this format:
{{
  "action": {{"type": "...", ...}},
  "thoughts": "brief explanation of your decision",
  "confidence": 0.0-1.0
}}

Return your response as JSON only, no other text."""
        
        return prompt
    
    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a web navigation agent. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    
    async def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic API."""
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system="You are a web navigation agent. Always respond with valid JSON only.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response into action format."""
        try:
            # Try to extract JSON from response
            response_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1]) if len(lines) > 2 else response_text
            
            # Parse JSON
            data = json.loads(response_text)
            
            # Extract action
            action = data.get("action", {})
            if not action:
                raise ValueError("Response missing 'action' field")
            
            # Ensure action has required fields based on type
            action_type = action.get("type")
            if not action_type:
                raise ValueError("Action missing 'type' field")
            
            # Validate and fix action structure
            if action_type == "click":
                if "selector" not in action:
                    raise ValueError("Click action requires 'selector'")
            elif action_type == "type":
                if "selector" not in action or "text" not in action:
                    raise ValueError("Type action requires 'selector' and 'text'")
            elif action_type == "select":
                if "selector" not in action or "value" not in action:
                    raise ValueError("Select action requires 'selector' and 'value'")
            elif action_type == "scroll":
                if "delta_y" not in action:
                    action["delta_y"] = 500  # Default scroll
            elif action_type == "wait":
                if "ms" not in action:
                    action["ms"] = 1000  # Default wait
            elif action_type == "stop":
                if "reason" not in action:
                    action["reason"] = "Task completed"
            else:
                raise ValueError(f"Unknown action type: {action_type}")
            
            return {
                "action": action,
                "thoughts": data.get("thoughts", ""),
                "info": {
                    "confidence": data.get("confidence", 0.8),
                    "model": self.model,
                    "provider": self.provider
                }
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {response_text[:200]}")
            raise ValueError(f"Invalid JSON response: {str(e)}")
        except Exception as e:
            logger.error(f"Error parsing response: {str(e)}")
            raise

