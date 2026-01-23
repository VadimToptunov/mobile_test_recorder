"""
Appium Backend Adapter

Supports:
- Appium v1.x (deprecated)
- Appium v2.x (recommended)
- Plugins: images, relaxed-caps, etc.
"""

from typing import Dict, Any, Optional
import subprocess
import time

from appium import webdriver
from appium.options.common import AppiumOptions

from framework.backends import MobileAutomationBackend, BackendCapability


class AppiumBackend(MobileAutomationBackend):
    """Appium backend implementation."""
    
    def __init__(self, server_url: str = "http://localhost:4723"):
        self.server_url = server_url
        self.sessions: Dict[str, webdriver.Remote] = {}
    
    def get_capabilities(self) -> BackendCapability:
        return BackendCapability(
            name="appium",
            supports_ios=True,
            supports_android=True,
            supports_web=True,
            supports_ui_tree=True,
            supports_screenshot=True,
            supports_tap=True,
            supports_swipe=True,
            supports_type=True,
            supports_gestures=True,
            requires_app_modification=False,
            execution_speed="medium"
        )
    
    def start_session(self, device_id: str, app_path: Optional[str] = None,
                     capabilities: Optional[Dict[str, Any]] = None) -> str:
        """Start Appium session."""
        caps = capabilities or {}
        
        # Auto-detect platform
        if "emulator" in device_id or device_id.startswith("emulator-"):
            platform = "Android"
            automation_name = "UiAutomator2"
        else:
            platform = "iOS"
            automation_name = "XCUITest"
        
        # Build capabilities
        options = AppiumOptions()
        options.platform_name = caps.get("platformName", platform)
        options.automation_name = caps.get("automationName", automation_name)
        options.device_name = device_id
        options.udid = device_id
        
        if app_path:
            options.app = app_path
        
        # Optional capabilities
        if "noReset" in caps:
            options.no_reset = caps["noReset"]
        if "fullReset" in caps:
            options.full_reset = caps["fullReset"]
        
        # Start driver
        driver = webdriver.Remote(
            command_executor=self.server_url,
            options=options
        )
        
        session_id = driver.session_id
        self.sessions[session_id] = driver
        
        return session_id
    
    def stop_session(self, session_id: str) -> None:
        """Stop Appium session."""
        if session_id in self.sessions:
            driver = self.sessions[session_id]
            driver.quit()
            del self.sessions[session_id]
    
    def get_screenshot(self, session_id: str) -> bytes:
        """Capture screenshot."""
        driver = self.sessions.get(session_id)
        if not driver:
            raise ValueError(f"Session not found: {session_id}")
        
        return driver.get_screenshot_as_png()
    
    def get_ui_tree(self, session_id: str) -> str:
        """Get page source (XML)."""
        driver = self.sessions.get(session_id)
        if not driver:
            raise ValueError(f"Session not found: {session_id}")
        
        return driver.page_source
    
    def tap(self, session_id: str, x: int, y: int) -> None:
        """Tap at coordinates."""
        driver = self.sessions.get(session_id)
        if not driver:
            raise ValueError(f"Session not found: {session_id}")
        
        from appium.webdriver.common.touch_action import TouchAction
        action = TouchAction(driver)
        action.tap(x=x, y=y).perform()
    
    def swipe(self, session_id: str, start_x: int, start_y: int,
              end_x: int, end_y: int, duration_ms: int = 300) -> None:
        """Swipe gesture."""
        driver = self.sessions.get(session_id)
        if not driver:
            raise ValueError(f"Session not found: {session_id}")
        
        driver.swipe(start_x, start_y, end_x, end_y, duration_ms)
    
    def type_text(self, session_id: str, text: str, element_id: Optional[str] = None) -> None:
        """Type text."""
        driver = self.sessions.get(session_id)
        if not driver:
            raise ValueError(f"Session not found: {session_id}")
        
        if element_id:
            element = driver.find_element_by_id(element_id)
            element.send_keys(text)
        else:
            # Type into active element
            driver.execute_script("mobile: type", {"text": text})
    
    def find_element(self, session_id: str, strategy: str, value: str) -> Optional[str]:
        """Find element."""
        driver = self.sessions.get(session_id)
        if not driver:
            raise ValueError(f"Session not found: {session_id}")
        
        from selenium.common.exceptions import NoSuchElementException
        
        try:
            if strategy == "id":
                element = driver.find_element_by_id(value)
            elif strategy == "xpath":
                element = driver.find_element_by_xpath(value)
            elif strategy == "accessibility_id":
                element = driver.find_element_by_accessibility_id(value)
            elif strategy == "class_name":
                element = driver.find_element_by_class_name(value)
            else:
                return None
            
            return element.id
        except NoSuchElementException:
            return None
    
    def get_element_bounds(self, session_id: str, element_id: str) -> Dict[str, int]:
        """Get element bounds."""
        driver = self.sessions.get(session_id)
        if not driver:
            raise ValueError(f"Session not found: {session_id}")
        
        element = driver.find_element_by_id(element_id)
        location = element.location
        size = element.size
        
        return {
            "x": location["x"],
            "y": location["y"],
            "width": size["width"],
            "height": size["height"]
        }


# Register with factory
from framework.backends import BackendFactory
BackendFactory.register("appium", AppiumBackend)
