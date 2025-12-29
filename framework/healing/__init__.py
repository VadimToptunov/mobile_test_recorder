"""
Self-healing test system

Automatically detects and fixes broken selectors when tests fail.
"""

from .failure_analyzer import FailureAnalyzer, SelectorFailure
from .selector_discovery import SelectorDiscovery, AlternativeSelector
from .element_matcher import ElementMatcher, MatchResult
from .file_updater import FileUpdater, UpdateResult

__all__ = [
    'FailureAnalyzer',
    'SelectorFailure',
    'SelectorDiscovery',
    'AlternativeSelector',
    'ElementMatcher',
    'MatchResult',
    'FileUpdater',
    'UpdateResult',
]

