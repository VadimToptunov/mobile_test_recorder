"""
Integration with existing test frameworks
"""

from .framework_detector import FrameworkDetector, DetectedFramework
from .style_analyzer import StyleAnalyzer, TestStyle
from .adaptive_generator import AdaptiveGenerator

__all__ = [
    'FrameworkDetector',
    'DetectedFramework',
    'StyleAnalyzer',
    'TestStyle',
    'AdaptiveGenerator',
]

