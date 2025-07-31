"""Unit tests for non-deterministic rules."""

import pytest
from pathlib import Path

from aditi.rules.example_block import ExampleBlockRule
from aditi.rules.nested_section import NestedSectionRule
from aditi.rules.task_example import TaskExampleRule
from aditi.rules.task_section import TaskSectionRule
from aditi.rules.short_description import ShortDescriptionRule
from aditi.rules.task_step import TaskStepRule
from aditi.rules.task_title import TaskTitleRule
from aditi.rules.task_duplicate import TaskDuplicateRule
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


class TestShortDescriptionRule:
    """Test the ShortDescription rule."""
    
    def test_rule_properties(self):
        """Test rule properties."""
        rule = ShortDescriptionRule()
        assert rule.name == "ShortDescription"
        assert rule.fix_type == FixType.NON_DETERMINISTIC
        assert "short description element" in rule.description
        assert rule.dependencies == []
    
    def test_can_fix(self):
        """Test can_fix method."""
        rule = ShortDescriptionRule()
        
        # Should fix ShortDescription violations
        violation = Violation(
            file_path=Path("test.adoc"),
            rule_name="ShortDescription",
            line=5,
            column=1,
            message="DITA topics require a short description element",
            severity=Severity.SUGGESTION,
            original_text="= Title"
        )
        assert rule.can_fix(violation) is True
        
        # Should not fix other violations
        violation.rule_name = "SomeOtherRule"
        assert rule.can_fix(violation) is False
    
    def test_generate_fix(self):
        """Test fix generation."""
        rule = ShortDescriptionRule()
        violation = Violation(
            file_path=Path("test.adoc"),
            rule_name="ShortDescription",
            line=5,
            column=1,
            message="DITA topics require a short description element",
            severity=Severity.SUGGESTION,
            original_text="= Title",
            check="AsciiDocDITA.ShortDescription"
        )
        
        fix = rule.generate_fix(violation, "dummy content")
        
        assert fix is not None
        assert fix.replacement_text == "// AsciiDocDITA.ShortDescription, suggestion, DITA topics require a short description element"
        assert fix.confidence == 1.0
        assert fix.requires_review is True
        assert fix.description == "Flag for manual review"


class TestTaskStepRule:
    """Test the TaskStep rule."""
    
    def test_rule_properties(self):
        """Test rule properties."""
        rule = TaskStepRule()
        assert rule.name == "TaskStep"
        assert rule.fix_type == FixType.NON_DETERMINISTIC
        assert "simple instructions" in rule.description
        assert rule.dependencies == ["ContentType"]
    
    def test_can_fix(self):
        """Test can_fix method."""
        rule = TaskStepRule()
        
        # Should fix TaskStep violations
        violation = Violation(
            file_path=Path("proc-test.adoc"),
            rule_name="TaskStep",
            line=25,
            column=1,
            message="Task steps should contain simple instructions",
            severity=Severity.SUGGESTION,
            original_text=". Complex step with multiple parts"
        )
        assert rule.can_fix(violation) is True
        
        # Should not fix other violations
        violation.rule_name = "SomeOtherRule"
        assert rule.can_fix(violation) is False
    
    def test_generate_fix(self):
        """Test fix generation."""
        rule = TaskStepRule()
        violation = Violation(
            file_path=Path("proc-test.adoc"),
            rule_name="TaskStep",
            line=25,
            column=1,
            message="Task steps should contain simple instructions",
            severity=Severity.SUGGESTION,
            original_text=". Complex step with multiple parts",
            check="AsciiDocDITA.TaskStep"
        )
        
        fix = rule.generate_fix(violation, "dummy content")
        
        assert fix is not None
        assert fix.replacement_text == "// AsciiDocDITA.TaskStep, suggestion, Task steps should contain simple instructions"
        assert fix.confidence == 1.0
        assert fix.requires_review is True
        assert fix.description == "Flag for manual review"


class TestTaskTitleRule:
    """Test the TaskTitle rule."""
    
    def test_rule_properties(self):
        """Test rule properties."""
        rule = TaskTitleRule()
        assert rule.name == "TaskTitle"
        assert rule.fix_type == FixType.NON_DETERMINISTIC
        assert "imperative verbs" in rule.description
        assert rule.dependencies == ["ContentType"]
    
    def test_can_fix(self):
        """Test can_fix method."""
        rule = TaskTitleRule()
        
        # Should fix TaskTitle violations
        violation = Violation(
            file_path=Path("proc-test.adoc"),
            rule_name="TaskTitle",
            line=1,
            column=1,
            message="Task titles should use imperative verbs",
            severity=Severity.SUGGESTION,
            original_text="= Installing Software"
        )
        assert rule.can_fix(violation) is True
        
        # Should not fix other violations
        violation.rule_name = "SomeOtherRule"
        assert rule.can_fix(violation) is False
    
    def test_generate_fix(self):
        """Test fix generation."""
        rule = TaskTitleRule()
        violation = Violation(
            file_path=Path("proc-test.adoc"),
            rule_name="TaskTitle",
            line=1,
            column=1,
            message="Task titles should use imperative verbs",
            severity=Severity.SUGGESTION,
            original_text="= Installing Software",
            check="AsciiDocDITA.TaskTitle"
        )
        
        fix = rule.generate_fix(violation, "dummy content")
        
        assert fix is not None
        assert fix.replacement_text == "// AsciiDocDITA.TaskTitle, suggestion, Task titles should use imperative verbs"
        assert fix.confidence == 1.0
        assert fix.requires_review is True
        assert fix.description == "Flag for manual review"


class TestTaskDuplicateRule:
    """Test the TaskDuplicate rule."""
    
    def test_rule_properties(self):
        """Test rule properties."""
        rule = TaskDuplicateRule()
        assert rule.name == "TaskDuplicate"
        assert rule.fix_type == FixType.NON_DETERMINISTIC
        assert "duplicate content" in rule.description
        assert rule.dependencies == ["ContentType"]
    
    def test_can_fix(self):
        """Test can_fix method."""
        rule = TaskDuplicateRule()
        
        # Should fix TaskDuplicate violations
        violation = Violation(
            file_path=Path("proc-test.adoc"),
            rule_name="TaskDuplicate",
            line=20,
            column=1,
            message="Task topics should avoid duplicate content",
            severity=Severity.SUGGESTION,
            original_text=". Repeated step"
        )
        assert rule.can_fix(violation) is True
        
        # Should not fix other violations
        violation.rule_name = "SomeOtherRule"
        assert rule.can_fix(violation) is False
    
    def test_generate_fix(self):
        """Test fix generation."""
        rule = TaskDuplicateRule()
        violation = Violation(
            file_path=Path("proc-test.adoc"),
            rule_name="TaskDuplicate",
            line=20,
            column=1,
            message="Task topics should avoid duplicate content",
            severity=Severity.SUGGESTION,
            original_text=". Repeated step",
            check="AsciiDocDITA.TaskDuplicate"
        )
        
        fix = rule.generate_fix(violation, "dummy content")
        
        assert fix is not None
        assert fix.replacement_text == "// AsciiDocDITA.TaskDuplicate, suggestion, Task topics should avoid duplicate content"
        assert fix.confidence == 1.0
        assert fix.requires_review is True
        assert fix.description == "Flag for manual review"