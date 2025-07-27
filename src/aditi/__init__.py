"""Aditi - AsciiDoc DITA Integration.

A CLI tool to prepare AsciiDoc files for migration to DITA by identifying
and fixing compatibility issues using Vale with AsciiDocDITA rules.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__license__ = "MIT"

# Package metadata
__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "ValeContainer",
    "ConfigManager",
    "get_config_manager",
    "AditiConfig",
    "RepositoryConfig",
    "SessionState",
]

# Import key components for easier access
from aditi.vale_container import ValeContainer
from aditi.config import (
    ConfigManager,
    get_config_manager,
    AditiConfig,
    RepositoryConfig,
    SessionState,
)