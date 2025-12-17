"""Observation extraction module for white agents."""
from typing import Dict, Any, List, Optional
from playwright.async_api import Page


async def extract_observation(page: Page, screenshot_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract observation from current page state for white agent.
    
    Args:
        page: Playwright page object
        screenshot_path: Optional path to screenshot (if saved)
        
    Returns:
        Dictionary with observation data
    """
    # Get basic page info
    current_url = page.url
    page_title = await page.title()
    
    # Extract DOM summary (interactive elements)
    dom_summary = await _extract_dom_summary(page)
    
    observation = {
        "url": current_url,
        "title": page_title,
        "dom_summary": dom_summary
    }
    
    if screenshot_path:
        observation["screenshot_path"] = screenshot_path
    
    return observation


async def _extract_dom_summary(page: Page, max_elements: int = 100) -> List[Dict[str, Any]]:
    """
    Extract a summary of interactive elements from the DOM.
    
    Args:
        page: Playwright page object
        max_elements: Maximum number of elements to extract
        
    Returns:
        List of element summaries
    """
    # Extract interactive elements using JavaScript
    elements = await page.evaluate(f"""
        () => {{
            const elements = [];
            const selectors = [
                'a[href]',
                'button',
                'input[type="text"]',
                'input[type="email"]',
                'input[type="password"]',
                'input[type="search"]',
                'input[type="number"]',
                'textarea',
                'select',
                '[role="button"]',
                '[role="link"]',
                '[onclick]',
                '[data-testid]',
                '[id]'
            ];
            
            for (const selector of selectors) {{
                const nodes = document.querySelectorAll(selector);
                for (const node of nodes) {{
                    if (elements.length >= {max_elements}) break;
                    
                    // Skip if not visible
                    const rect = node.getBoundingClientRect();
                    if (rect.width === 0 && rect.height === 0) continue;
                    
                    // Get selector
                    let cssSelector = '';
                    if (node.id) {{
                        cssSelector = '#' + node.id;
                    }} else if (node.className && typeof node.className === 'string') {{
                        const classes = node.className.split(' ').filter(c => c).slice(0, 2);
                        if (classes.length > 0) {{
                            cssSelector = '.' + classes.join('.');
                        }}
                    }}
                    
                    if (!cssSelector) {{
                        cssSelector = node.tagName.toLowerCase();
                    }}
                    
                    // Get text content (truncated)
                    const text = node.textContent || node.value || '';
                    const textContent = text.trim().substring(0, 100);
                    
                    elements.push({{
                        selector: cssSelector,
                        tag: node.tagName.toLowerCase(),
                        text: textContent,
                        type: node.type || node.tagName.toLowerCase(),
                        visible: true
                    }});
                }}
                if (elements.length >= {max_elements}) break;
            }}
            
            return elements.slice(0, {max_elements});
        }}
    """)
    
    return elements


def compute_observation_hash(observation: Dict[str, Any]) -> str:
    """
    Compute a hash of the observation for tracking.
    
    Args:
        observation: Observation dictionary
        
    Returns:
        Hash string
    """
    import hashlib
    import json
    
    # Create a stable representation
    stable_obs = {
        "url": observation.get("url"),
        "title": observation.get("title"),
        "dom_elements": len(observation.get("dom_summary", []))
    }
    
    obs_str = json.dumps(stable_obs, sort_keys=True)
    return hashlib.md5(obs_str.encode()).hexdigest()

