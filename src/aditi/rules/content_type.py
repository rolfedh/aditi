"""ContentType rule implementation.

This rule detects missing or invalid :_mod-docs-content-type: attributes
and adds appropriate content types based on filename patterns and existing attributes.
"""

import re
from typing import Optional, List, Tuple
from pathlib import Path

from .base import Rule, FixType, Fix
from ..vale_parser import Violation


class ContentTypeRule(Rule):
    """Rule for detecting and fixing missing content type attributes.
    
    Valid content types:
    - ASSEMBLY
    - CONCEPT
    - PROCEDURE
    - REFERENCE
    - SNIPPET
    """
    
    VALID_CONTENT_TYPES = ["ASSEMBLY", "CONCEPT", "PROCEDURE", "REFERENCE", "SNIPPET"]
    
    # Filename prefix patterns for content type detection
    FILENAME_PATTERNS = {
        "assembly": "ASSEMBLY",
        "con-": "CONCEPT",
        "concept": "CONCEPT",
        "proc-": "PROCEDURE",
        "procedure": "PROCEDURE",
        "ref-": "REFERENCE",
        "reference": "REFERENCE",
        "snip-": "SNIPPET",
        "snippet": "SNIPPET"
    }
    
    # Deprecated attribute patterns
    DEPRECATED_ATTRIBUTES = {
        ":type:": True,
        ":Type:": True,
        ":content-type:": True,
        ":ContentType:": True,
        ":_content-type:": True
    }
    
    @property
    def name(self) -> str:
        return "ContentType"
    
    @property
    def fix_type(self) -> FixType:
        return FixType.PARTIALLY_DETERMINISTIC
    
    @property
    def description(self) -> str:
        return ("Detects missing or invalid content type attributes and adds them "
                "based on filename patterns or replaces with TBD placeholder")
    
    def can_fix(self, violation: Violation) -> bool:
        """Check if this rule can fix the violation."""
        return violation.rule_name == self.name
    
    def detect_content_type_from_filename(self, filename: str) -> Optional[str]:
        """Detect content type from filename patterns.
        
        Args:
            filename: The filename to analyze
            
        Returns:
            The detected content type or None
        """
        filename_lower = filename.lower()
        
        for pattern, content_type in self.FILENAME_PATTERNS.items():
            if filename_lower.startswith(pattern):
                return content_type
                
        return None
    
    def find_existing_attributes(self, file_content: str) -> List[Tuple[int, str, str]]:
        """Find existing content type attributes in the file.
        
        Args:
            file_content: The file content to search
            
        Returns:
            List of tuples (line_number, attribute_name, value)
        """
        attributes = []
        lines = file_content.splitlines()
        
        # Pattern for content type attributes (including commented out)
        patterns = [
            # Standard attribute
            (r'^:_mod-docs-content-type:\s*(.*)$', ':_mod-docs-content-type:'),
            # Commented out attribute  
            (r'^//\s*:_mod-docs-content-type:\s*(.*)$', '// :_mod-docs-content-type:'),
            # Deprecated attributes
            (r'^:(type|Type|content-type|ContentType|_content-type):\s*(.*)$', None)
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, attr_name in patterns:
                match = re.match(pattern, line)
                if match:
                    if attr_name:  # Standard or commented attribute
                        value = match.group(1).strip()
                    else:  # Deprecated attribute
                        attr_name = match.group(1)
                        value = match.group(2).strip()
                    attributes.append((i, attr_name, value))
                    
        return attributes
    
    def find_title_line(self, file_content: str) -> int:
        """Find the first title line in the file.
        
        Args:
            file_content: The file content to search
            
        Returns:
            Line number of the first title (1-based) or 0 if not found
        """
        lines = file_content.splitlines()
        
        for i, line in enumerate(lines, 1):
            # Look for AsciiDoc title patterns
            if line.startswith('= ') or line.startswith('== '):
                return i
                
        return 0
    
    def find_insertion_point_after_comment_blocks(self, file_content: str) -> int:
        """Find the appropriate insertion point after any initial comment blocks.
        
        This method ensures we don't insert attributes inside comment blocks.
        Returns the line number after the last initial comment block, accounting
        for any blank lines that should be preserved.
        
        Args:
            file_content: The file content to search
            
        Returns:
            Line number for insertion (1-based)
        """
        lines = file_content.splitlines()
        in_comment_block = False
        last_comment_block_end = 0
        found_content_after_comments = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Check for comment block delimiters
            if stripped == '////':
                if not in_comment_block:
                    in_comment_block = True
                else:
                    in_comment_block = False
                    last_comment_block_end = i + 1
            
            # If we're past comment blocks and found non-comment content
            elif not in_comment_block and last_comment_block_end > 0:
                if stripped and not stripped.startswith('//'):
                    found_content_after_comments = True
                    break
        
        if last_comment_block_end > 0:
            # We found comment blocks at the start
            # Skip any blank lines after the comment block
            insert_line = last_comment_block_end
            while insert_line < len(lines) and not lines[insert_line].strip():
                insert_line += 1
            return insert_line + 1
        else:
            # No initial comment blocks, insert at line 1
            return 1
    
    def generate_fix(self, violation: Violation, file_content: str) -> Optional[Fix]:
        """Generate a fix for the violation."""
        if not self.can_fix(violation):
            return None
            
        # Check for existing attributes
        existing_attrs = self.find_existing_attributes(file_content)
        
        # Determine the content type
        content_type = None
        
        # First, check for commented out attributes with valid values
        for line_num, attr_name, value in existing_attrs:
            if '// :_mod-docs-content-type:' in attr_name and value in self.VALID_CONTENT_TYPES:
                content_type = value
                break
                
        # Second, check deprecated attributes
        if not content_type:
            for line_num, attr_name, value in existing_attrs:
                if attr_name in self.DEPRECATED_ATTRIBUTES and value.upper() in self.VALID_CONTENT_TYPES:
                    content_type = value.upper()
                    break
                    
        # Third, try to detect from filename
        if not content_type:
            filename = violation.file_path.name
            content_type = self.detect_content_type_from_filename(filename)
            
        # If still no content type, use TBD
        if not content_type:
            content_type = "TBD"
            
        # Determine where to insert the attribute
        # First check for comment blocks to avoid inserting inside them
        after_comment_line = self.find_insertion_point_after_comment_blocks(file_content)
        title_line = self.find_title_line(file_content)
        
        if title_line == 0:
            # No title found, use the position after comment blocks
            insert_line = after_comment_line
        else:
            # We want to insert before the title but after any initial comment blocks
            # Prefer 2-3 lines before title, but not before the comment block end
            preferred_line = max(1, title_line - 3)
            insert_line = max(after_comment_line, preferred_line)
            
        # Create the attribute line with blank line after
        attribute_line = f":_mod-docs-content-type: {content_type}\n"
        
        # Determine the fix based on existing attributes
        if existing_attrs:
            # Replace the first existing attribute
            first_attr = existing_attrs[0]
            line_num, attr_name, value = first_attr
            
            # Get the current line
            lines = file_content.splitlines(keepends=True)
            if line_num <= len(lines):
                current_line = lines[line_num - 1]
                
                # Check if next line exists and add blank line if needed
                lines = file_content.splitlines(keepends=True)
                replacement_text = attribute_line.rstrip()
                
                # Check if we need to add a blank line after the attribute
                if line_num < len(lines):
                    next_line = lines[line_num] if line_num < len(lines) else ""
                    # If next line is not empty, add a blank line
                    if next_line.strip():
                        replacement_text += "\n"
                
                # Create replacement text
                if content_type == "TBD":
                    description = "Replace with valid content type attribute (TBD placeholder)"
                else:
                    description = f"Replace with content type: {content_type}"
                    
                fix = Fix(
                    violation=violation,
                    replacement_text=replacement_text,
                    confidence=0.8 if content_type != "TBD" else 0.5,
                    requires_review=True,
                    description=description
                )
                
                # Store additional context for the processor
                fix.line_to_replace = line_num
                fix.original_line = current_line
                
                return fix
        else:
            # Insert new attribute
            lines = file_content.splitlines(keepends=True)
            
            # Check if we need to add a blank line after the attribute
            replacement_text = attribute_line
            if insert_line <= len(lines):
                next_line = lines[insert_line - 1] if insert_line <= len(lines) else ""
                # If next line is not empty, add a blank line
                if next_line.strip():
                    replacement_text += "\n"
            
            if content_type == "TBD":
                description = "Insert content type attribute with TBD placeholder"
            else:
                description = f"Insert content type: {content_type}"
                
            fix = Fix(
                violation=violation,
                replacement_text=replacement_text,
                confidence=0.8 if content_type != "TBD" else 0.5,
                requires_review=True,
                description=description
            )
            
            # Store insertion context
            fix.insert_at_line = insert_line
            
            return fix
            
        return None