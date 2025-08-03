"""LineBreak rule implementation.

This rule detects and removes hard line breaks that are not supported in DITA.
Hard line breaks in AsciiDoc (using +, :hardbreaks-option:, [options="hardbreaks"], 
or [%hardbreaks]) need to be removed for DITA compatibility.
"""

import re
from pathlib import Path
from typing import Optional

from .base import Rule, FixType, Fix
from ..vale_parser import Violation


class LineBreakRule(Rule):
    """Rule for detecting and removing hard line breaks not supported in DITA.
    
    DITA does not support hard line breaks. This rule removes various AsciiDoc
    hard line break syntaxes:
    - Lines ending with space + plus sign (e.g., "text +")
    - :hardbreaks-option: attribute
    - [options="hardbreaks"] or [options='hardbreaks'] or [options=hardbreaks]
    - [%hardbreaks] shorthand syntax
    """
    
    @property
    def name(self) -> str:
        return "LineBreak"
    
    @property
    def fix_type(self) -> FixType:
        return FixType.FULLY_DETERMINISTIC
    
    @property
    def description(self) -> str:
        return ("Removes hard line break syntax that is not supported in DITA "
                "(e.g., trailing +, :hardbreaks-option:, [%hardbreaks])")
    
    @property
    def dependencies(self) -> list[str]:
        return []
    
    def can_fix(self, violation: Violation) -> bool:
        """Check if this rule can fix the violation."""
        return violation.rule_name == self.name
    
    def _is_in_comment(self, file_content: str, line_number: int) -> bool:
        """Check if the violation is within a comment line."""
        line = self.get_line_content(file_content, line_number)
        # Check if line starts with comment markers (accounting for whitespace)
        return bool(re.match(r'^\s*//', line))
    
    def _is_in_code_block(self, file_content: str, line_number: int) -> bool:
        """Check if the violation is within a code block."""
        lines = file_content.splitlines()
        in_code_block = False
        
        for i in range(min(line_number, len(lines))):
            line = lines[i].strip()
            # Check for code block delimiters
            if line in ['----', '....', '````']:
                in_code_block = not in_code_block
        
        return in_code_block
    
    def _is_in_inline_code(self, line_content: str, column: int) -> bool:
        """Check if the + is within inline code (backticks).
        
        Args:
            line_content: The content of the line
            column: The column position of the violation (1-based)
            
        Returns:
            True if the + is inside inline code
        """
        # Find all backtick pairs in the line
        # Match both single backticks and double backticks
        patterns = [
            (r'``[^`]+``', 2),  # Double backticks (offset 2)
            (r'`[^`]+`', 1)     # Single backticks (offset 1)
        ]
        
        for pattern, offset in patterns:
            for match in re.finditer(pattern, line_content):
                # Adjust for 1-based column indexing
                if match.start() + offset < column - 1 < match.end() - offset:
                    return True
        
        # Also check for literal passthrough (single plus signs)
        # Pattern: +text+
        for match in re.finditer(r'\+[^+]+\+', line_content):
            if match.start() < column - 1 < match.end():
                return True
                
        return False
    
    def generate_fix(self, violation: Violation, file_content: str) -> Optional[Fix]:
        """Generate a fix for the violation."""
        if not self.can_fix(violation):
            return None
        
        # Skip if in comment or code block
        if self._is_in_comment(file_content, violation.line):
            return None
        if self._is_in_code_block(file_content, violation.line):
            return None
        
        line_content = self.get_line_content(file_content, violation.line)
        original_line = line_content
        replacement_text = None
        description = None
        
        # Check for different hard break patterns
        if re.search(r'\s\+\s*$', line_content):
            # Check if the + is inside inline code before fixing
            match = re.search(r'\s\+\s*$', line_content)
            if match and self._is_in_inline_code(line_content, match.start() + 2):
                # The + is part of inline code, don't fix
                return None
            # Remove trailing space + plus sign
            replacement_text = re.sub(r'\s\+\s*$', '', line_content).rstrip()
            description = "Remove trailing + hard line break"
            
        elif ':hardbreaks-option:' in line_content:
            # Remove the entire hardbreaks-option line
            replacement_text = ""
            description = "Remove :hardbreaks-option: attribute"
            
        elif re.match(r'^\s*\[options=["\']?hardbreaks["\']?\]\s*$', line_content):
            # Remove the entire options line
            replacement_text = ""
            description = "Remove [options=hardbreaks] attribute"
            
        elif re.match(r'^\s*\[%hardbreaks\]\s*$', line_content):
            # Remove the entire %hardbreaks line
            replacement_text = ""
            description = "Remove [%hardbreaks] attribute"
        
        if replacement_text is not None:
            # Create the fix
            fix = Fix(
                violation=violation,
                replacement_text=replacement_text,
                confidence=0.95,
                requires_review=False,
                description=description
            )
            
            # Validate the fix
            if self.validate_fix(fix, file_content):
                return fix
        
        return None
    
    def validate_fix(self, fix: Fix, file_content: str) -> bool:
        """Validate that the fix won't break the document."""
        # Basic validation - ensure we're not removing critical content
        if fix.replacement_text == "":
            # When removing entire lines, check if they only contain the attribute
            line_content = self.get_line_content(file_content, fix.violation.line).strip()
            # These patterns are safe to remove entirely
            safe_to_remove = [
                r'^:hardbreaks-option:\s*$',
                r'^\[options=["\']?hardbreaks["\']?\]\s*$',
                r'^\[%hardbreaks\]\s*$'
            ]
            return any(re.match(pattern, line_content) for pattern in safe_to_remove)
        
        return True