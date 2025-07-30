"""TaskTitle rule implementation.

This rule detects issues with task topic titles that may not follow
DITA task title conventions.
"""

from pathlib import Path
from typing import Optional

from .base import Rule, FixType, Fix
from ..vale_parser import Violation


class TaskTitleRule(Rule):
    """Rule for detecting task title issues.
    
    DITA task topics should have titles that clearly indicate the task
    being performed, typically using imperative verb forms.
    """
    
    @property
    def name(self) -> str:
        return "TaskTitle"
    
    @property
    def fix_type(self) -> FixType:
        return FixType.NON_DETERMINISTIC
    
    @property
    def description(self) -> str:
        return ("DITA task titles should clearly describe the task using "
                "imperative verbs (e.g., 'Install the software', 'Configure settings').")
    
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