"""TableFooter rule implementation.

This rule prevents table footer usage that's not supported in DITA.
"""

from pathlib import Path
from typing import Optional

from .base import Rule, FixType, Fix
from ..vale_parser import Violation


class TableFooterRule(Rule):
    """Rule for detecting table footers that aren't supported in DITA.
    
    DITA 1.3 doesn't support table footers.
    Consider moving footer content to table caption or following content.
    """
    
    @property
    def name(self) -> str:
        return "TableFooter"
    
    @property
    def fix_type(self) -> FixType:
        return FixType.NON_DETERMINISTIC
    
    @property
    def description(self) -> str:
        return ("DITA 1.3 doesn't support table footers. "
                "Consider moving footer content to table caption or following content.")
    
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
            replacement_text=f"// AsciiDocDITA {violation.message}",
            confidence=1.0,
            requires_review=True,
            description="Flag for manual review"
        )
        
        return fix