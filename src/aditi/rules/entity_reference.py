"""EntityReference rule implementation.

This rule detects unsupported HTML entities in AsciiDoc and replaces them
with DITA-compatible AsciiDoc attributes.
"""

from typing import Optional, Dict

from .base import Rule, FixType, Fix
from ..vale_parser import Violation


class EntityReferenceRule(Rule):
    """Rule for replacing unsupported HTML entities with DITA-compatible ones.
    
    DITA 1.3 supports only five character entity references:
    - &amp; (&)
    - &lt; (<)
    - &gt; (>)
    - &apos; (')
    - &quot; (")
    
    All other entities must be replaced with appropriate AsciiDoc attributes.
    """
    
    # Mapping of HTML entities to AsciiDoc attributes
    ENTITY_REPLACEMENTS: Dict[str, str] = {
        "&nbsp;": "{nbsp}",
        "&ndash;": "{ndash}",
        "&mdash;": "{mdash}",
        "&hellip;": "{hellip}",
        "&ldquo;": "{ldquo}",
        "&rdquo;": "{rdquo}",
        "&lsquo;": "{lsquo}",
        "&rsquo;": "{rsquo}",
        "&trade;": "{trade}",
        "&reg;": "{reg}",
        "&copy;": "{copy}",
        "&deg;": "{deg}",
        "&plusmn;": "{plusmn}",
        "&frac12;": "{frac12}",
        "&frac14;": "{frac14}",
        "&frac34;": "{frac34}",
        "&times;": "{times}",
        "&divide;": "{divide}",
        "&euro;": "{euro}",
        "&pound;": "{pound}",
        "&yen;": "{yen}",
        "&cent;": "{cent}",
        # Common numeric entities
        "&#160;": "{nbsp}",  # Non-breaking space
        "&#8211;": "{ndash}",  # En dash
        "&#8212;": "{mdash}",  # Em dash
        "&#8230;": "{hellip}",  # Ellipsis
        "&#8220;": "{ldquo}",  # Left double quote
        "&#8221;": "{rdquo}",  # Right double quote
        "&#8216;": "{lsquo}",  # Left single quote
        "&#8217;": "{rsquo}",  # Right single quote
        "&#8482;": "{trade}",  # Trademark
        "&#174;": "{reg}",  # Registered
        "&#169;": "{copy}",  # Copyright
    }
    
    @property
    def name(self) -> str:
        return "EntityReference"
    
    @property
    def fix_type(self) -> FixType:
        return FixType.FULLY_DETERMINISTIC
    
    @property
    def description(self) -> str:
        return ("Replaces unsupported HTML entities with DITA-compatible "
                "AsciiDoc attributes (e.g., &nbsp; → {nbsp})")
    
    def can_fix(self, violation: Violation) -> bool:
        """Check if this rule can fix the violation."""
        # Check if it's an EntityReference violation
        if violation.rule_name != self.name:
            return False
            
        # Check if we have a replacement for the matched entity
        # Handle both with and without semicolon
        entity = violation.original_text
        if not entity.endswith(';'):
            entity = entity + ';'
        return entity in self.ENTITY_REPLACEMENTS
    
    def generate_fix(self, violation: Violation, file_content: str) -> Optional[Fix]:
        """Generate a fix for the violation."""
        if not self.can_fix(violation):
            return None
            
        # Get the replacement text
        # Handle both with and without semicolon
        entity = violation.original_text
        if not entity.endswith(';'):
            entity = entity + ';'
            
        replacement = self.ENTITY_REPLACEMENTS.get(entity)
        if not replacement:
            return None
            
        # Create the fix
        fix = Fix(
            violation=violation,
            replacement_text=replacement,
            confidence=1.0,  # This is a fully deterministic fix
            requires_review=False,
            description=f"Replace '{entity}' with '{replacement}'"
        )
        
        # Validate the fix
        if not self.validate_fix(fix, file_content):
            return None
            
        return fix
    
    def validate_fix(self, fix: Fix, file_content: str) -> bool:
        """Validate that the fix won't break the document."""
        # For entity references, we just need to ensure the replacement
        # doesn't create invalid AsciiDoc syntax
        
        # Get the line content
        line_content = self.get_line_content(file_content, fix.violation.line)
        if not line_content:
            return False
            
        # Check if we're inside a code block
        # Look for code block delimiters before the current line
        lines = file_content.splitlines()
        in_code_block = False
        for i in range(fix.violation.line - 1):
            line = lines[i].strip()
            if line == "----" or line == "....":
                in_code_block = not in_code_block
                
        if in_code_block:
            return False
            
        # Check if we're inside inline code
        # Count backticks before the entity position
        before_text = line_content[:fix.violation.column - 1]
        backtick_count = before_text.count("`")
        if backtick_count % 2 != 0:  # Odd number means we're inside inline code
            return False
            
        return True