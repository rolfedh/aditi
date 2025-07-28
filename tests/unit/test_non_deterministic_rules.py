"""Unit tests for non-deterministic rules."""

import pytest
from pathlib import Path

from aditi.rules.example_block import ExampleBlockRule
from aditi.rules.nested_section import NestedSectionRule
from aditi.rules.task_example import TaskExampleRule
from aditi.rules.task_section import TaskSectionRule
from aditi.rules import FixType
from aditi.vale_parser import Violation, Severity


class TestExampleBlockRule:
    """Test the ExampleBlock rule."""
    
    def test_rule_properties(self):
        """Test rule properties."""
        rule = ExampleBlockRule()
        assert rule.name == "ExampleBlock"
        assert rule.fix_type == FixType.NON_DETERMINISTIC
        assert "main body" in rule.description
        assert rule.dependencies == []
    
    def test_can_fix(self):
        """Test can_fix method."""
        rule = ExampleBlockRule()
        
        # Should fix ExampleBlock violations
        violation = Violation(
            file_path=Path("test.adoc"),
            rule_name="ExampleBlock",
            line=10,
            column=1,
            message="Example blocks should be in the main body",
            severity=Severity.WARNING,
            original_text="===="
        )
        assert rule.can_fix(violation) is True
        
        # Should not fix other violations
        violation.rule_name = "SomeOtherRule"
        assert rule.can_fix(violation) is False
    
    def test_generate_fix(self):
        """Test fix generation."""
        rule = ExampleBlockRule()
        violation = Violation(
            file_path=Path("test.adoc"),
            rule_name="ExampleBlock",
            line=10,
            column=1,
            message="Example blocks should be in the main body",
            severity=Severity.WARNING,
            original_text="===="
        )
        
        fix = rule.generate_fix(violation, "dummy content")
        
        assert fix is not None
        assert fix.replacement_text == "// AsciiDocDITA Example blocks should be in the main body"
        assert fix.confidence == 1.0
        assert fix.requires_review is True
        assert fix.description == "Flag for manual review"


class TestNestedSectionRule:
    """Test the NestedSection rule."""
    
    def test_rule_properties(self):
        """Test rule properties."""
        rule = NestedSectionRule()
        assert rule.name == "NestedSection"
        assert rule.fix_type == FixType.NON_DETERMINISTIC
        assert "level 2 section" in rule.description
        assert rule.dependencies == []
    
    def test_can_fix(self):
        """Test can_fix method."""
        rule = NestedSectionRule()
        
        # Should fix NestedSection violations
        violation = Violation(
            file_path=Path("test.adoc"),
            rule_name="NestedSection",
            line=20,
            column=1,
            message="Nested sections should be moved to separate files",
            severity=Severity.WARNING,
            original_text="=== Nested Section"
        )
        assert rule.can_fix(violation) is True
        
        # Should not fix other violations
        violation.rule_name = "SomeOtherRule"
        assert rule.can_fix(violation) is False
    
    def test_generate_fix(self):
        """Test fix generation."""
        rule = NestedSectionRule()
        violation = Violation(
            file_path=Path("test.adoc"),
            rule_name="NestedSection",
            line=20,
            column=1,
            message="Nested sections should be moved to separate files",
            severity=Severity.WARNING,
            original_text="=== Nested Section"
        )
        
        fix = rule.generate_fix(violation, "dummy content")
        
        assert fix is not None
        assert fix.replacement_text == "// AsciiDocDITA Nested sections should be moved to separate files"
        assert fix.confidence == 1.0
        assert fix.requires_review is True


class TestTaskExampleRule:
    """Test the TaskExample rule."""
    
    def test_rule_properties(self):
        """Test rule properties."""
        rule = TaskExampleRule()
        assert rule.name == "TaskExample"
        assert rule.fix_type == FixType.NON_DETERMINISTIC
        assert "one <example> element" in rule.description
        assert rule.dependencies == ["ContentType"]
    
    def test_can_fix(self):
        """Test can_fix method."""
        rule = TaskExampleRule()
        
        # Should fix TaskExample violations
        violation = Violation(
            file_path=Path("proc-test.adoc"),
            rule_name="TaskExample",
            line=30,
            column=1,
            message="Task topics can only have one example",
            severity=Severity.SUGGESTION,
            original_text="===="
        )
        assert rule.can_fix(violation) is True
        
        # Should not fix other violations
        violation.rule_name = "SomeOtherRule"
        assert rule.can_fix(violation) is False
    
    def test_generate_fix(self):
        """Test fix generation."""
        rule = TaskExampleRule()
        violation = Violation(
            file_path=Path("proc-test.adoc"),
            rule_name="TaskExample",
            line=30,
            column=1,
            message="Task topics can only have one example",
            severity=Severity.SUGGESTION,
            original_text="===="
        )
        
        fix = rule.generate_fix(violation, "dummy content")
        
        assert fix is not None
        assert fix.replacement_text == "// AsciiDocDITA Task topics can only have one example"
        assert fix.confidence == 1.0
        assert fix.requires_review is True


class TestTaskSectionRule:
    """Test the TaskSection rule."""
    
    def test_rule_properties(self):
        """Test rule properties."""
        rule = TaskSectionRule()
        assert rule.name == "TaskSection"
        assert rule.fix_type == FixType.NON_DETERMINISTIC
        assert "does not allow sections" in rule.description
        assert rule.dependencies == ["ContentType"]
    
    def test_can_fix(self):
        """Test can_fix method."""
        rule = TaskSectionRule()
        
        # Should fix TaskSection violations
        violation = Violation(
            file_path=Path("proc-test.adoc"),
            rule_name="TaskSection",
            line=15,
            column=1,
            message="Task topics should not have sections",
            severity=Severity.SUGGESTION,
            original_text="== Section"
        )
        assert rule.can_fix(violation) is True
        
        # Should not fix other violations
        violation.rule_name = "SomeOtherRule"
        assert rule.can_fix(violation) is False
    
    def test_generate_fix(self):
        """Test fix generation."""
        rule = TaskSectionRule()
        violation = Violation(
            file_path=Path("proc-test.adoc"),
            rule_name="TaskSection",
            line=15,
            column=1,
            message="Task topics should not have sections",
            severity=Severity.SUGGESTION,
            original_text="== Section"
        )
        
        fix = rule.generate_fix(violation, "dummy content")
        
        assert fix is not None
        assert fix.replacement_text == "// AsciiDocDITA Task topics should not have sections"
        assert fix.confidence == 1.0
        assert fix.requires_review is True