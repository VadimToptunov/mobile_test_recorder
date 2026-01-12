"""
Integration module for existing test frameworks
"""

from .model_enricher import ModelEnricher, ProjectIntegrator, EnrichmentResult

__all__ = [
    "ModelEnricher",
    "ProjectIntegrator",
    "EnrichmentResult",
]
