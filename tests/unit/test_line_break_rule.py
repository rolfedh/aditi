"""Unit tests for the LineBreak rule."""

import pytest
from pathlib import Path

from aditi.rules.line_break import LineBreakRule
from aditi.rules.base import FixType
from aditi.vale_parser import Violation, Severity


class TestLineBreakRule:
    """Test cases for the LineBreak rule."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.rule = LineBreakRule()
    
    def test_rule_properties(self):
        """Test basic rule properties."""
        assert self.rule.name == "LineBreak"
        assert self.rule.fix_type == FixType.FULLY_DETERMINISTIC
        assert "hard line break" in self.rule.description.lower()
        assert self.rule.dependencies == []
    
    def test_can_fix(self):
        """Test can_fix method."""
        violation = Violation(
            file_path=Path("test.adoc"),
            line=5,
            column=10,
            severity=Severity.WARNING,
            message="Hard line breaks are not supported in DITA.",
            check="AsciiDocDITA.LineBreak",
            rule_name="LineBreak",
            original_text="text +"
        )
        assert self.rule.can_fix(violation) is True
        
        # Wrong rule name
        violation.rule_name = "SomeOtherRule"
        assert self.rule.can_fix(violation) is False
    
    def test_trailing_plus_fix(self):
        """Test fixing lines ending with space + plus sign."""
        content = """This is a line +
with a hard break.

Another line +  
with extra spaces."""
        
        violation = Violation(
            file_path=Path("test.adoc"),
            line=1,
            column=15,
            severity=Severity.WARNING,
            message="Hard line breaks are not supported in DITA.",
            check="AsciiDocDITA.LineBreak",
            rule_name="LineBreak",
            original_text=" +"
        )
        
        fix = self.rule.generate_fix(violation, content)
        assert fix is not None
        assert fix.replacement_text == "This is a line"
        assert fix.confidence == 0.95
        assert fix.requires_review is False
        assert "trailing +" in fix.description.lower()
    
    def test_hardbreaks_option_fix(self):
        """Test fixing :hardbreaks-option: attribute."""
        content = """= Title

:hardbreaks-option:

Some content here."""
        
        violation = Violation(
            file_path=Path("test.adoc"),
            line=3,
            column=1,
            severity=Severity.WARNING,
            message="Hard line breaks are not supported in DITA.",
            check="AsciiDocDITA.LineBreak",
            rule_name="LineBreak",
            original_text=":hardbreaks-option:"
        )
        
        fix = self.rule.generate_fix(violation, content)
        assert fix is not None
        assert fix.replacement_text == ""
        assert ":hardbreaks-option:" in fix.description
    
    def test_options_hardbreaks_fix(self):
        """Test fixing [options="hardbreaks"] attribute."""
        content = """[options="hardbreaks"]
This is text
with hard breaks."""
        
        violation = Violation(
            file_path=Path("test.adoc"),
            line=1,
            column=1,
            severity=Severity.WARNING,
            message="Hard line breaks are not supported in DITA.",
            check="AsciiDocDITA.LineBreak",
            rule_name="LineBreak",
            original_text='[options="hardbreaks"]'
        )
        
        fix = self.rule.generate_fix(violation, content)
        assert fix is not None
        assert fix.replacement_text == ""
        assert "[options=hardbreaks]" in fix.description
    
    def test_percent_hardbreaks_fix(self):
        """Test fixing [%hardbreaks] shorthand syntax."""
        content = """[%hardbreaks]
This is text
with hard breaks."""
        
        violation = Violation(
            file_path=Path("test.adoc"),
            line=1,
            column=1,
            severity=Severity.WARNING,
            message="Hard line breaks are not supported in DITA.",
            check="AsciiDocDITA.LineBreak",
            rule_name="LineBreak",
            original_text="[%hardbreaks]"
        )
        
        fix = self.rule.generate_fix(violation, content)
        assert fix is not None
        assert fix.replacement_text == ""
        assert "[%hardbreaks]" in fix.description
    
    def test_comment_ignored(self):
        """Test that line breaks in comments are ignored."""
        content = """// This is a comment +
// with a hard break +"""
        
        violation = Violation(
            file_path=Path("test.adoc"),
            line=1,
            column=20,
            severity=Severity.WARNING,
            message="Hard line breaks are not supported in DITA.",
            check="AsciiDocDITA.LineBreak",
            rule_name="LineBreak",
            original_text=" +"
        )
        
        fix = self.rule.generate_fix(violation, content)
        assert fix is None  # Should be ignored in comments
    
    def test_code_block_ignored(self):
        """Test that line breaks in code blocks are ignored."""
        content = """----
code with +
hard break +
----"""
        
        violation = Violation(
            file_path=Path("test.adoc"),
            line=2,
            column=10,
            severity=Severity.WARNING,
            message="Hard line breaks are not supported in DITA.",
            check="AsciiDocDITA.LineBreak",
            rule_name="LineBreak",
            original_text=" +"
        )
        
        fix = self.rule.generate_fix(violation, content)
        assert fix is None  # Should be ignored in code blocks
    
    def test_validate_fix(self):
        """Test fix validation."""
        content = ":hardbreaks-option:"
        
        from aditi.rules.base import Fix
        
        # Valid removal of attribute line
        fix = Fix(
            violation=Violation(
                file_path=Path("test.adoc"),
                line=1,
                column=1,
                severity=Severity.WARNING,
                message="Test",
                check="AsciiDocDITA.LineBreak",
                rule_name="LineBreak",
                original_text=":hardbreaks-option:"
            ),
            replacement_text="",
            confidence=0.95,
            requires_review=False
        )
        
        assert self.rule.validate_fix(fix, content) is True
        
        # Non-empty replacement should also be valid
        fix.replacement_text = "Some text"
        assert self.rule.validate_fix(fix, content) is True
    
    def test_options_variations(self):
        """Test different variations of options syntax."""
        variations = [
            '[options="hardbreaks"]',
            "[options='hardbreaks']",
            "[options=hardbreaks]"
        ]
        
        for option_syntax in variations:
            content = f"{option_syntax}\nSome text"
            
            violation = Violation(
                file_path=Path("test.adoc"),
                line=1,
                column=1,
                severity=Severity.WARNING,
                message="Hard line breaks are not supported in DITA.",
                check="AsciiDocDITA.LineBreak",
                rule_name="LineBreak",
                original_text=option_syntax
            )
            
            fix = self.rule.generate_fix(violation, content)
            assert fix is not None
            assert fix.replacement_text == ""
    
    def test_inline_code_with_plus(self):
        """Test that + inside inline code is not fixed."""
        content = """Use the command `grep '[0-9]+' file.txt` to find numbers.
Run `sed 's/[[:space:]]+/,/g'` to replace spaces.
The regex `[a-z]+` matches lowercase letters."""
        
        # Test first line with grep command
        violation = Violation(
            file_path=Path("test.adoc"),
            line=1,
            column=30,  # Position of + in grep command
            severity=Severity.WARNING,
            message="Hard line breaks are not supported in DITA.",
            check="AsciiDocDITA.LineBreak",
            rule_name="LineBreak",
            original_text="+"
        )
        
        fix = self.rule.generate_fix(violation, content)
        assert fix is None  # Should not fix + inside inline code
    
    def test_inline_code_double_backticks(self):
        """Test that + inside double backtick inline code is not fixed."""
        content = """Use ``command +`` for line continuation.
The pattern ``[0-9]+`` matches digits."""
        
        violation = Violation(
            file_path=Path("test.adoc"),
            line=1,
            column=15,  # Position of + in command
            severity=Severity.WARNING,
            message="Hard line breaks are not supported in DITA.",
            check="AsciiDocDITA.LineBreak",
            rule_name="LineBreak",
            original_text=" +"
        )
        
        fix = self.rule.generate_fix(violation, content)
        assert fix is None  # Should not fix + inside inline code
    
    def test_literal_passthrough_with_plus(self):
        """Test that + inside literal passthrough is not fixed."""
        content = """The symbol +text+ is literal.
Use +C+++ for the language."""
        
        violation = Violation(
            file_path=Path("test.adoc"),
            line=2,
            column=7,  # Position of + in C++
            severity=Severity.WARNING,
            message="Hard line breaks are not supported in DITA.",
            check="AsciiDocDITA.LineBreak",
            rule_name="LineBreak",
            original_text="+"
        )
        
        fix = self.rule.generate_fix(violation, content)
        assert fix is None  # Should not fix + inside literal passthrough
    
    def test_actual_line_break_not_in_code(self):
        """Test that actual line breaks outside code are fixed."""
        content = """This is regular text +
with a line break.
But `grep +` is a command."""
        
        violation = Violation(
            file_path=Path("test.adoc"),
            line=1,
            column=21,  # Position of + at end of line
            severity=Severity.WARNING,
            message="Hard line breaks are not supported in DITA.",
            check="AsciiDocDITA.LineBreak",
            rule_name="LineBreak",
            original_text=" +"
        )
        
        fix = self.rule.generate_fix(violation, content)
        assert fix is not None
        assert fix.replacement_text == "This is regular text"
        assert "trailing +" in fix.description.lower()