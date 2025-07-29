"""EquationFormula rule implementation.

This rule notes the lack of LaTeX/AsciiMath support in DITA conversion.
"""

from pathlib import Path
from typing import Optional

from .base import Rule, FixType, Fix
from ..vale_parser import Violation


class EquationFormulaRule(Rule):
    """Rule for detecting equations that may not convert to DITA.
    
    DITA conversion doesn't support LaTeX or AsciiMath equations.
    Mathematical content may need to be converted to images or MathML.
    """
    
    @property
    def name(self) -> str:
        return "EquationFormula"
    
    @property
    def fix_type(self) -> FixType:
        return FixType.NON_DETERMINISTIC
    
    @property
    def description(self) -> str:
        return ("DITA conversion doesn't support LaTeX or AsciiMath equations. "
                "Consider converting to images or MathML.")
    
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