"""BlockTitle rule implementation.

This rule limits title usage to specific block elements supported in DITA.
"""

from pathlib import Path
from typing import Optional

from .base import Rule, FixType, Fix
from ..vale_parser import Violation


class BlockTitleRule(Rule):
    """Rule for detecting unsupported block titles.
    
    DITA 1.3 only supports titles on certain block elements.
    Block titles on unsupported elements should be restructured.
    """
    
    @property
    def name(self) -> str:
        return "BlockTitle"
    
    @property
    def fix_type(self) -> FixType:
        return FixType.NON_DETERMINISTIC
    
    @property
    def description(self) -> str:
        return ("DITA 1.3 only supports titles on specific block elements. "
                "Consider restructuring or removing unsupported block titles.")
    
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