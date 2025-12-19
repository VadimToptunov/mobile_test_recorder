"""
App Model - Core data structures for representing mobile application behavior

This module defines the semantic model of a mobile application including:
- Screens and UI elements
- Actions and transitions
- API calls and correlations
- State machine
- Navigation flows
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class Platform(str, Enum):
    """Supported platforms"""
    ANDROID = "android"
    IOS = "ios"
    CROSS_PLATFORM = "cross-platform"


class ActionType(str, Enum):
    """Types of UI actions"""
    TAP = "tap"
    SWIPE = "swipe"
    INPUT = "input"
    LONG_PRESS = "long_press"
    DOUBLE_TAP = "double_tap"


class ElementType(str, Enum):
    """Types of UI elements"""
    BUTTON = "button"
    INPUT = "input"
    TEXT = "text"
    LIST = "list"
    IMAGE = "image"
    CHECKBOX = "checkbox"
    SWITCH = "switch"
    RADIO = "radio"
    WEBVIEW = "webview"
    GENERIC = "generic"


class TestPriority(str, Enum):
    """Element testing priority"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    IGNORE = "ignore"


class SelectorStability(str, Enum):
    """Selector stability assessment"""
    HIGH = "high"    # accessibility ID, resource ID
    MEDIUM = "medium"  # text-based
    LOW = "low"      # XPath with index
    UNKNOWN = "unknown"


# ============================================================================
# Core Models
# ============================================================================

class Selector(BaseModel):
    """
    Cross-platform element selector with fallback strategies
    
    Supports multiple locator strategies:
    - android: Android-specific locator
    - ios: iOS-specific locator
    - test_id: Universal test identifier
    - xpath: XPath locator (fragile)
    """
    android: Optional[str] = None
    ios: Optional[str] = None
    test_id: Optional[str] = None
    xpath: Optional[str] = None
    android_fallback: List[str] = Field(default_factory=list)
    ios_fallback: List[str] = Field(default_factory=list)
    stability: SelectorStability = SelectorStability.UNKNOWN
    
    @field_validator('android', 'ios', 'test_id', 'xpath')
    @classmethod
    def validate_locators(cls, v):
        """At least one locator must be provided"""
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "android": "id:com.app:id/login_button",
                "ios": "accessibility:login_button",
                "test_id": "login_button",
                "stability": "high"
            }
        }
    }


class Element(BaseModel):
    """
    UI Element representation
    
    Represents a single interactive or visible element on screen
    """
    id: str = Field(..., description="Unique element identifier")
    type: ElementType = Field(..., description="Element type")
    selector: Selector = Field(..., description="Element selector")
    text: Optional[str] = Field(None, description="Visible text content")
    capabilities: List[str] = Field(
        default_factory=list,
        description="Element capabilities (tappable, input, scrollable, etc.)"
    )
    test_priority: TestPriority = TestPriority.MEDIUM
    visible_when: Optional[List[str]] = Field(
        None,
        description="Conditions when element is visible"
    )
    description: Optional[str] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "login_button",
                "type": "button",
                "selector": {
                    "android": "id:login_btn",
                    "ios": "accessibility:login_btn"
                },
                "capabilities": ["tappable"],
                "test_priority": "high"
            }
        }
    }


class Action(BaseModel):
    """
    User action on an element
    
    Represents a recorded or possible action that triggers state changes
    """
    name: str = Field(..., description="Action name")
    ui_action: ActionType = Field(..., description="Type of UI interaction")
    element_id: str = Field(..., description="Target element ID")
    api_call: Optional[str] = Field(None, description="Triggered API call")
    transitions: Dict[str, str] = Field(
        default_factory=dict,
        description="State transitions (success/failure/cancel)"
    )
    validation: Optional[str] = Field(
        None,
        description="Validation rule for this action"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "perform_login",
                "ui_action": "tap",
                "element_id": "login_button",
                "api_call": "auth_login",
                "transitions": {
                    "success": "HomeScreen",
                    "failure": "LoginErrorScreen"
                }
            }
        }
    }


class APICall(BaseModel):
    """
    API endpoint representation
    
    Captured from network observations or static analysis
    """
    name: str = Field(..., description="API call identifier")
    endpoint: str = Field(..., description="API endpoint path")
    method: str = Field(..., description="HTTP method")
    schema: Dict[str, Any] = Field(
        default_factory=dict,
        description="Request/Response schema"
    )
    responses: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Observed responses"
    )
    triggers_state_change: Optional[str] = Field(
        None,
        description="State machine event this API triggers"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "auth_login",
                "endpoint": "/api/v1/auth/login",
                "method": "POST",
                "schema": {
                    "username": "string",
                    "password": "string"
                },
                "triggers_state_change": "login_success"
            }
        }
    }


class Precondition(BaseModel):
    """
    Condition that must be satisfied to reach a screen
    """
    state: Optional[str] = None
    feature_flag: Optional[str] = None
    api_condition: Optional[str] = None


class Screen(BaseModel):
    """
    Screen (Activity/ViewController) representation
    
    Represents a logical UI state with elements and possible actions
    """
    name: str = Field(..., description="Screen identifier")
    class_name: Optional[str] = Field(
        None,
        description="Activity/ViewController class name"
    )
    preconditions: List[Precondition] = Field(
        default_factory=list,
        description="Conditions to reach this screen"
    )
    elements: List[Element] = Field(
        default_factory=list,
        description="UI elements on this screen"
    )
    actions: List[Action] = Field(
        default_factory=list,
        description="Possible actions on this screen"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "LoginScreen",
                "class_name": "com.app.ui.LoginActivity",
                "elements": [
                    {
                        "id": "username_field",
                        "type": "input",
                        "selector": {"android": "id:username"}
                    }
                ],
                "actions": [
                    {
                        "name": "login",
                        "ui_action": "tap",
                        "element_id": "login_button"
                    }
                ]
            }
        }
    }


class StateTransition(BaseModel):
    """
    State machine transition
    """
    from_state: str
    to_state: str
    trigger: str
    condition: Optional[str] = None


class StateMachine(BaseModel):
    """
    Application state machine
    
    Models high-level application states and transitions
    """
    states: List[str] = Field(default_factory=list)
    transitions: List[StateTransition] = Field(default_factory=list)
    initial_state: Optional[str] = None


class Flow(BaseModel):
    """
    Navigation flow (sequence of screens and actions)
    """
    name: str
    description: Optional[str] = None
    steps: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Sequence of screen/action pairs"
    )


class AppModelMeta(BaseModel):
    """
    Metadata about the app model
    """
    schema_version: str = Field(default="1.0.0", pattern=r"^\d+\.\d+\.\d+$")
    app_version: str
    platform: Platform
    recorded_at: datetime = Field(default_factory=datetime.now)
    session_id: Optional[str] = None


class AppModel(BaseModel):
    """
    Complete application model
    
    This is the central data structure that represents everything
    we know about the mobile application's behavior
    """
    meta: AppModelMeta
    screens: Dict[str, Screen] = Field(default_factory=dict)
    api_calls: Dict[str, APICall] = Field(default_factory=dict)
    state_machine: Optional[StateMachine] = None
    flows: List[Flow] = Field(default_factory=list)
    
    def validate_consistency(self) -> List[str]:
        """
        Validate model consistency
        
        Returns list of validation errors
        """
        errors = []
        
        # Check that all referenced screens exist
        for screen_name, screen in self.screens.items():
            for action in screen.actions:
                for target_screen in action.transitions.values():
                    if target_screen not in self.screens:
                        errors.append(
                            f"Screen '{screen_name}': "
                            f"references non-existent screen '{target_screen}'"
                        )
                
                # Check that referenced API calls exist
                if action.api_call and action.api_call not in self.api_calls:
                    errors.append(
                        f"Screen '{screen_name}': "
                        f"references non-existent API '{action.api_call}'"
                    )
        
        return errors
    
    def get_screen(self, name: str) -> Optional[Screen]:
        """Get screen by name"""
        return self.screens.get(name)
    
    def get_api_call(self, name: str) -> Optional[APICall]:
        """Get API call by name"""
        return self.api_calls.get(name)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "meta": {
                    "schema_version": "1.0.0",
                    "app_version": "1.2.3",
                    "platform": "android",
                    "recorded_at": "2025-12-19T10:00:00Z"
                },
                "screens": {
                    "LoginScreen": {
                        "name": "LoginScreen",
                        "elements": [],
                        "actions": []
                    }
                },
                "api_calls": {},
                "flows": []
            }
        }
    }

