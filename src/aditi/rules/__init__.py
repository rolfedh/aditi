"""Rule framework for Aditi.

This package contains the rule engine that processes Vale violations
and applies fixes to AsciiDoc files.
"""

from .base import Rule, FixType, Fix
from .registry import RuleRegistry, get_rule_registry

__all__ = [
    "Rule",
    "FixType", 
    "Fix",
    "RuleRegistry",
    "get_rule_registry"
]