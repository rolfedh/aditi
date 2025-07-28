"""NestedSection rule implementation.

This rule detects nested sections (level 2 and deeper) which are not allowed in DITA.
"""

from typing import Optional

from .base import Rule, FixType, Fix
from ..vale_parser import Violation


class NestedSectionRule(Rule):
    """Rule for flagging nested sections.
    
    DITA 1.3 allows the <section> element to appear only within the main body
    of the topic. If a level 2 section is needed, move it to a separate file.
    """
    
    @property
    def name(self) -> str:
        """Rule identifier matching Vale rule name."""
        return "NestedSection"
    
    @property
    def fix_type(self) -> FixType:
        """Classification of fix determinism."""
        return FixType.NON_DETERMINISTIC
    
    @property
    def description(self) -> str:
        """Human-readable description of what this rule does."""
        return ("DITA 1.3 allows the <section> element to appear only within the main body "
                "of the topic. If a level 2 section is needed, move it to a separate file.")
    
    def can_fix(self, violation: Violation) -> bool:
        """Check if this rule can fix the violation.
        
        Args:
            violation: The violation to check
            
        Returns:
            True if this is a NestedSection violation
        """
        return violation.rule_name == "NestedSection"
    
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