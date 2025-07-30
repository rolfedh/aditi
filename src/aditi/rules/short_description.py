"""ShortDescription rule implementation.

This rule detects missing or improperly formatted short description elements
in AsciiDoc files that need the role="_abstract" attribute for DITA conversion.
"""

from pathlib import Path
from typing import Optional

from .base import Rule, FixType, Fix
from ..vale_parser import Violation


class ShortDescriptionRule(Rule):
    """Rule for detecting missing or invalid short description elements.
    
    DITA requires a short description element which in AsciiDoc is created
    by adding [role="_abstract"] to a paragraph.
    """
    
    @property
    def name(self) -> str:
        return "ShortDescription"
    
    @property
    def fix_type(self) -> FixType:
        return FixType.NON_DETERMINISTIC
    
    @property
    def description(self) -> str:
        return ("DITA topics require a short description element. In AsciiDoc, "
                "add [role=\"_abstract\"] above a paragraph to create one.")
    
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