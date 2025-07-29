"""Unit tests for the processor module."""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from aditi.processor import RuleProcessor, ProcessingResult, FileChange
from aditi.vale_parser import Violation, Severity
from aditi.config import AditiConfig
from aditi.rules import Fix, FixType


class TestProcessingResult:
    """Test the ProcessingResult dataclass."""
    
    def test_processing_result_properties(self):
        """Test ProcessingResult properties and methods."""
        result = ProcessingResult(
            violations_found=[
                Violation(Path("test.adoc"), "Rule1", 1, 1, "msg", Severity.ERROR, "text"),
                Violation(Path("test.adoc"), "Rule1", 2, 1, "msg", Severity.WARNING, "text"),
                Violation(Path("test2.adoc"), "Rule2", 1, 1, "msg", Severity.ERROR, "text"),
            ],
            fixes_applied=[Mock(spec=Fix), Mock(spec=Fix)],
            fixes_skipped=[Mock(spec=Fix)],
            files_processed={Path("test.adoc"), Path("test2.adoc")},
            files_modified={Path("test.adoc")},
            errors=["Error 1"]
        )
        
        assert result.total_violations == 3
        assert result.total_fixes_applied == 2
        assert result.total_fixes_available == 3  # applied + skipped
        
        # Test violations by severity
        by_severity = result.get_violations_by_severity()
        assert by_severity[Severity.ERROR] == 2
        assert by_severity[Severity.WARNING] == 1
        assert by_severity[Severity.SUGGESTION] == 0
        
        # Test violations by rule
        by_rule = result.get_violations_by_rule()
        assert by_rule["Rule1"] == 2
        assert by_rule["Rule2"] == 1


class TestRuleProcessor:
    """Test the RuleProcessor class."""
    
    @pytest.fixture
    def mock_vale_container(self):
        """Create a mock ValeContainer."""
        container = Mock()
        # Mock run_vale to return violations for the test file
        def mock_run_vale(args, project_root=None):
            # Filter out --output=JSON to get actual file paths
            file_paths = [arg for arg in args if not arg.startswith('--')]
            if file_paths:
                file_path = file_paths[0]
                return json.dumps({
                    file_path: {
                        "Alerts": [
                            {
                                "Check": "AsciiDocDITA.EntityReference",
                                "Line": 1,
                                "Column": 10,
                                "Message": "Replace '&nbsp;' with '{nbsp}'",
                                "Severity": "error",
                                "Match": "&nbsp;",
                                "Suggestions": ["{nbsp}"]
                            }
                        ]
                    }
                })
            return "{}"
        
        container.run_vale.side_effect = mock_run_vale
        # Also mock run_vale_raw for the new implementation
        container.run_vale_raw.side_effect = mock_run_vale
        return container
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock AditiConfig."""
        config = Mock(spec=AditiConfig)
        config.allowed_paths = []
        return config
    
    @pytest.fixture
    def processor(self, mock_vale_container, mock_config):
        """Create a RuleProcessor with mocks."""
        with patch('aditi.processor.RuleRegistry') as mock_registry_class:
            # Create a mock registry instance
            mock_registry = Mock()
            mock_registry.auto_discover.return_value = None
            mock_registry.get_rules_in_dependency_order.return_value = []
            mock_registry.get_rule_for_violation.return_value = None
            mock_registry_class.return_value = mock_registry
            
            processor = RuleProcessor(mock_vale_container, mock_config)
            # Ensure the mock registry is properly set
            processor.rule_registry = mock_registry
            return processor
    
    def test_process_files_dry_run(self, processor, mock_vale_container, tmp_path):
        """Test processing files in dry run mode."""
        # Create a test file with absolute path
        test_file = tmp_path / "test.adoc"
        test_file.write_text("Text with &nbsp; entity")
        # Convert to absolute path
        test_file = test_file.absolute()
        
        # Create a mock violation
        mock_violation = Violation(
            file_path=test_file,
            rule_name="EntityReference",
            line=1,
            column=11,
            message="Replace '&nbsp;' with '{nbsp}'",
            severity=Severity.ERROR,
            original_text="&nbsp;"
        )
        
        # Create a mock fix
        mock_fix = Fix(
            violation=mock_violation,
            replacement_text="{nbsp}",
            confidence=1.0
        )
        
        # Mock the rule
        mock_rule = Mock()
        mock_rule.name = "EntityReference"
        mock_rule.can_fix.return_value = True
        mock_rule.generate_fix.return_value = mock_fix
        
        processor.rule_registry.get_rules_in_dependency_order.return_value = [mock_rule]
        processor.rule_registry.get_rule_for_violation.return_value = mock_rule
        
        # Process files
        result = processor.process_files([test_file], dry_run=True)
        
        # Verify results
        assert result.total_violations == 1
        assert len(result.files_processed) == 1
        assert len(result.files_modified) == 0  # No modifications in dry run
        assert len(result.fixes_skipped) == 1  # Fixes are skipped in dry run
        assert len(result.fixes_applied) == 0
        
        # Verify Vale was called (using run_vale_raw now)
        mock_vale_container.run_vale_raw.assert_called_once()
    
    def test_process_files_with_fixes(self, processor, mock_vale_container, tmp_path):
        """Test processing files with actual fixes."""
        # Create a test file with absolute path
        test_file = tmp_path / "test.adoc"
        original_content = "Text with &nbsp; entity"
        test_file.write_text(original_content)
        # Convert to absolute path
        test_file = test_file.absolute()
        
        # Create a mock fix
        mock_violation = Violation(
            file_path=test_file,
            rule_name="EntityReference",
            line=1,
            column=11,
            message="Replace entity",
            severity=Severity.ERROR,
            original_text="&nbsp;"
        )
        
        mock_fix = Fix(
            violation=mock_violation,
            replacement_text="{nbsp}",
            confidence=1.0
        )
        
        # Mock the rule
        mock_rule = Mock()
        mock_rule.name = "EntityReference"
        mock_rule.can_fix.return_value = True
        mock_rule.generate_fix.return_value = mock_fix
        
        processor.rule_registry.get_rules_in_dependency_order.return_value = [mock_rule]
        processor.rule_registry.get_rule_for_violation.return_value = mock_rule
        
        # Process files (not dry run)
        result = processor.process_files([test_file], dry_run=False)
        
        # Verify results
        assert result.total_violations == 1
        assert len(result.files_processed) == 1
        assert len(result.files_modified) == 1
        assert len(result.fixes_applied) == 1
        assert len(result.fixes_skipped) == 0
        
        # Verify file was modified
        modified_content = test_file.read_text()
        assert "{nbsp}" in modified_content
        assert "&nbsp;" not in modified_content
    
    def test_run_vale_on_files(self, processor, mock_vale_container):
        """Test running Vale on files."""
        files = [Path("test1.adoc"), Path("test2.adoc")]
        mock_vale_container.run_vale_raw.return_value = '{"test": "output"}'
        
        output = processor._run_vale_on_files(files)
        
        assert output is not None
        assert "test1.adoc" in output  # Verify the mock response is returned
        mock_vale_container.run_vale_raw.assert_called_once_with(
            ["--output=JSON", "test1.adoc", "test2.adoc"],
            Path.cwd()
        )
    
    def test_run_vale_on_files_error(self, processor, mock_vale_container):
        """Test handling Vale execution errors."""
        mock_vale_container.run_vale_raw.side_effect = Exception("Vale error")
        
        output = processor._run_vale_on_files([Path("test.adoc")])
        
        assert output is None
    
    def test_create_backup_directory(self, processor):
        """Test creating backup directory."""
        backup_dir = processor._create_backup_directory()
        
        assert backup_dir.exists()
        assert "aditi-data/backups" in str(backup_dir)
        assert backup_dir.is_dir()
    
    def test_backup_file(self, processor, tmp_path):
        """Test backing up a file."""
        # Create a test file
        test_file = tmp_path / "test.adoc"
        test_file.write_text("Original content")
        
        # Set backup directory
        processor._backup_dir = tmp_path / "backup"
        processor._backup_dir.mkdir()
        
        # Backup the file
        with patch('pathlib.Path.cwd', return_value=tmp_path):
            success = processor._backup_file(test_file)
        
        assert success is True
        backup_file = processor._backup_dir / "test.adoc"
        assert backup_file.exists()
        assert backup_file.read_text() == "Original content"
    
    def test_display_summary(self, processor, capsys):
        """Test displaying processing summary."""
        # Create a result with various violations
        result = ProcessingResult(
            violations_found=[
                Violation(Path("test.adoc"), "EntityReference", 1, 1, "msg", Severity.ERROR, "text"),
                Violation(Path("test.adoc"), "ContentType", 1, 1, "msg", Severity.WARNING, "text"),
                Violation(Path("test2.adoc"), "TaskSection", 1, 1, "msg", Severity.SUGGESTION, "text"),
            ],
            fixes_applied=[],
            fixes_skipped=[Mock(spec=Fix), Mock(spec=Fix)],
            files_processed={Path("test.adoc"), Path("test2.adoc")},
            files_modified=set(),
            errors=[]
        )
        
        # Mock rules
        mock_entity_rule = Mock()
        mock_entity_rule.name = "EntityReference"
        mock_entity_rule.fix_type = FixType.FULLY_DETERMINISTIC
        
        mock_content_rule = Mock()
        mock_content_rule.name = "ContentType"
        mock_content_rule.fix_type = FixType.PARTIALLY_DETERMINISTIC
        
        mock_task_rule = Mock()
        mock_task_rule.name = "TaskSection"
        mock_task_rule.fix_type = FixType.NON_DETERMINISTIC
        
        processor.rule_registry.get_all_rules.return_value = [
            mock_entity_rule, mock_content_rule, mock_task_rule
        ]
        
        # Mock get_rule_for_violation to return appropriate rules
        def get_rule_for_violation(violation):
            if violation.rule_name == "EntityReference":
                return mock_entity_rule
            elif violation.rule_name == "ContentType":
                return mock_content_rule
            else:
                return None
                
        processor.rule_registry.get_rule_for_violation.side_effect = get_rule_for_violation
        
        # Display summary
        processor.display_summary(result)
        
        # Check output
        captured = capsys.readouterr()
        assert "Analysis Results" in captured.out
        assert "Files processed: 2" in captured.out
        assert "Total issues: 3" in captured.out
        assert "Can be auto-fixed: 2" in captured.out
        assert "67% of issues can be fixed automatically" in captured.out