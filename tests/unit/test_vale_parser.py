"""Unit tests for vale_parser module."""

import json
import pytest
from pathlib import Path

from aditi.vale_parser import ValeParser, Violation, Severity


class TestValeParser:
    """Test the ValeParser class."""
    
    @pytest.fixture
    def sample_vale_output(self):
        """Sample Vale JSON output for testing."""
        return json.dumps({
            "docs/test.adoc": {
                "Alerts": [
                    {
                        "Check": "AsciiDocDITA.EntityReference",
                        "Line": 15,
                        "Column": 23,
                        "Message": "Replace '&nbsp;' with '{nbsp}'",
                        "Severity": "error",
                        "Match": "&nbsp;",
                        "Suggestions": ["{nbsp}"],
                        "Link": "https://example.com/entity-reference"
                    },
                    {
                        "Check": "AsciiDocDITA.ContentType",
                        "Line": 1,
                        "Column": 1,
                        "Message": "Missing content type attribute",
                        "Severity": "warning",
                        "Match": "",
                        "Suggestions": []
                    }
                ]
            },
            "docs/another.adoc": {
                "Alerts": [
                    {
                        "Check": "AsciiDocDITA.TaskSection",
                        "Line": 34,
                        "Column": 1,
                        "Message": "Task sections must use numbered lists",
                        "Severity": "suggestion",
                        "Match": "== Prerequisites",
                        "Suggestions": []
                    }
                ]
            }
        })
    
    def test_parse_json_output(self, sample_vale_output):
        """Test parsing Vale JSON output."""
        parser = ValeParser()
        violations = parser.parse_json_output(sample_vale_output)
        
        assert len(violations) == 3
        
        # Check first violation
        v1 = violations[0]
        assert v1.file_path == Path("docs/test.adoc")
        assert v1.rule_name == "EntityReference"
        assert v1.line == 15
        assert v1.column == 23
        assert v1.message == "Replace '&nbsp;' with '{nbsp}'"
        assert v1.severity == Severity.ERROR
        assert v1.original_text == "&nbsp;"
        assert v1.suggested_fix == "{nbsp}"
        assert v1.check == "AsciiDocDITA.EntityReference"
        
        # Check second violation
        v2 = violations[1]
        assert v2.rule_name == "ContentType"
        assert v2.severity == Severity.WARNING
        
        # Check third violation
        v3 = violations[2]
        assert v3.file_path == Path("docs/another.adoc")
        assert v3.rule_name == "TaskSection"
        assert v3.severity == Severity.SUGGESTION
    
    def test_parse_invalid_json(self):
        """Test handling of invalid JSON."""
        parser = ValeParser()
        
        with pytest.raises(json.JSONDecodeError):
            parser.parse_json_output("invalid json {")
    
    def test_parse_empty_output(self):
        """Test parsing empty Vale output."""
        parser = ValeParser()
        violations = parser.parse_json_output("{}")
        
        assert len(violations) == 0
    
    def test_group_by_file(self, sample_vale_output):
        """Test grouping violations by file."""
        parser = ValeParser()
        violations = parser.parse_json_output(sample_vale_output)
        grouped = parser.group_by_file(violations)
        
        assert len(grouped) == 2
        assert Path("docs/test.adoc") in grouped
        assert Path("docs/another.adoc") in grouped
        assert len(grouped[Path("docs/test.adoc")]) == 2
        assert len(grouped[Path("docs/another.adoc")]) == 1
    
    def test_group_by_rule(self, sample_vale_output):
        """Test grouping violations by rule."""
        parser = ValeParser()
        violations = parser.parse_json_output(sample_vale_output)
        grouped = parser.group_by_rule(violations)
        
        assert len(grouped) == 3
        assert "EntityReference" in grouped
        assert "ContentType" in grouped
        assert "TaskSection" in grouped
        assert len(grouped["EntityReference"]) == 1
        assert len(grouped["ContentType"]) == 1
        assert len(grouped["TaskSection"]) == 1
    
    def test_filter_by_severity(self, sample_vale_output):
        """Test filtering violations by severity."""
        parser = ValeParser()
        violations = parser.parse_json_output(sample_vale_output)
        
        errors = parser.filter_by_severity(violations, Severity.ERROR)
        warnings = parser.filter_by_severity(violations, Severity.WARNING)
        suggestions = parser.filter_by_severity(violations, Severity.SUGGESTION)
        
        assert len(errors) == 1
        assert len(warnings) == 1
        assert len(suggestions) == 1
    
    def test_get_statistics(self, sample_vale_output):
        """Test getting violation statistics."""
        parser = ValeParser()
        violations = parser.parse_json_output(sample_vale_output)
        stats = parser.get_statistics(violations)
        
        assert stats["total"] == 3
        assert stats["by_severity"][Severity.ERROR.value] == 1
        assert stats["by_severity"][Severity.WARNING.value] == 1
        assert stats["by_severity"][Severity.SUGGESTION.value] == 1
        assert stats["files_affected"] == 2
        assert stats["by_rule"]["EntityReference"] == 1
        assert stats["by_rule"]["ContentType"] == 1
        assert stats["by_rule"]["TaskSection"] == 1
    
    def test_violation_from_vale_alert(self):
        """Test creating a Violation from a Vale alert."""
        alert = {
            "Check": "AsciiDocDITA.EntityReference",
            "Line": 10,
            "Column": 5,
            "Message": "Test message",
            "Severity": "error",
            "Match": "&test;",
            "Suggestions": ["{test}"],
            "Link": "https://example.com"
        }
        
        violation = Violation.from_vale_alert(Path("test.adoc"), alert)
        
        assert violation.file_path == Path("test.adoc")
        assert violation.rule_name == "EntityReference"
        assert violation.line == 10
        assert violation.column == 5
        assert violation.message == "Test message"
        assert violation.severity == Severity.ERROR
        assert violation.original_text == "&test;"
        assert violation.suggested_fix == "{test}"
        assert violation.check == "AsciiDocDITA.EntityReference"
        assert violation.link == "https://example.com"