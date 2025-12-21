"""
Model Builder

Automatically builds AppModel from observed events and correlations.
"""

from typing import Dict, List, Optional, Set, Any
from datetime import datetime
from framework.model.app_model import (
    AppModel,
    AppModelMeta,
    Screen,
    Element,
    ElementType,
    Action,
    ActionType,
    APICall,
    Selector,
    Platform,
    Flow,
    StateMachine,
    StateTransition
)
from framework.correlation import CorrelationResult, EventCorrelator
from framework.storage.event_store import EventStore


class ModelBuilder:
    """
    Builds AppModel from observed events
    
    Takes events and correlations and generates a structured AppModel
    that can be used for test generation.
    """
    
    def __init__(self, event_store: Optional[EventStore] = None):
        """
        Initialize model builder
        
        Args:
            event_store: Optional EventStore for loading events
        """
        self.event_store = event_store
    
    def build_from_session(
        self,
        session_id: str,
        app_version: str,
        platform: Platform = Platform.ANDROID,
        correlation_result: Optional[CorrelationResult] = None
    ) -> AppModel:
        """
        Build AppModel from a recorded session
        
        Args:
            session_id: Session ID to build from
            app_version: Application version
            platform: Target platform
            correlation_result: Pre-computed correlations (optional)
        
        Returns:
            Complete AppModel
        """
        if not self.event_store:
            raise ValueError("EventStore required for session-based model building")
        
        # Get session info
        sessions = self.event_store.get_sessions()
        session = next((s for s in sessions if s.get('session_id') == session_id), None)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        # Get correlations if not provided
        if not correlation_result:
            correlator = EventCorrelator(event_store=self.event_store)
            correlation_result = correlator.correlate_session(session_id)
        
        # Load events
        ui_events = self.event_store.get_events(
            session_id=session_id,
            event_type='UIEvent',
            limit=10000
        )
        api_events = self.event_store.get_events(
            session_id=session_id,
            event_type='NetworkEvent',
            limit=10000
        )
        nav_events = self.event_store.get_events(
            session_id=session_id,
            event_type='NavigationEvent',
            limit=10000
        )
        
        # Convert to dicts
        ui_dicts = [self._event_to_dict(e) for e in ui_events]
        api_dicts = [self._event_to_dict(e) for e in api_events]
        nav_dicts = [self._event_to_dict(e) for e in nav_events]
        
        return self.build_from_events(
            app_version=app_version,
            platform=platform,
            session_id=session_id,
            ui_events=ui_dicts,
            api_events=api_dicts,
            nav_events=nav_dicts,
            correlation_result=correlation_result
        )
    
    def build_from_events(
        self,
        app_version: str,
        platform: Platform,
        session_id: str,
        ui_events: List[Dict[str, Any]],
        api_events: List[Dict[str, Any]],
        nav_events: List[Dict[str, Any]],
        correlation_result: Optional[CorrelationResult] = None
    ) -> AppModel:
        """
        Build AppModel from event lists
        
        Args:
            app_version: Application version
            platform: Target platform
            session_id: Session identifier
            ui_events: UI event dicts
            api_events: API event dicts
            nav_events: Navigation event dicts
            correlation_result: Pre-computed correlations
        
        Returns:
            Complete AppModel
        """
        # Create metadata
        meta = AppModelMeta(
            app_version=app_version,
            platform=platform,
            recorded_at=datetime.now(),
            session_id=session_id
        )
        
        # Build screens
        screens = self._build_screens(nav_events, ui_events)
        
        # Build API calls
        api_calls = self._build_api_calls(api_events)
        
        # Build flows
        flows = []
        if correlation_result:
            flows = self._build_flows(correlation_result)
        
        # Build state machine
        state_machine = self._build_state_machine(nav_events, correlation_result)
        
        return AppModel(
            meta=meta,
            screens=screens,
            api_calls=api_calls,
            flows=flows,
            state_machine=state_machine
        )
    
    def _build_screens(
        self,
        nav_events: List[Dict[str, Any]],
        ui_events: List[Dict[str, Any]]
    ) -> Dict[str, Screen]:
        """
        Build Screen models from navigation and UI events
        
        Infers screens from navigation events and populates them with
        elements from UI events.
        """
        screens: Dict[str, Screen] = {}
        
        # Get unique screens from navigation events
        screen_names: Set[str] = set()
        for nav in nav_events:
            if 'toScreen' in nav:
                screen_names.add(nav['toScreen'])
            if 'fromScreen' in nav:
                screen_names.add(nav['fromScreen'])
        
        # Also get screens from UI events
        for ui in ui_events:
            if 'screen' in ui:
                screen_names.add(ui['screen'])
        
        # Build each screen
        for screen_name in screen_names:
            if screen_name and screen_name != 'unknown':
                # Get UI events for this screen
                screen_ui_events = [
                    ui for ui in ui_events
                    if ui.get('screen') == screen_name
                ]
                
                # Extract elements
                elements = self._extract_elements(screen_ui_events)
                
                # Extract actions
                actions = self._extract_actions(screen_ui_events)
                
                screen = Screen(
                    name=screen_name,
                    class_name=None,
                    elements=list(elements.values()),
                    actions=actions
                )
                
                screens[screen_name] = screen
        
        return screens
    
    def _extract_elements(
        self,
        ui_events: List[Dict[str, Any]]
    ) -> Dict[str, Element]:
        """
        Extract UI elements from UI events
        
        Each unique element that was interacted with becomes an Element.
        """
        elements: Dict[str, Element] = {}
        
        for event in ui_events:
            element_id = event.get('elementId')
            if not element_id:
                continue
            
            if element_id in elements:
                continue  # Already extracted
            
            # Infer element type from action
            action = event.get('action', 'tap')
            element_type = self._infer_element_type(action, event)
            
            # Build selector
            selector = self._build_selector(event)
            
            element = Element(
                id=element_id,
                type=element_type,
                selector=selector,
                text=event.get('text') or event.get('contentDescription'),
                visible_when=None
            )
            
            elements[element_id] = element
        
        return elements
    
    def _infer_element_type(
        self,
        action: str,
        event: Dict[str, Any]
    ) -> ElementType:
        """Infer element type from action and event data"""
        
        if action == 'input':
            return ElementType.INPUT  # Use INPUT instead of TEXT_INPUT
        elif action == 'swipe':
            return ElementType.LIST  # Swipeable elements are typically lists
        elif action == 'tap':
            text = event.get('text', '').lower()
            if 'button' in text or 'btn' in text:
                return ElementType.BUTTON
            else:
                return ElementType.BUTTON  # Default for taps
        else:
            return ElementType.GENERIC
    
    def _build_selector(self, event: Dict[str, Any]) -> Selector:
        """Build selector from event data"""
        
        element_id = event.get('elementId')
        text = event.get('text')
        content_desc = event.get('contentDescription')
        class_name = event.get('className')
        
        # Build platform-specific selectors
        android_selector = {}
        ios_selector = {}
        
        if element_id:
            # Assume element_id is a test tag
            android_selector['test_id'] = element_id
            ios_selector['accessibility_id'] = element_id
        
        if content_desc:
            android_selector['content_desc'] = content_desc
            ios_selector['accessibility_id'] = content_desc
        
        # Fallback to text
        if text and not android_selector:
            android_selector['text'] = text
            ios_selector['label'] = text
        
        # Very weak fallback - XPath by class
        if class_name and not android_selector:
            android_selector['xpath'] = f"//{class_name}"
            ios_selector['xpath'] = f"//{class_name}"
        
        # Build selector with fallbacks
        android_str = None
        ios_str = None
        test_id_str = None
        xpath_str = None
        android_fallbacks = []
        ios_fallbacks = []
        
        if element_id:
            test_id_str = element_id
            # Add fallbacks
            if 'text' in android_selector:
                android_fallbacks.append(android_selector['text'])
            if 'xpath' in android_selector:
                android_fallbacks.append(android_selector['xpath'])
        
        if 'resource_id' in android_selector:
            android_str = android_selector['resource_id']
        elif 'text' in android_selector:
            android_str = android_selector['text']
        elif 'xpath' in android_selector:
            android_str = android_selector['xpath']
        
        if 'accessibility_id' in ios_selector:
            ios_str = ios_selector['accessibility_id']
        elif 'label' in ios_selector:
            ios_str = ios_selector['label']
        elif 'xpath' in ios_selector:
            ios_str = ios_selector['xpath']
        
        if 'xpath' in android_selector and not test_id_str:
            xpath_str = android_selector['xpath']
        
        return Selector(
            android=android_str,
            ios=ios_str,
            test_id=test_id_str,
            xpath=xpath_str,
            android_fallback=android_fallbacks,
            ios_fallback=ios_fallbacks
        )
    
    def _extract_actions(
        self,
        ui_events: List[Dict[str, Any]]
    ) -> List[Action]:
        """
        Extract actions from UI events
        
        Groups events by element to create actions.
        """
        actions: List[Action] = []
        seen_actions: Set[str] = set()
        
        for event in ui_events:
            element_id = event.get('elementId')
            if not element_id:
                continue  # Skip events without element ID
            
            action_type_str = event.get('action', 'tap')
            
            # Map string to ActionType
            action_type = self._map_action_type(action_type_str)
            
            # Create unique key
            action_key = f"{element_id}_{action_type.value}"
            
            if action_key in seen_actions:
                continue
            
            seen_actions.add(action_key)
            
            action = Action(
                name=f"{action_type.value}_{element_id}",
                ui_action=action_type,
                element_id=element_id,
                api_call=None,
                validation=None
            )
            
            actions.append(action)
        
        return actions
    
    def _map_action_type(self, action_str: str) -> ActionType:
        """Map action string to ActionType enum"""
        mapping = {
            'tap': ActionType.TAP,
            'click': ActionType.TAP,
            'input': ActionType.INPUT,
            'swipe': ActionType.SWIPE,
            'scroll': ActionType.SWIPE,  # Map scroll to SWIPE
            'long_press': ActionType.LONG_PRESS,
            'navigate': ActionType.TAP  # Map navigate to TAP (navigation trigger)
        }
        return mapping.get(action_str.lower(), ActionType.TAP)
    
    def _build_api_calls(
        self,
        api_events: List[Dict[str, Any]]
    ) -> Dict[str, APICall]:
        """
        Build APICall models from network events
        
        Each unique endpoint becomes an APICall definition.
        """
        api_calls: Dict[str, APICall] = {}
        
        for event in api_events:
            method = event.get('method', 'GET')
            url = event.get('url', '')
            
            # Extract endpoint path
            endpoint = self._extract_endpoint(url)
            
            # Create unique key
            key = f"{method}_{endpoint}"
            
            if key in api_calls:
                continue  # Already processed
            
            # Extract request/response schemas (simplified)
            request_body = event.get('requestBody')
            response_body = event.get('responseBody')
            
            schema = {}
            if isinstance(request_body, dict):
                schema['request'] = request_body
            if isinstance(response_body, dict):
                schema['response'] = response_body
            
            api_call = APICall(
                name=key,
                method=method.upper(),
                endpoint=endpoint,
                schema=schema,
                triggers_state_change=None
            )
            
            api_calls[key] = api_call
        
        return api_calls
    
    def _extract_endpoint(self, url: str) -> str:
        """Extract endpoint path from full URL"""
        if not url:
            return "/"
        
        # Remove protocol and domain
        if '://' in url:
            url = url.split('://', 1)[1]
        
        if '/' in url:
            path = '/' + '/'.join(url.split('/')[1:])
        else:
            path = '/'
        
        # Remove query parameters
        if '?' in path:
            path = path.split('?')[0]
        
        return path
    
    def _build_flows(
        self,
        correlation_result: CorrelationResult
    ) -> List[Flow]:
        """
        Build Flow models from correlation results
        
        Each full flow correlation becomes a Flow.
        """
        flows: List[Flow] = []
        
        for full_flow in correlation_result.full_flows:
            steps = []
            
            # Add UI step
            ui_corr = full_flow.ui_correlation
            steps.append({
                'type': 'ui_action',
                'screen': ui_corr.ui_screen,
                'action': ui_corr.ui_event_type,
                'element': ui_corr.ui_element_id
            })
            
            # Add API steps
            for api_call in ui_corr.api_calls:
                steps.append({
                    'type': 'api_call',
                    'method': api_call.get('method'),
                    'endpoint': api_call.get('endpoint')
                })
            
            # Add navigation steps
            for nav_corr in full_flow.api_navigation_correlations:
                steps.append({
                    'type': 'navigation',
                    'from': nav_corr.from_screen,
                    'to': nav_corr.to_screen,
                    'condition': nav_corr.condition
                })
            
            flow = Flow(
                name=full_flow.flow_name or full_flow.flow_id,
                description=full_flow.description,
                steps=steps
            )
            
            flows.append(flow)
        
        return flows
    
    def _build_state_machine(
        self,
        nav_events: List[Dict[str, Any]],
        correlation_result: Optional[CorrelationResult]
    ) -> Optional[StateMachine]:
        """
        Build state machine from navigation events
        
        Creates states for each screen and transitions between them.
        """
        states: List[str] = []
        transitions: List[StateTransition] = []
        
        # Get unique screens
        screen_names: Set[str] = set()
        for nav in nav_events:
            if 'toScreen' in nav:
                screen_names.add(nav['toScreen'])
            if 'fromScreen' in nav:
                screen_names.add(nav['fromScreen'])
        
        # Create states (just list of state names)
        for screen in screen_names:
            if screen and screen != 'unknown':
                states.append(screen)
        
        # Create transitions
        seen_transitions: Set[str] = set()
        
        for nav in nav_events:
            from_screen = nav.get('fromScreen')
            to_screen = nav.get('toScreen')
            
            if not from_screen or not to_screen:
                continue
            
            trans_key = f"{from_screen}_to_{to_screen}"
            if trans_key in seen_transitions:
                continue
            
            seen_transitions.add(trans_key)
            
            # Try to find trigger from correlations
            trigger = None
            if correlation_result:
                for nav_corr in correlation_result.api_to_navigation:
                    if (nav_corr.from_screen == from_screen and
                        nav_corr.to_screen == to_screen):
                        trigger = f"api_{nav_corr.api_method}_{nav_corr.api_endpoint}"
                        break
            
            transition = StateTransition(
                from_state=from_screen,
                to_state=to_screen,
                trigger=trigger or 'user_action',
                condition=None
            )
            
            transitions.append(transition)
        
        # Determine initial state (first screen visited)
        initial_state = None
        if nav_events:
            first_nav = nav_events[0]
            initial_state = first_nav.get('toScreen') or first_nav.get('fromScreen')
        
        if not states:
            return None
        
        return StateMachine(
            states=states,
            transitions=transitions,
            initial_state=initial_state
        )
    
    def _event_to_dict(self, event: Any) -> Dict[str, Any]:
        """Convert event object to dict"""
        if isinstance(event, dict):
            return event
        
        if hasattr(event, 'keys'):
            return {key: event[key] for key in event.keys()}
        
        if hasattr(event, 'model_dump'):
            return event.model_dump()
        
        return {}

