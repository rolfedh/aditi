"""ExampleBlock rule implementation.

This rule detects example blocks that appear outside the main body of the topic,
such as in sections, within other blocks, or as part of lists.
"""

from typing import Optional

from .base import Rule, FixType, Fix
from ..vale_parser import Violation


class ExampleBlockRule(Rule):
    """Rule for flagging example blocks outside the main body.
    
    DITA 1.3 allows the <example> element to appear only within the main body
    of the topic. Do not use example blocks in sections, within other blocks,
    or as part of lists.
    """
    
    @property
    def name(self) -> str:
        """Rule identifier matching Vale rule name."""
        return "ExampleBlock"
    
    @property
    def fix_type(self) -> FixType:
        """Classification of fix determinism."""
        return FixType.NON_DETERMINISTIC
    
    @property
    def description(self) -> str:
        """Human-readable description of what this rule does."""
        return ("DITA 1.3 allows the <example> element to appear only within the main body "
                "of the topic. Do not use example blocks in sections, within other blocks, "
                "or as part of lists.")
    
    def can_fix(self, violation: Violation) -> bool:
        """Check if this rule can fix the violation.
        
        Args:
            violation: The violation to check
            
        Returns:
            True if this is an ExampleBlock violation
        """
        return violation.rule_name == "ExampleBlock"
    
    def generate_fix(self, violation: Violation, file_content: str) -> Optional[Fix]:
        """Generate a comment flag for the violation.
        
        Args:
            violation: The violation to fix
            file_content: The content of the file (not used for non-deterministic fixes)
            
        Returns:
            A Fix that adds a comment flag
        """
        # Use the Vale message directly
        comment = f"// AsciiDocDITA {violation.message}"
        
        return Fix(
            violation=violation,
            replacement_text=comment,
            confidence=1.0,
            requires_review=True,
            description="Flag for manual review"
        )