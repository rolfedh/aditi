"""TaskStep rule implementation.

This rule detects complex content in DITA task topics that cannot be
properly mapped to simple task steps.
"""

from pathlib import Path
from typing import Optional

from .base import Rule, FixType, Fix
from ..vale_parser import Violation


class TaskStepRule(Rule):
    """Rule for detecting complex content that doesn't map to DITA task steps.
    
    DITA task steps should contain simple, sequential instructions.
    Complex content like nested lists, code blocks, or multiple paragraphs
    may not convert properly.
    """
    
    @property
    def name(self) -> str:
        return "TaskStep"
    
    @property
    def fix_type(self) -> FixType:
        return FixType.NON_DETERMINISTIC
    
    @property
    def description(self) -> str:
        return ("DITA task steps should contain simple instructions. "
                "Complex content may need to be moved to separate topics or simplified.")
    
    @property
    def dependencies(self) -> list[str]:
        return ["ContentType"]
    
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