"""TaskDuplicate rule implementation.

This rule detects duplicate or redundant content in DITA task topics
that should be consolidated or removed.
"""

from pathlib import Path
from typing import Optional

from .base import Rule, FixType, Fix
from ..vale_parser import Violation


class TaskDuplicateRule(Rule):
    """Rule for detecting duplicate content in task topics.
    
    DITA task topics should have unique, non-redundant content.
    Duplicate steps or information should be consolidated or cross-referenced.
    """
    
    @property
    def name(self) -> str:
        return "TaskDuplicate"
    
    @property
    def fix_type(self) -> FixType:
        return FixType.NON_DETERMINISTIC
    
    @property
    def description(self) -> str:
        return ("DITA task topics should avoid duplicate content. "
                "Consider consolidating redundant steps or using cross-references.")
    
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