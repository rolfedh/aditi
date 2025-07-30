"""AuthorLine rule implementation.

This rule recommends adding an empty line after the document title for proper formatting.
"""

from pathlib import Path
from typing import Optional

from .base import Rule, FixType, Fix
from ..vale_parser import Violation


class AuthorLineRule(Rule):
    """Rule for detecting missing empty line after document title.
    
    DITA conversion works better when there's an empty line after the document title.
    This helps separate the title from the content that follows.
    """
    
    @property
    def name(self) -> str:
        return "AuthorLine"
    
    @property
    def fix_type(self) -> FixType:
        return FixType.NON_DETERMINISTIC
    
    @property
    def description(self) -> str:
        return ("Add an empty line after the document title to improve DITA conversion. "
                "This helps separate title metadata from content.")
    
    @property
    def dependencies(self) -> list[str]:
        return []
    
    def can_fix(self, violation: Violation) -> bool:
        """Check if this rule can fix the violation."""
        return violation.rule_name == self.name
    
    def generate_fix(self, violation: Violation, file_content: str) -> Optional[Fix]:
        """Generate a fix for the violation."""
        if not self.can_fix(violation):
            return None
        
        # For non-deterministic rules, we just flag the issue
        fix = Fix(
            violation=violation,
            replacement_text=self.create_comment_flag(violation),
            confidence=1.0,
            requires_review=True,
            description="Flag for manual review"
        )
        
        return fix