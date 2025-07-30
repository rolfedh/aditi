"""RelatedLinks rule implementation.

This rule specifies link formatting rules for DITA compatibility.
"""

from pathlib import Path
from typing import Optional

from .base import Rule, FixType, Fix
from ..vale_parser import Violation


class RelatedLinksRule(Rule):
    """Rule for detecting link formatting issues in DITA conversion.
    
    DITA has specific requirements for related links formatting.
    Links should follow DITA conventions for proper conversion.
    """
    
    @property
    def name(self) -> str:
        return "RelatedLinks"
    
    @property
    def fix_type(self) -> FixType:
        return FixType.NON_DETERMINISTIC
    
    @property
    def description(self) -> str:
        return ("DITA has specific requirements for related links formatting. "
                "Ensure links follow DITA conventions for proper conversion.")
    
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