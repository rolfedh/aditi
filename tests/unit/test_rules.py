"""Unit tests for rule framework and specific rules."""

import pytest
from pathlib import Path

from aditi.vale_parser import Violation, Severity
from aditi.rules import Rule, FixType, Fix, RuleRegistry
from aditi.rules.entity_reference import EntityReferenceRule
from aditi.rules.content_type import ContentTypeRule


class TestRuleFramework:
    """Test the rule framework base classes."""
    
    def test_fix_type_enum(self):
        """Test FixType enum values."""
        assert FixType.FULLY_DETERMINISTIC.value == "fully_deterministic"
        assert FixType.PARTIALLY_DETERMINISTIC.value == "partially_deterministic"
        assert FixType.NON_DETERMINISTIC.value == "non_deterministic"
    
    def test_fix_dataclass(self):
        """Test Fix dataclass."""
        violation = Violation(
            file_path=Path("test.adoc"),
            rule_name="TestRule",
            line=1,
            column=1,
            message="Test",
            severity=Severity.ERROR,
            original_text="old"
        )
        
        fix = Fix(
            violation=violation,
            replacement_text="new",
            confidence=0.9,
            requires_review=True,
            description="Test fix"
        )
        
        assert fix.violation == violation
        assert fix.replacement_text == "new"
        assert fix.confidence == 0.9
        assert fix.requires_review is True
        assert fix.description == "Test fix"
        assert fix.is_comment_flag is False
        
        # Test comment flag
        comment_fix = Fix(
            violation=violation,
            replacement_text="// TODO: Fix this",
            confidence=0.5
        )
        assert comment_fix.is_comment_flag is True


class TestEntityReferenceRule:
    """Test the EntityReference rule."""
    
    @pytest.fixture
    def rule(self):
        return EntityReferenceRule()
    
    def test_rule_properties(self, rule):
        """Test rule properties."""
        assert rule.name == "EntityReference"
        assert rule.fix_type == FixType.FULLY_DETERMINISTIC
        assert "entities" in rule.description.lower()
    
    def test_can_fix(self, rule):
        """Test can_fix method."""
        # Valid EntityReference violation
        violation = Violation(
            file_path=Path("test.adoc"),
            rule_name="EntityReference",
            line=1,
            column=1,
            message="Replace entity",
            severity=Severity.ERROR,
            original_text="&nbsp;"
        )
        assert rule.can_fix(violation) is True
        
        # Different rule
        violation.rule_name = "OtherRule"
        assert rule.can_fix(violation) is False
        
        # Unknown entity
        violation.rule_name = "EntityReference"
        violation.original_text = "&unknown;"
        assert rule.can_fix(violation) is False
    
    def test_generate_fix(self, rule):
        """Test generate_fix method."""
        file_content = "This has a&nbsp;space here."
        
        violation = Violation(
            file_path=Path("test.adoc"),
            rule_name="EntityReference",
            line=1,
            column=11,
            message="Replace entity",
            severity=Severity.ERROR,
            original_text="&nbsp;"
        )
        
        fix = rule.generate_fix(violation, file_content)
        
        assert fix is not None
        assert fix.replacement_text == "{nbsp}"
        assert fix.confidence == 1.0
        assert fix.requires_review is False
        assert "Replace '&nbsp;' with '{nbsp}'" in fix.description
    
    def test_validate_fix(self, rule):
        """Test validate_fix method."""
        violation = Violation(
            file_path=Path("test.adoc"),
            rule_name="EntityReference",
            line=1,
            column=1,
            message="Replace entity",
            severity=Severity.ERROR,
            original_text="&nbsp;"
        )
        
        fix = Fix(violation=violation, replacement_text="{nbsp}", confidence=1.0)
        
        # Normal content - should validate
        assert rule.validate_fix(fix, "Text with &nbsp; entity") is True
        
        # Inside code block - should not validate
        violation.line = 2
        assert rule.validate_fix(fix, "----\n&nbsp;\n----") is False
        
        # Inside inline code - should not validate
        violation.line = 1
        violation.column = 7
        assert rule.validate_fix(fix, "Text `&nbsp;` here") is False
    
    def test_entity_replacements(self, rule):
        """Test that common entities have replacements."""
        common_entities = [
            "&nbsp;", "&ndash;", "&mdash;", "&hellip;",
            "&ldquo;", "&rdquo;", "&trade;", "&reg;", "&copy;"
        ]
        
        for entity in common_entities:
            assert entity in rule.ENTITY_REPLACEMENTS
            assert rule.ENTITY_REPLACEMENTS[entity].startswith("{")
            assert rule.ENTITY_REPLACEMENTS[entity].endswith("}")


class TestContentTypeRule:
    """Test the ContentType rule."""
    
    @pytest.fixture
    def rule(self):
        return ContentTypeRule()
    
    def test_rule_properties(self, rule):
        """Test rule properties."""
        assert rule.name == "ContentType"
        assert rule.fix_type == FixType.PARTIALLY_DETERMINISTIC
        assert "content type" in rule.description.lower()
    
    def test_detect_content_type_from_filename(self, rule):
        """Test filename-based content type detection."""
        assert rule.detect_content_type_from_filename("assembly-guide.adoc") == "ASSEMBLY"
        assert rule.detect_content_type_from_filename("con-overview.adoc") == "CONCEPT"
        assert rule.detect_content_type_from_filename("concept-intro.adoc") == "CONCEPT"
        assert rule.detect_content_type_from_filename("proc-install.adoc") == "PROCEDURE"
        assert rule.detect_content_type_from_filename("procedure-setup.adoc") == "PROCEDURE"
        assert rule.detect_content_type_from_filename("ref-api.adoc") == "REFERENCE"
        assert rule.detect_content_type_from_filename("reference-guide.adoc") == "REFERENCE"
        assert rule.detect_content_type_from_filename("snip-example.adoc") == "SNIPPET"
        assert rule.detect_content_type_from_filename("unknown.adoc") is None
    
    def test_find_existing_attributes(self, rule):
        """Test finding existing content type attributes."""
        content = """
:_mod-docs-content-type: CONCEPT

= My Document

Some content here.
"""
        attributes = rule.find_existing_attributes(content)
        assert len(attributes) == 1
        assert attributes[0] == (2, ':_mod-docs-content-type:', 'CONCEPT')
        
        # Test with commented attribute
        content_commented = """
// :_mod-docs-content-type: PROCEDURE

= My Document
"""
        attributes = rule.find_existing_attributes(content_commented)
        assert len(attributes) == 1
        assert attributes[0] == (2, '// :_mod-docs-content-type:', 'PROCEDURE')
        
        # Test with deprecated attribute
        content_deprecated = """
:type: concept

= My Document
"""
        attributes = rule.find_existing_attributes(content_deprecated)
        assert len(attributes) == 1
        assert attributes[0][1] == "type"
        assert attributes[0][2] == "concept"
    
    def test_find_title_line(self, rule):
        """Test finding the title line."""
        content = """
Some intro text

= Main Title

Content here
"""
        assert rule.find_title_line(content) == 4
        
        # Test with level 2 title
        content_h2 = """
== Section Title
"""
        assert rule.find_title_line(content_h2) == 2
        
        # Test with no title
        assert rule.find_title_line("Just content") == 0
    
    def test_generate_fix_with_filename_detection(self, rule):
        """Test generating fix with filename detection."""
        file_content = """
= Installation Guide

This is how to install.
"""
        
        violation = Violation(
            file_path=Path("proc-install.adoc"),
            rule_name="ContentType",
            line=1,
            column=1,
            message="Missing content type",
            severity=Severity.WARNING,
            original_text=""
        )
        
        fix = rule.generate_fix(violation, file_content)
        
        assert fix is not None
        assert ":_mod-docs-content-type: PROCEDURE" in fix.replacement_text
        assert fix.confidence == 0.8
        assert fix.requires_review is True
        assert hasattr(fix, 'insert_at_line')
    
    def test_generate_fix_with_tbd(self, rule):
        """Test generating fix with TBD placeholder."""
        file_content = "= Unknown Document"
        
        violation = Violation(
            file_path=Path("unknown.adoc"),
            rule_name="ContentType",
            line=1,
            column=1,
            message="Missing content type",
            severity=Severity.WARNING,
            original_text=""
        )
        
        fix = rule.generate_fix(violation, file_content)
        
        assert fix is not None
        assert ":_mod-docs-content-type: TBD" in fix.replacement_text
        assert fix.confidence == 0.5
        assert "TBD placeholder" in fix.description


class TestRuleRegistry:
    """Test the RuleRegistry class."""
    
    def test_register_and_get_rule(self):
        """Test registering and retrieving rules."""
        registry = RuleRegistry()
        
        # Register a rule
        registry.register(EntityReferenceRule)
        
        # Get the rule
        rule = registry.get_rule("EntityReference")
        assert rule is not None
        assert isinstance(rule, EntityReferenceRule)
        
        # Try to get non-existent rule
        assert registry.get_rule("NonExistent") is None
    
    def test_get_rule_for_violation(self):
        """Test getting appropriate rule for a violation."""
        registry = RuleRegistry()
        registry.register(EntityReferenceRule)
        
        violation = Violation(
            file_path=Path("test.adoc"),
            rule_name="EntityReference",
            line=1,
            column=1,
            message="Test",
            severity=Severity.ERROR,
            original_text="&nbsp;"
        )
        
        rule = registry.get_rule_for_violation(violation)
        assert rule is not None
        assert isinstance(rule, EntityReferenceRule)
    
    def test_get_rules_in_dependency_order(self):
        """Test getting rules sorted by dependencies."""
        registry = RuleRegistry()
        registry.register(EntityReferenceRule)
        registry.register(ContentTypeRule)
        
        rules = registry.get_rules_in_dependency_order()
        assert len(rules) == 2
        
        # ContentType should come before EntityReference since it has no dependencies
        rule_names = [r.name for r in rules]
        assert rule_names.index("ContentType") < len(rule_names)