"""Action execution module for Playwright."""
from typing import Dict, Any, Optional
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError


class ActionExecutor:
    """Executes actions in Playwright browser context."""
    
    def __init__(self, default_timeout: int = 10000):
        """
        Initialize action executor.
        
        Args:
            default_timeout: Default timeout in milliseconds
        """
        self.default_timeout = default_timeout
    
    async def execute_action(self, page: Page, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an action on a page.
        
        Args:
            page: Playwright page object
            action: Action dictionary with 'type' and action-specific fields
            
        Returns:
            Dictionary with 'success', 'error', 'url' fields
        """
        action_type = action.get("type")
        result = {
            "success": False,
            "error": None,
            "url": page.url
        }
        
        try:
            if action_type == "click":
                selector = action["selector"]
                await page.click(selector, timeout=self.default_timeout)
                result["success"] = True
                
            elif action_type == "type":
                selector = action["selector"]
                text = action["text"]
                await page.fill(selector, text, timeout=self.default_timeout)
                
                if action.get("press_enter", False):
                    await page.press(selector, "Enter", timeout=self.default_timeout)
                
                result["success"] = True
                
            elif action_type == "select":
                selector = action["selector"]
                value = action["value"]
                await page.select_option(selector, value, timeout=self.default_timeout)
                result["success"] = True
                
            elif action_type == "scroll":
                delta_y = action.get("delta_y", 0)
                await page.evaluate(f"window.scrollBy(0, {delta_y})")
                result["success"] = True
                
            elif action_type == "wait":
                import asyncio
                ms = action.get("ms", 500)
                await asyncio.sleep(ms / 1000.0)
                result["success"] = True
                
            elif action_type == "stop":
                result["success"] = True
                result["stop_reason"] = action.get("reason", "done")
                
            else:
                result["error"] = f"Unknown action type: {action_type}"
            
            # Update URL after action
            result["url"] = page.url
            
        except PlaywrightTimeoutError as e:
            result["error"] = f"Timeout executing {action_type}: {str(e)}"
        except Exception as e:
            result["error"] = f"Error executing {action_type}: {str(e)}"
        
        return result

