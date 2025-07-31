"""Aditi - AsciiDoc DITA Integration.

A CLI tool to prepare AsciiDoc files for migration to DITA by identifying
and fixing compatibility issues using Vale with AsciiDocDITA rules.
"""

# Version is now maintained in pyproject.toml only
# Use importlib.metadata to read it dynamically
try:
    from importlib.metadata import version
    __version__ = version("aditi")
except Exception:
    # Fallback for development/editable installs
    import sys
    from pathlib import Path
    try:
        if sys.version_info >= (3, 11):
            import tomllib
        else:
            import tomli as tomllib
        
        # Find pyproject.toml
        root = Path(__file__).parent.parent.parent
        pyproject_path = root / "pyproject.toml"
        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
                __version__ = data.get("project", {}).get("version", "unknown")
        else:
            __version__ = "unknown"
    except Exception:
        __version__ = "unknown"

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