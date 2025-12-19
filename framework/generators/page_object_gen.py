"""
Page Object Generator

Generates Page Object classes from App Model screens.
"""

from typing import List
from pathlib import Path
from jinja2 import Template

from framework.model.app_model import Screen, Element, Action


PAGE_OBJECT_TEMPLATE = """
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class {{ class_name }}:
    \"\"\"
    Page Object for {{ screen.name }} screen
    
    Generated from App Model
    \"\"\"
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    
    # Selectors
{% for element in screen.elements %}
    {{ element.id | upper }}_SELECTOR = {
        "android": {{ element.selector.android | tojson }},
        "ios": {{ element.selector.ios | tojson }}
    }
{% endfor %}
    
    def _get_selector(self, selector_dict: dict) -> tuple:
        \"\"\"Get platform-specific selector\"\"\"
        platform = self.driver.capabilities.get('platformName', '').lower()
        
        if platform == 'android':
            selector = selector_dict['android']
        elif platform == 'ios':
            selector = selector_dict['ios']
        else:
            raise ValueError(f"Unsupported platform: {platform}")
        
        # Determine locator strategy
        if selector.startswith('//'):
            return (AppiumBy.XPATH, selector)
        elif selector.startswith('~'):
            return (AppiumBy.ACCESSIBILITY_ID, selector[1:])
        else:
            return (AppiumBy.ID, selector)
    
{% for element in screen.elements %}
    def get_{{ element.id }}(self):
        \"\"\"Get {{ element.id }} element\"\"\"
        by, value = self._get_selector(self.{{ element.id | upper }}_SELECTOR)
        return self.wait.until(EC.presence_of_element_located((by, value)))
    
{% endfor %}

    # Actions
{% for action in screen.actions %}
    def {{ action.name }}(self{% for param in action.parameters %}, {{ param.name }}: {{ param.type }}{% endfor %}):
        \"\"\"{{ action.description or action.name }}\"\"\"
{% if action.target_element %}
        element = self.get_{{ action.target_element }}()
{% endif %}
{% if action.action_type == 'tap' %}
        element.click()
{% elif action.action_type == 'input' %}
        element.clear()
        element.send_keys({{ action.parameters[0].name if action.parameters else 'text' }})
{% elif action.action_type == 'swipe' %}
        # Swipe action
        self.driver.swipe(start_x=element.location['x'], 
                         start_y=element.location['y'],
                         end_x=element.location['x'] + 200,
                         end_y=element.location['y'],
                         duration=500)
{% else %}
        # {{ action.action_type }} action
        element.click()
{% endif %}
{% if action.triggers_api %}
        # API call: {{ action.triggers_api }}
{% endif %}
{% if action.wait_for %}
        # Wait for: {{ action.wait_for }}
        import time
        time.sleep(1)
{% endif %}
        
{% endfor %}

    def is_displayed(self) -> bool:
        \"\"\"Check if screen is currently displayed\"\"\"
        try:
{% if screen.elements %}
            self.get_{{ screen.elements[0].id }}()
            return True
{% else %}
            return True
{% endif %}
        except Exception:
            return False
    
    def wait_until_displayed(self, timeout: int = 10):
        \"\"\"Wait until screen is displayed\"\"\"
        from selenium.common.exceptions import TimeoutException
        import time
        
        end_time = time.time() + timeout
        while time.time() < end_time:
            if self.is_displayed():
                return True
            time.sleep(0.5)
        
        raise TimeoutException(f"{{ screen.name }} screen not displayed after {timeout}s")
"""


def generate_page_object(screen: Screen, output_dir: Path) -> Path:
    """
    Generate Page Object class for screen
    
    Args:
        screen: Screen model
        output_dir: Output directory for generated file
    
    Returns:
        Path to generated file
    """
    # Create class name
    class_name = f"{screen.name.replace('Screen', '').replace(' ', '')}Page"
    
    # Render template
    template = Template(PAGE_OBJECT_TEMPLATE)
    content = template.render(
        screen=screen,
        class_name=class_name
    )
    
    # Write to file
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / f"{class_name.lower()}.py"
    file_path.write_text(content)
    
    return file_path


def generate_all_page_objects(screens: List[Screen], output_dir: Path) -> List[Path]:
    """
    Generate Page Objects for all screens
    
    Args:
        screens: List of screen models
        output_dir: Output directory
    
    Returns:
        List of generated file paths
    """
    generated_files = []
    
    for screen in screens:
        file_path = generate_page_object(screen, output_dir)
        generated_files.append(file_path)
    
    # Generate __init__.py
    init_content = "# Generated Page Objects\n\n"
    for screen in screens:
        class_name = f"{screen.name.replace('Screen', '').replace(' ', '')}Page"
        init_content += f"from .{class_name.lower()} import {class_name}\n"
    
    init_content += "\n__all__ = [\n"
    for screen in screens:
        class_name = f"{screen.name.replace('Screen', '').replace(' ', '')}Page"
        init_content += f"    '{class_name}',\n"
    init_content += "]\n"
    
    init_path = output_dir / "__init__.py"
    init_path.write_text(init_content)
    generated_files.append(init_path)
    
    return generated_files

