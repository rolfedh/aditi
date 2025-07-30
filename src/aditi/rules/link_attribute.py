"""LinkAttribute rule implementation.

This rule prevents attribute references in link URLs that may not work in DITA.
"""

from pathlib import Path
from typing import Optional

from .base import Rule, FixType, Fix
from ..vale_parser import Violation


class LinkAttributeRule(Rule):
    """Rule for detecting attribute references in link URLs.
    
    DITA may not resolve attribute references in link URLs correctly.
    Use direct URLs or restructure links to avoid attribute references.
    """
    
    @property
    def name(self) -> str:
        return "LinkAttribute"
    
    @property
    def fix_type(self) -> FixType:
        return FixType.NON_DETERMINISTIC
    
    @property
    def description(self) -> str:
        return ("DITA may not resolve attribute references in link URLs correctly. "
                "Use direct URLs or restructure links.")
    
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