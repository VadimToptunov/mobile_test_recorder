"""
Parallel test execution with intelligent sharding

Distributes tests across multiple workers for faster execution.
"""

from .test_sharding import TestSharding, ShardStrategy
from .parallel_executor import ParallelExecutor, ExecutionResult

__all__ = [
    'TestSharding',
    'ShardStrategy',
    'ParallelExecutor',
    'ExecutionResult',
]
