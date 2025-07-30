"""CrossReference rule implementation.

This rule restricts cross-references to the current document for DITA compatibility.
"""

from pathlib import Path
from typing import Optional

from .base import Rule, FixType, Fix
from ..vale_parser import Violation


class CrossReferenceRule(Rule):
    """Rule for detecting cross-references that may not work in DITA.
    
    DITA cross-references should be limited to the current document.
    External cross-references may need to be restructured.
    """
    
    @property
    def name(self) -> str:
        return "CrossReference"
    
    @property
    def fix_type(self) -> FixType:
        return FixType.NON_DETERMINISTIC
    
    @property
    def description(self) -> str:
        return ("DITA cross-references should be limited to the current document. "
                "External cross-references may need restructuring.")
    
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