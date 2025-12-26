"""
Machine Learning module for intelligent element classification and prediction.

This module provides AI/ML capabilities for:
- Element type classification
- Visual element detection
- Selector healing
- Flow pattern recognition
- Analytics dashboards
"""

from framework.ml.element_classifier import ElementClassifier
from framework.ml.visual_detector import VisualDetector
from framework.ml.selector_healer import SelectorHealer
from framework.ml.pattern_recognizer import PatternRecognizer
from framework.ml.analytics_dashboard import AnalyticsDashboard

__all__ = [
    'ElementClassifier',
    'VisualDetector',
    'SelectorHealer',
    'PatternRecognizer',
    'AnalyticsDashboard',
]

