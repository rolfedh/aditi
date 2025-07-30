"""SidebarBlock rule implementation.

This rule recommends content restructuring instead of sidebar blocks.
"""

from pathlib import Path
from typing import Optional

from .base import Rule, FixType, Fix
from ..vale_parser import Violation


class SidebarBlockRule(Rule):
    """Rule for detecting sidebar blocks that need restructuring for DITA.
    
    DITA doesn't have direct sidebar equivalents.
    Consider restructuring sidebar content into separate topics or sections.
    """
    
    @property
    def name(self) -> str:
        return "SidebarBlock"
    
    @property
    def fix_type(self) -> FixType:
        return FixType.NON_DETERMINISTIC
    
    @property
    def description(self) -> str:
        return ("DITA doesn't have direct sidebar equivalents. "
                "Consider restructuring into separate topics or sections.")
    
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