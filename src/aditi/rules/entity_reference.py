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
            
        # Check if we're inside inline code
        # Count backticks before the entity position
        before_text = line_content[:fix.violation.column - 1]
        backtick_count = before_text.count("`")
        if backtick_count % 2 != 0:  # Odd number means we're inside inline code
            return False
            
        # Check if we're inside a code block and if replacements are enabled
        lines = file_content.splitlines()
        code_block_info = self._get_code_block_context(lines, fix.violation.line - 1)
        
        if code_block_info['in_code_block']:
            # Check if replacements are enabled for this code block
            if code_block_info['replacements_enabled']:
                return True  # Entities should be processed
            else:
                return False  # Entities should remain literal
            
        return True
    
    def _get_code_block_context(self, lines: list, target_line_idx: int) -> dict:
        """Determine if we're in a code block and check its substitution settings.
        
        Args:
            lines: List of all lines in the document
            target_line_idx: Zero-based index of the target line
            
        Returns:
            Dict with 'in_code_block' and 'replacements_enabled' flags
        """
        in_code_block = False
        block_type = None
        block_start_line = -1
        subs_value = None
        pending_source_subs = None  # Store subs from [source] line
        
        for i in range(min(target_line_idx + 1, len(lines))):
            line = lines[i].strip()
            
            # First check if this is a source attribute line
            if line.startswith("[source"):
                # Extract subs but don't mark as in block yet
                pending_source_subs = self._extract_subs_from_line(line)
                continue
                
            # Check for listing/source block delimiters
            if line == "----":
                if not in_code_block:
                    in_code_block = True
                    block_type = "listing"
                    block_start_line = i
                    # Check if there was a source line just before
                    if i > 0 and pending_source_subs is not None:
                        subs_value = pending_source_subs
                        block_type = "source"
                    else:
                        # Look for other attributes in previous lines
                        subs_value = self._find_block_attributes(lines, i)
                    pending_source_subs = None  # Reset
                else:
                    # Closing delimiter
                    in_code_block = False
                    block_type = None
                    subs_value = None
                    pending_source_subs = None
            elif line == "....":
                if not in_code_block:
                    in_code_block = True
                    block_type = "literal"
                    block_start_line = i
                    # Look for attributes in previous lines
                    subs_value = self._find_block_attributes(lines, i)
                else:
                    # Closing delimiter
                    in_code_block = False
                    block_type = None
                    subs_value = None
            else:
                # Any other line resets pending source
                if line and not line.startswith("["):
                    pending_source_subs = None
        
        # Determine if replacements are enabled
        replacements_enabled = False
        if subs_value:
            # Parse subs value
            subs_list = self._parse_subs_value(subs_value)
            replacements_enabled = 'replacements' in subs_list
        
        return {
            'in_code_block': in_code_block,
            'replacements_enabled': replacements_enabled,
            'block_type': block_type,
            'subs': subs_value
        }
    
    def _find_block_attributes(self, lines: list, delimiter_idx: int) -> Optional[str]:
        """Find block attributes that might contain subs setting.
        
        Args:
            lines: List of all lines
            delimiter_idx: Index of the block delimiter line
            
        Returns:
            The subs value if found, None otherwise
        """
        # Look backwards for block attributes (up to 3 lines)
        for i in range(max(0, delimiter_idx - 3), delimiter_idx):
            line = lines[i].strip()
            # Check for [source,...] or [listing,...] style attributes
            if line.startswith('[') and line.endswith(']'):
                return self._extract_subs_from_line(line)
        return None
    
    def _extract_subs_from_line(self, line: str) -> Optional[str]:
        """Extract subs value from an attribute line.
        
        Args:
            line: Line containing attributes like [source,java,subs="attributes+"]
            
        Returns:
            The subs value if found, None otherwise
        """
        import re
        
        # Look for subs="value" or subs='value'
        match = re.search(r'subs\s*=\s*["\']([^"\']+)["\']', line)
        if match:
            return match.group(1)
        
        # Look for subs=value (without quotes)
        match = re.search(r'subs\s*=\s*([^,\]]+)', line)
        if match:
            return match.group(1).strip()
        
        return None
    
    def _parse_subs_value(self, subs_value: str) -> list:
        """Parse the subs attribute value into a list of substitutions.
        
        Args:
            subs_value: Value like "attributes+", "replacements", "+replacements,-attributes"
            
        Returns:
            List of active substitution types
        """
        if not subs_value:
            return []
        
        # Handle special values
        if subs_value == 'normal':
            # Normal substitutions include replacements
            return ['specialcharacters', 'quotes', 'attributes', 'replacements', 'macros', 'post_replacements']
        elif subs_value == 'none':
            return []
        elif subs_value == 'verbatim':
            return ['specialcharacters']
        
        # For code blocks, default is no substitutions
        # We start with empty list and only add what's explicitly requested
        active_subs = []
        
        # Parse comma-separated list with +/- modifiers
        parts = [p.strip() for p in subs_value.split(',')]
        
        for part in parts:
            if not part:
                continue
                
            # Check for trailing + which means "add to defaults"
            # For code blocks, default is empty, so "attributes+" just adds attributes
            if part.endswith('+') and not part.startswith('+'):
                sub_type = part[:-1]  # Remove trailing +
                if sub_type and sub_type not in active_subs:
                    active_subs.append(sub_type)
            elif part.startswith('+'):
                # Explicit add with +prefix
                sub_type = part[1:]
                # Handle +normal specially - it adds all normal substitutions
                if sub_type == 'normal':
                    for normal_sub in ['specialcharacters', 'quotes', 'attributes', 'replacements', 'macros', 'post_replacements']:
                        if normal_sub not in active_subs:
                            active_subs.append(normal_sub)
                elif sub_type and sub_type not in active_subs:
                    active_subs.append(sub_type)
            elif part.startswith('-'):
                # Remove from existing
                sub_type = part[1:]
                if sub_type in active_subs:
                    active_subs.remove(sub_type)
            else:
                # No modifier - this replaces everything
                if part not in active_subs:
                    active_subs.append(part)
        
        return active_subs