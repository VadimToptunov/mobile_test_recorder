"""
Selector Optimizer

Optimizes and improves existing selectors.
"""

from typing import Dict, List, Optional
from framework.model.app_model import Selector
from framework.selectors.selector_scorer import SelectorScorer, SelectorStability


class SelectorOptimizer:
    """
    Optimizes selectors for better stability and performance
    
    Analyzes existing selectors and suggests improvements.
    """
    
    def __init__(self):
        self.scorer = SelectorScorer()
    
    def optimize_selector(self, selector: Selector) -> Selector:
        """
        Optimize a selector
        
        Args:
            selector: Selector to optimize
        
        Returns:
            Optimized selector
        """
        # Score current selector
        android_score = self.scorer.score_selector(selector.android or {})
        ios_score = self.scorer.score_selector(selector.ios or {})
        
        # Update stability if not set
        if not selector.stability_score:
            selector.stability_score = max(android_score, ios_score)
            selector.stability = self.scorer.get_stability_level(
                selector.stability_score
            ).value
        
        # Optimize XPath if present and poor
        if selector.android and 'xpath' in selector.android:
            if android_score < 0.5:
                selector.android = self._optimize_xpath(selector.android)
        
        if selector.ios and 'xpath' in selector.ios:
            if ios_score < 0.5:
                selector.ios = self._optimize_xpath(selector.ios)
        
        return selector
    
    def _optimize_xpath(self, selector: Dict[str, str]) -> Dict[str, str]:
        """Optimize XPath expression"""
        xpath = selector.get('xpath', '')
        
        if not xpath:
            return selector
        
        # Try to simplify XPath
        optimized_xpath = xpath
        
        # Remove leading // if followed by specific path
        if xpath.startswith('//') and xpath.count('/') > 3:
            # Keep just the last 2 levels
            parts = xpath.split('/')
            if len(parts) > 3:
                optimized_xpath = '//' + '/'.join(parts[-2:])
        
        # Remove index if it's [1] (first element, default)
        optimized_xpath = optimized_xpath.replace('[1]', '')
        
        return {'xpath': optimized_xpath}
    
    def analyze_selectors(
        self,
        selectors: List[Selector]
    ) -> Dict[str, any]:
        """
        Analyze a collection of selectors
        
        Args:
            selectors: List of selectors to analyze
        
        Returns:
            Analysis report with statistics and recommendations
        """
        total = len(selectors)
        
        if total == 0:
            return {
                'total': 0,
                'statistics': {},
                'recommendations': []
            }
        
        # Count by stability
        excellent = sum(1 for s in selectors if s.stability == SelectorStability.EXCELLENT.value)
        good = sum(1 for s in selectors if s.stability == SelectorStability.GOOD.value)
        fair = sum(1 for s in selectors if s.stability == SelectorStability.FAIR.value)
        poor = sum(1 for s in selectors if s.stability == SelectorStability.POOR.value)
        fragile = sum(1 for s in selectors if s.stability == SelectorStability.FRAGILE.value)
        
        # Count by strategy
        strategies = {}
        for selector in selectors:
            strategy = selector.primary_strategy
            strategies[strategy] = strategies.get(strategy, 0) + 1
        
        # Average stability score
        avg_score = sum(s.stability_score or 0 for s in selectors) / total if total > 0 else 0
        
        # Generate recommendations
        recommendations = []
        
        if fragile > total * 0.2:
            recommendations.append(
                f"⚠️  {fragile} fragile selectors detected ({fragile/total*100:.1f}%). "
                "Add test tags to improve stability."
            )
        
        if poor + fragile > total * 0.3:
            recommendations.append(
                f"⚠️  {poor + fragile} unstable selectors ({(poor+fragile)/total*100:.1f}%). "
                "Consider using accessibility IDs or resource IDs."
            )
        
        xpath_count = strategies.get('xpath', 0)
        if xpath_count > total * 0.5:
            recommendations.append(
                f"⚠️  {xpath_count} XPath selectors ({xpath_count/total*100:.1f}%). "
                "XPath is fragile. Add stable IDs to UI elements."
            )
        
        if avg_score >= 0.8:
            recommendations.append(
                f"✅ Good selector quality! Average stability: {avg_score:.2f}"
            )
        
        return {
            'total': total,
            'average_stability': round(avg_score, 2),
            'stability_distribution': {
                'excellent': excellent,
                'good': good,
                'fair': fair,
                'poor': poor,
                'fragile': fragile
            },
            'strategy_distribution': strategies,
            'recommendations': recommendations
        }
    
    def find_duplicate_selectors(
        self,
        selectors: List[Selector]
    ) -> List[tuple[str, str]]:
        """
        Find duplicate selectors (same selector for different elements)
        
        Args:
            selectors: List of selectors
        
        Returns:
            List of (element_id1, element_id2) tuples with duplicate selectors
        """
        duplicates = []
        seen = {}
        
        for selector in selectors:
            # Check Android selector
            if selector.android:
                key = str(sorted(selector.android.items()))
                if key in seen:
                    duplicates.append((seen[key], selector.id))
                else:
                    seen[key] = selector.id
        
        return duplicates
    
    def suggest_improvements(self, selector: Selector) -> List[str]:
        """
        Suggest improvements for a selector
        
        Args:
            selector: Selector to analyze
        
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        
        # Check stability
        if selector.stability_score and selector.stability_score < 0.5:
            suggestions.append(
                "⚠️  Low stability score. Add test tags or accessibility IDs to UI elements."
            )
        
        # Check if using XPath
        if selector.android and 'xpath' in selector.android:
            suggestions.append(
                "💡 Using XPath. Consider adding resource-id or test tag for better stability."
            )
        
        # Check if using text
        if selector.android and 'text' in selector.android:
            text = selector.android['text']
            if self.scorer._looks_dynamic(text):
                suggestions.append(
                    f"⚠️  Text selector '{text}' looks dynamic. May break if content changes."
                )
        
        # Check if missing iOS selector
        if selector.android and not selector.ios:
            suggestions.append(
                "💡 Missing iOS selector. Add for cross-platform support."
            )
        
        # Check fallback strategies
        if not selector.fallback_strategies or len(selector.fallback_strategies) < 2:
            suggestions.append(
                "💡 Add more fallback strategies for resilience."
            )
        
        if not suggestions:
            suggestions.append("✅ Selector looks good!")
        
        return suggestions

