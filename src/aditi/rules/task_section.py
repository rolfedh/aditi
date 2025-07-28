"""TaskSection rule implementation.

This rule detects sections in task topics.
"""

from typing import Optional

from .base import Rule, FixType, Fix
from ..vale_parser import Violation


class TaskSectionRule(Rule):
    """Rule for flagging sections in task topics.
    
    DITA 1.3 does not allow sections in a task topic.
    If a section is needed, move it to a separate file.
    """
    
    @property
    def name(self) -> str:
        """Rule identifier matching Vale rule name."""
        return "TaskSection"
    
    @property
    def fix_type(self) -> FixType:
        """Classification of fix determinism."""
        return FixType.NON_DETERMINISTIC
    
    @property
    def dependencies(self) -> list[str]:
        """List of rule names that must run before this rule."""
        return ["ContentType"]  # Needs to know if it's a task topic
    
    @property
    def description(self) -> str:
        """Human-readable description of what this rule does."""
        return ("DITA 1.3 does not allow sections in a task topic. "
                "If a section is needed, move it to a separate file.")
    
    def can_fix(self, violation: Violation) -> bool:
        """Check if this rule can fix the violation.
        
        Args:
            violation: The violation to check
            
        Returns:
            True if this is a TaskSection violation
        """
        return violation.rule_name == "TaskSection"
    
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