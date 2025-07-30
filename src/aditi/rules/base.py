"""Base classes for the Aditi rule framework."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any

from ..vale_parser import Violation


class FixType(Enum):
    """Classification of fix determinism."""
    FULLY_DETERMINISTIC = "fully_deterministic"
    PARTIALLY_DETERMINISTIC = "partially_deterministic"
    NON_DETERMINISTIC = "non_deterministic"


@dataclass
class Fix:
    """Represents a fix for a violation."""
    violation: Violation
    replacement_text: str
    confidence: float  # 0.0 to 1.0
    requires_review: bool = False
    description: Optional[str] = None
    
    @property
    def is_comment_flag(self) -> bool:
        """Check if this fix is just adding a comment flag."""
        return self.replacement_text.startswith("// ")


class Rule(ABC):
    """Abstract base class for all rules."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Rule identifier matching Vale rule name."""
        pass
    
    @property
    @abstractmethod
    def fix_type(self) -> FixType:
        """Classification of fix determinism."""
        pass
    
    @property
    def dependencies(self) -> List[str]:
        """List of rule names that must run before this rule."""
        return []
    
    @property
    def description(self) -> str:
        """Human-readable description of what this rule does."""
        return ""
    
    @abstractmethod
    def can_fix(self, violation: Violation) -> bool:
        """Check if this rule can fix the violation.
        
        Args:
            violation: The violation to check
            
        Returns:
            True if this rule can handle the violation
        """
        pass
    
    def create_comment_flag(self, violation: Violation) -> str:
        """Create a standardized comment flag for violations.
        
        Args:
            violation: The violation to flag
            
        Returns:
            Formatted comment string with Check, Severity, Message
        """
        return f"// {violation.check}, {violation.severity.value}, {violation.message}"
    
    @abstractmethod
    def generate_fix(self, violation: Violation, file_content: str) -> Optional[Fix]:
        """Generate a fix for the violation.
        
        Args:
            violation: The violation to fix
            file_content: The full content of the file
            
        Returns:
            A Fix object if a fix can be generated, None otherwise
        """
        pass
    
    def validate_fix(self, fix: Fix, file_content: str) -> bool:
        """Validate that a fix won't break the document.
        
        Args:
            fix: The fix to validate
            file_content: The current file content
            
        Returns:
            True if the fix is safe to apply
        """
        # Default implementation - can be overridden by specific rules
        return True
    
    def get_line_content(self, file_content: str, line_number: int) -> str:
        """Get the content of a specific line.
        
        Args:
            file_content: The full file content
            line_number: 1-based line number
            
        Returns:
            The content of the specified line
        """
        lines = file_content.splitlines(keepends=True)
        if 0 < line_number <= len(lines):
            return lines[line_number - 1]
        return ""
    
    def get_line_at_position(self, file_content: str, line: int, column: int) -> tuple[int, int]:
        """Get the start and end position of text at a specific line/column.
        
        Args:
            file_content: The full file content
            line: 1-based line number
            column: 1-based column number
            
        Returns:
            Tuple of (start_pos, end_pos) in the file content
        """
        lines = file_content.splitlines(keepends=True)
        if line < 1 or line > len(lines):
            return -1, -1
            
        # Calculate absolute position
        pos = sum(len(lines[i]) for i in range(line - 1))
        pos += column - 1
        
        return pos, pos
    
    def replace_text_at_position(self, content: str, start: int, end: int, replacement: str) -> str:
        """Replace text at a specific position in the content.
        
        Args:
            content: The original content
            start: Start position (0-based)
            end: End position (0-based)
            replacement: The replacement text
            
        Returns:
            The modified content
        """
        return content[:start] + replacement + content[end:]