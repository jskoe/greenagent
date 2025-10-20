import asyncio
from typing import Optional, Tuple
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import time


class BrowserManager:
    """Manages Playwright browser instances and contexts for isolated task execution."""
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self._active_contexts = set()
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()
    
    async def start(self):
        """Initialize Playwright and launch browser."""
        if self.playwright is None:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
    
    async def stop(self):
        """Clean up all contexts and close browser."""
        # Close all active contexts
        for context in list(self._active_contexts):
            try:
                await context.close()
            except Exception:
                pass
        self._active_contexts.clear()
        
        # Close browser
        if self.browser:
            await self.browser.close()
            self.browser = None
        
        # Stop playwright
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
    
    async def create_context(self) -> BrowserContext:
        """Create a new isolated browser context."""
        if not self.browser:
            await self.start()
        
        context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # Track active contexts
        self._active_contexts.add(context)
        
        return context
    
    async def close_context(self, context: BrowserContext):
        """Close a browser context and remove from tracking."""
        try:
            await context.close()
        except Exception:
            pass
        finally:
            self._active_contexts.discard(context)
    
    async def capture_state(self, page: Page) -> Tuple[str, str, bytes]:
        """
        Capture the current state of a page.
        
        Returns:
            Tuple of (page_content, current_url, screenshot_bytes)
        """
        # Get page content
        content = await page.content()
        
        # Get current URL
        url = page.url
        
        # Take screenshot
        screenshot_bytes = await page.screenshot(full_page=True)
        
        return content, url, screenshot_bytes
    
    async def navigate_to_url(self, context: BrowserContext, url: str, timeout: int = 30000) -> Page:
        """
        Navigate to a URL and return the page.
        
        Args:
            context: Browser context to use
            url: URL to navigate to
            timeout: Navigation timeout in milliseconds
            
        Returns:
            Page object after navigation
        """
        page = await context.new_page()
        
        # Set navigation timeout
        page.set_default_timeout(timeout)
        
        # Navigate to URL
        await page.goto(url, wait_until='domcontentloaded')
        
        return page
    
    def get_active_context_count(self) -> int:
        """Get the number of currently active contexts."""
        return len(self._active_contexts)


# Global browser manager instance
_browser_manager: Optional[BrowserManager] = None


async def get_browser_manager() -> BrowserManager:
    """Get the global browser manager instance."""
    global _browser_manager
    if _browser_manager is None:
        _browser_manager = BrowserManager()
        await _browser_manager.start()
    return _browser_manager


async def cleanup_browser_manager():
    """Clean up the global browser manager."""
    global _browser_manager
    if _browser_manager is not None:
        await _browser_manager.stop()
        _browser_manager = None
