"""
Selector Builder

Builds optimal selectors from element attributes.
"""

from typing import Dict, List, Optional
from framework.model.app_model import Selector, Platform
from framework.selectors.selector_scorer import SelectorScorer


class SelectorBuilder:
    """
    Builds intelligent selectors from element data
    
    Creates cross-platform selectors with fallback chains.
    """
    
    def __init__(self):
        self.scorer = SelectorScorer()
    
    def build_selector(
        self,
        element_id: str,
        attributes: Dict[str, str],
        platform: Platform = Platform.ANDROID
    ) -> Selector:
        """
        Build optimal selector from element attributes
        
        Args:
            element_id: Element identifier
            attributes: Available attributes (test_tag, resource_id, text, etc.)
            platform: Target platform
        
        Returns:
            Selector with primary strategy and fallbacks
        """
        # Build platform-specific selectors
        android_selector = self._build_platform_selector(attributes, "android")
        ios_selector = self._build_platform_selector(attributes, "ios")
        
        # Determine primary strategy
        primary_strategy = self._determine_primary_strategy(attributes)
        
        # Build fallback chain
        fallback_strategies = self._build_fallback_chain(attributes, primary_strategy)
        
        # Calculate stability
        primary_selector = android_selector if platform == Platform.ANDROID else ios_selector
        stability_score = self.scorer.score_selector(primary_selector or {})
        stability = self.scorer.get_stability_level(stability_score)
        
        return Selector(
            id=element_id,
            android=android_selector,
            ios=ios_selector,
            primary_strategy=primary_strategy,
            fallback_strategies=fallback_strategies,
            stability=stability.value,
            stability_score=stability_score
        )
    
    def _build_platform_selector(
        self,
        attributes: Dict[str, str],
        platform: str
    ) -> Optional[Dict[str, str]]:
        """Build selector for specific platform"""
        
        if platform == "android":
            return self._build_android_selector(attributes)
        elif platform == "ios":
            return self._build_ios_selector(attributes)
        
        return None
    
    def _build_android_selector(self, attributes: Dict[str, str]) -> Optional[Dict[str, str]]:
        """Build Android-specific selector"""
        
        # Priority order for Android
        if 'test_tag' in attributes and attributes['test_tag']:
            return {'test_id': attributes['test_tag']}
        
        if 'resource_id' in attributes and attributes['resource_id']:
            return {'resource_id': attributes['resource_id']}
        
        if 'content_desc' in attributes and attributes['content_desc']:
            return {'content_desc': attributes['content_desc']}
        
        if 'text' in attributes and attributes['text']:
            return {'text': attributes['text']}
        
        # Fallback to XPath if we have class name
        if 'class_name' in attributes and attributes['class_name']:
            return {'xpath': f"//{attributes['class_name']}"}
        
        return None
    
    def _build_ios_selector(self, attributes: Dict[str, str]) -> Optional[Dict[str, str]]:
        """Build iOS-specific selector"""
        
        # Priority order for iOS
        if 'accessibility_id' in attributes and attributes['accessibility_id']:
            return {'accessibility_id': attributes['accessibility_id']}
        
        if 'test_tag' in attributes and attributes['test_tag']:
            return {'accessibility_id': attributes['test_tag']}
        
        if 'text' in attributes and attributes['text']:
            return {'label': attributes['text']}
        
        if 'class_name' in attributes and attributes['class_name']:
            return {'xpath': f"//{attributes['class_name']}"}
        
        return None
    
    def _determine_primary_strategy(self, attributes: Dict[str, str]) -> str:
        """Determine the primary locator strategy"""
        
        # Score all available strategies
        strategies = []
        
        if 'test_tag' in attributes and attributes['test_tag']:
            strategies.append(('test_id', 1.0))
        
        if 'accessibility_id' in attributes and attributes['accessibility_id']:
            strategies.append(('accessibility_id', 0.95))
        
        if 'resource_id' in attributes and attributes['resource_id']:
            strategies.append(('resource_id', 0.90))
        
        if 'content_desc' in attributes and attributes['content_desc']:
            strategies.append(('content_desc', 0.75))
        
        if 'text' in attributes and attributes['text']:
            strategies.append(('text', 0.60))
        
        if 'class_name' in attributes and attributes['class_name']:
            strategies.append(('xpath', 0.30))
        
        if not strategies:
            return 'xpath'
        
        # Return strategy with highest score
        strategies.sort(key=lambda x: x[1], reverse=True)
        return strategies[0][0]
    
    def _build_fallback_chain(
        self,
        attributes: Dict[str, str],
        primary_strategy: str
    ) -> List[str]:
        """Build fallback strategy chain"""
        
        # All possible strategies in priority order
        all_strategies = [
            'test_id',
            'accessibility_id',
            'resource_id',
            'content_desc',
            'text',
            'xpath'
        ]
        
        # Available strategies based on attributes
        available = []
        
        if 'test_tag' in attributes and attributes['test_tag']:
            available.append('test_id')
        
        if 'accessibility_id' in attributes and attributes['accessibility_id']:
            available.append('accessibility_id')
        
        if 'resource_id' in attributes and attributes['resource_id']:
            available.append('resource_id')
        
        if 'content_desc' in attributes and attributes['content_desc']:
            available.append('content_desc')
        
        if 'text' in attributes and attributes['text']:
            available.append('text')
        
        # XPath always available as last resort
        available.append('xpath')
        
        # Remove primary strategy and return rest
        fallbacks = [s for s in available if s != primary_strategy]
        
        return fallbacks[:3]  # Limit to 3 fallbacks

