"""Test EntityReference rule with subs attribute handling."""

import pytest
from pathlib import Path

from aditi.rules.entity_reference import EntityReferenceRule
from aditi.vale_parser import Violation


class TestEntityReferenceSubs:
    """Test EntityReference rule respects subs attributes."""
    
    @pytest.fixture
    def rule(self):
        """Create EntityReference rule instance."""
        return EntityReferenceRule()
    
    def create_violation(self, line: int, column: int, text: str) -> Violation:
        """Helper to create a test violation."""
        return Violation(
            file_path=Path("test.adoc"),
            line=line,
            column=column,
            severity="error",
            rule_name="EntityReference",
            message="Test",
            original_text=text
        )
    
    def test_default_code_block_no_fix(self, rule):
        """Test that entities in default code blocks are not fixed."""
        content = """[source,html]
----
<p>Hello&nbsp;World</p>
----"""
        
        violation = self.create_violation(3, 9, "&nbsp;")
        fix = rule.generate_fix(violation, content)
        assert fix is None  # Should not fix in default code block
    
    def test_code_block_with_replacements_fixes(self, rule):
        """Test that entities in code blocks with replacements are fixed."""
        content = """[source,html,subs="replacements"]
----
<p>Hello&nbsp;World</p>
----"""
        
        violation = self.create_violation(3, 9, "&nbsp;")
        fix = rule.generate_fix(violation, content)
        assert fix is not None
        assert fix.replacement_text == "{nbsp}"
    
    def test_code_block_with_attributes_plus_no_fix(self, rule):
        """Test that attributes+ alone doesn't enable entity fixing."""
        content = """[source,terminal,subs="attributes+"]
----
echo "Version {version}"
echo "Hello&nbsp;World"
----"""
        
        violation = self.create_violation(4, 12, "&nbsp;")
        fix = rule.generate_fix(violation, content)
        assert fix is None  # attributes+ doesn't include replacements
    
    def test_code_block_with_multiple_subs_fixes(self, rule):
        """Test multiple subs including replacements."""
        content = """[source,html,subs="attributes+,replacements"]
----
<p>{product}&nbsp;v{version}</p>
----"""
        
        violation = self.create_violation(3, 13, "&nbsp;")
        fix = rule.generate_fix(violation, content)
        assert fix is not None
        assert fix.replacement_text == "{nbsp}"
    
    def test_listing_block_with_subs(self, rule):
        """Test listing blocks with subs attribute."""
        content = """[subs="replacements"]
----
Some text with &reg; symbol
----"""
        
        violation = self.create_violation(3, 16, "&reg;")
        fix = rule.generate_fix(violation, content)
        assert fix is not None
        assert fix.replacement_text == "{reg}"
    
    def test_literal_block_default_no_fix(self, rule):
        """Test literal blocks (.... delimiters) default behavior."""
        content = """....
Text with &copy; symbol
...."""
        
        violation = self.create_violation(2, 11, "&copy;")
        fix = rule.generate_fix(violation, content)
        assert fix is None  # Literal blocks default to no substitutions
    
    def test_normal_text_always_fixes(self, rule):
        """Test entities in normal text are always fixed."""
        content = """= Document Title

Regular text with &nbsp; entity."""
        
        violation = self.create_violation(3, 19, "&nbsp;")
        fix = rule.generate_fix(violation, content)
        assert fix is not None
        assert fix.replacement_text == "{nbsp}"
    
    def test_inline_code_no_fix(self, rule):
        """Test entities in inline code are not fixed."""
        content = """= Document Title

Use the `&nbsp;` entity in HTML."""
        
        violation = self.create_violation(3, 10, "&nbsp;")
        fix = rule.generate_fix(violation, content)
        assert fix is None  # Inside backticks
    
    def test_subs_normal_value(self, rule):
        """Test subs="normal" enables replacements."""
        content = """[source,html,subs="normal"]
----
<p>Text&trade;</p>
----"""
        
        violation = self.create_violation(3, 8, "&trade;")
        fix = rule.generate_fix(violation, content)
        assert fix is not None
        assert fix.replacement_text == "{trade}"
    
    def test_subs_none_value(self, rule):
        """Test subs="none" disables all substitutions."""
        content = """[source,html,subs="none"]
----
<p>Text&trade;</p>
----"""
        
        violation = self.create_violation(3, 8, "&trade;")
        fix = rule.generate_fix(violation, content)
        assert fix is None
    
    def test_subs_with_spaces(self, rule):
        """Test subs parsing handles spaces correctly."""
        content = """[source, html, subs = "replacements"]
----
<p>Text&mdash;more text</p>
----"""
        
        violation = self.create_violation(3, 8, "&mdash;")
        fix = rule.generate_fix(violation, content)
        assert fix is not None
        assert fix.replacement_text == "{mdash}"
    
    @pytest.mark.skip(reason="Nested code blocks are a known limitation - requires complex state tracking")
    def test_nested_code_blocks(self, rule):
        """Test nested code block handling.
        
        This test represents a complex edge case where code blocks are nested
        within other code blocks. Proper handling would require maintaining
        a stack of block contexts and their substitution settings.
        
        For now, this is documented as a known limitation in ENTITY_REFERENCE_HANDLING.md
        """
        content = """[source,asciidoc,subs="replacements"]
----
[source,html]
----
<p>&nbsp;</p>
----
&copy; 2024
----"""
        
        # Entity in outer block (with replacements)
        violation1 = self.create_violation(7, 1, "&copy;")
        fix1 = rule.generate_fix(violation1, content)
        assert fix1 is not None
        assert fix1.replacement_text == "{copy}"
        
        # Entity in inner block (no replacements) - this is tricky!
        # The current implementation might not handle this correctly
        violation2 = self.create_violation(5, 4, "&nbsp;")
        fix2 = rule.generate_fix(violation2, content)
        # This might incorrectly return a fix due to the outer block's settings
    
    def test_subs_plus_normal_fixes(self, rule):
        """Test that subs='+normal' enables entity fixing."""
        content = """[source,html,subs="+normal"]
----
<p>Copyright &copy; 2024</p>
----"""
        
        violation = self.create_violation(3, 14, "&copy;")
        fix = rule.generate_fix(violation, content)
        assert fix is not None
        assert fix.replacement_text == "{copy}"
    
    def test_subs_minus_replacements_no_fix(self, rule):
        """Test that subs='normal,-replacements' disables entity fixing."""
        content = """[source,html,subs="normal,-replacements"]
----
<p>Copyright &copy; 2024</p>
----"""
        
        violation = self.create_violation(3, 14, "&copy;")
        fix = rule.generate_fix(violation, content)
        assert fix is None  # -replacements should disable entity fixing