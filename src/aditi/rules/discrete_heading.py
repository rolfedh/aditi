"""DiscreteHeading rule implementation.

This rule suggests alternatives to discrete headings that don't convert well to DITA.
"""

from pathlib import Path
from typing import Optional

from .base import Rule, FixType, Fix
from ..vale_parser import Violation


class DiscreteHeadingRule(Rule):
    """Rule for detecting discrete headings that may not convert well to DITA.
    
    Discrete headings in AsciiDoc don't have direct DITA equivalents.
    Consider using regular sections or restructuring content.
    """
    
    @property
    def name(self) -> str:
        return "DiscreteHeading"
    
    @property
    def fix_type(self) -> FixType:
        return FixType.NON_DETERMINISTIC
    
    @property
    def description(self) -> str:
        return ("Discrete headings don't have direct DITA equivalents. "
                "Consider using regular sections or restructuring content.")
    
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