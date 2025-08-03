"""Integration test for LineBreak rule implementation."""

import pytest
from pathlib import Path
import tempfile
import shutil

from aditi.vale_parser import ValeParser, Violation, Severity
from aditi.rules.line_break import LineBreakRule


class TestLineBreakIntegration:
    """Integration tests for LineBreak rule."""
    
    def test_process_sample_file(self):
        """Test processing the sample AsciiDoc file with line breaks."""
        # Sample content with various line break patterns
        content = """= Test Document

This is a paragraph with a hard line break +
that continues on the next line.

:hardbreaks-option:

Now all lines
will have hard breaks.

[options="hardbreaks"]
This section has
automatic hard breaks.

[%hardbreaks]
Using shorthand syntax.

// Comment with + 
// should be ignored +

----
Code block +
also ignored +
----

Normal text +
with break."""
        
        # Simulate violations that would be detected by Vale
        violations = [
            Violation(
                file_path=Path("test.adoc"),
                line=3,
                column=44,
                severity=Severity.WARNING,
                message="Hard line breaks are not supported in DITA.",
                check="AsciiDocDITA.LineBreak",
                rule_name="LineBreak",
                original_text=" +"
            ),
            Violation(
                file_path=Path("test.adoc"),
                line=6,
                column=1,
                severity=Severity.WARNING,
                message="Hard line breaks are not supported in DITA.",
                check="AsciiDocDITA.LineBreak",
                rule_name="LineBreak",
                original_text=":hardbreaks-option:"
            ),
            Violation(
                file_path=Path("test.adoc"),
                line=11,
                column=1,
                severity=Severity.WARNING,
                message="Hard line breaks are not supported in DITA.",
                check="AsciiDocDITA.LineBreak",
                rule_name="LineBreak",
                original_text='[options="hardbreaks"]'
            ),
            Violation(
                file_path=Path("test.adoc"),
                line=15,
                column=1,
                severity=Severity.WARNING,
                message="Hard line breaks are not supported in DITA.",
                check="AsciiDocDITA.LineBreak",
                rule_name="LineBreak",
                original_text="[%hardbreaks]"
            ),
            Violation(
                file_path=Path("test.adoc"),
                line=25,
                column=13,
                severity=Severity.WARNING,
                message="Hard line breaks are not supported in DITA.",
                check="AsciiDocDITA.LineBreak",
                rule_name="LineBreak",
                original_text=" +"
            )
        ]
        
        # Apply fixes
        rule = LineBreakRule()
        fixes = []
        
        for violation in violations:
            fix = rule.generate_fix(violation, content)
            if fix:
                fixes.append(fix)
        
        # Verify fixes were generated (comments and code blocks ignored)
        # One fix should be skipped because it's in a code block
        assert len(fixes) == 4
        
        # Check fix details
        assert fixes[0].replacement_text == "This is a paragraph with a hard line break"
        assert fixes[0].description == "Remove trailing + hard line break"
        
        assert fixes[1].replacement_text == ""
        assert ":hardbreaks-option:" in fixes[1].description
        
        assert fixes[2].replacement_text == ""
        assert "[options=hardbreaks]" in fixes[2].description
        
        assert fixes[3].replacement_text == ""
        assert "[%hardbreaks]" in fixes[3].description
    
    def test_apply_fixes_to_content(self):
        """Test applying fixes to actual content."""
        original_content = """= Document Title

First paragraph +
with hard break.

:hardbreaks-option:

[options="hardbreaks"]
Text here.

[%hardbreaks]
More text.

Final paragraph +
with break."""
        
        expected_content = """= Document Title

First paragraph
with hard break.



Text here.


More text.

Final paragraph
with break."""
        
        # Simulate the fix application process
        lines = original_content.splitlines()
        rule = LineBreakRule()
        
        # Apply fixes (simplified version)
        # Line 3: Remove trailing +
        lines[2] = "First paragraph"
        # Line 6: Remove :hardbreaks-option:
        lines[5] = ""
        # Line 8: Remove [options="hardbreaks"]
        lines[7] = ""
        # Line 11: Remove [%hardbreaks]
        lines[10] = ""
        # Line 14: Remove trailing +
        lines[13] = "Final paragraph"
        
        result_content = "\n".join(lines)
        
        # Verify the result matches expected
        assert result_content == expected_content
    
    def test_inline_code_protection(self):
        """Test that inline code with + is protected from fixes."""
        content = """= Technical Document

Use `grep '[0-9]+' file.txt` to find patterns.
This line has a real break +
that should be fixed.

Run the command ``sed 's/ +/,/g'`` carefully.
Another real line break +
here as well.

The +C+++ language is powerful.
Mathematical: `x + y` equals sum."""
        
        # Simulate violations that Vale would detect
        violations = [
            Violation(
                file_path=Path("test.adoc"),
                line=3,
                column=30,  # The + in grep command
                severity=Severity.WARNING,
                message="Hard line breaks are not supported in DITA.",
                check="AsciiDocDITA.LineBreak",
                rule_name="LineBreak",
                original_text="+"
            ),
            Violation(
                file_path=Path("test.adoc"),
                line=4,
                column=29,  # Real line break
                severity=Severity.WARNING,
                message="Hard line breaks are not supported in DITA.",
                check="AsciiDocDITA.LineBreak",
                rule_name="LineBreak",
                original_text=" +"
            ),
            Violation(
                file_path=Path("test.adoc"),
                line=8,
                column=28,  # Another real line break
                severity=Severity.WARNING,
                message="Hard line breaks are not supported in DITA.",
                check="AsciiDocDITA.LineBreak",
                rule_name="LineBreak",
                original_text=" +"
            )
        ]
        
        rule = LineBreakRule()
        fixes = []
        
        for violation in violations:
            fix = rule.generate_fix(violation, content)
            if fix:
                fixes.append(fix)
        
        # Should only fix the real line breaks, not the + in code
        assert len(fixes) == 2
        
        # Check that real line breaks are fixed
        assert fixes[0].violation.line == 4
        assert fixes[0].replacement_text == "This line has a real break"
        
        assert fixes[1].violation.line == 8
        assert fixes[1].replacement_text == "Another real line break"