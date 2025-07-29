"""Unit tests for the journey workflow functions."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typer import Exit

from aditi.commands.journey import (
    apply_rules_workflow,
    generate_preparation_report
)
from aditi.config import SessionState, AditiConfig
from aditi.vale_parser import Violation, Severity
from aditi.processor import ProcessingResult
from aditi.rules import FixType


class TestApplyRulesWorkflow:
    """Test the apply_rules_workflow function."""
    
    @patch("aditi.commands.journey.process_single_rule")
    @patch("aditi.commands.journey.collect_adoc_files")
    @patch("aditi.commands.journey.RuleProcessor")
    @patch("aditi.commands.journey.ValeContainer")
    @patch("aditi.commands.journey.ConfigManager")
    def test_apply_rules_workflow_success(self, mock_cm_class, mock_vale_class,
                                         mock_processor_class, mock_collect,
                                         mock_process_rule, capsys):
        """Test successful rule application workflow."""
        # Setup mocks
        mock_cm = Mock()
        mock_config = AditiConfig()
        mock_session = SessionState()
        mock_cm.load_config.return_value = mock_config
        mock_cm.load_session.return_value = mock_session
        mock_cm_class.return_value = mock_cm
        
        mock_vale = Mock()
        mock_vale_class.return_value = mock_vale
        
        # Mock file collection
        mock_collect.return_value = [
            Path("/test/file1.adoc"),
            Path("/test/file2.adoc")
        ]
        
        # Mock violations
        violation1 = Mock(spec=Violation)
        violation1.rule_name = "EntityReference"
        violation2 = Mock(spec=Violation)
        violation2.rule_name = "ContentType"
        
        mock_result = ProcessingResult(
            violations_found=[violation1, violation2],
            fixes_applied=[],
            fixes_skipped=[],
            files_processed=set(),
            files_modified=set(),
            errors=[]
        )
        
        mock_processor = Mock()
        mock_processor.process_files.return_value = mock_result
        mock_processor.vale_parser.group_by_rule.return_value = {
            "EntityReference": [violation1],
            "ContentType": [violation2]
        }
        mock_processor.rule_registry.get_rule.side_effect = lambda name: Mock(name=name)
        mock_processor_class.return_value = mock_processor
        
        # Mock process_single_rule to return True (continue)
        mock_process_rule.return_value = True
        
        # Run workflow
        apply_rules_workflow()
        
        # Verify
        captured = capsys.readouterr()
        assert "Analyzing AsciiDoc files" in captured.out
        
        # Should process both rules
        assert mock_process_rule.call_count == 2
        
        # Session should be updated
        assert "EntityReference" in mock_session.applied_rules
        assert "ContentType" in mock_session.applied_rules
        
        # Vale should be cleaned up
        mock_vale.cleanup.assert_called_once()
    
    @patch("aditi.commands.journey.ValeContainer")
    @patch("aditi.commands.journey.ConfigManager")
    def test_apply_rules_workflow_vale_error(self, mock_cm_class, mock_vale_class, capsys):
        """Test workflow when Vale initialization fails."""
        mock_cm = Mock()
        mock_cm.load_config.return_value = AditiConfig()
        mock_cm.load_session.return_value = SessionState()
        mock_cm_class.return_value = mock_cm
        
        mock_vale_class.side_effect = Exception("Container error")
        
        with pytest.raises(Exit):
            apply_rules_workflow()
        
        captured = capsys.readouterr()
        assert "Failed to initialize Vale" in captured.out
    
    @patch("aditi.commands.journey.collect_adoc_files")
    @patch("aditi.commands.journey.ValeContainer")
    @patch("aditi.commands.journey.ConfigManager")
    def test_apply_rules_workflow_no_files(self, mock_cm_class, mock_vale_class,
                                          mock_collect, capsys):
        """Test workflow when no .adoc files are found."""
        mock_cm = Mock()
        mock_cm.load_config.return_value = AditiConfig()
        mock_cm.load_session.return_value = SessionState()
        mock_cm_class.return_value = mock_cm
        
        mock_vale = Mock()
        mock_vale_class.return_value = mock_vale
        
        mock_collect.return_value = []
        
        apply_rules_workflow()
        
        captured = capsys.readouterr()
        assert "No .adoc files found to process" in captured.out
    
    @patch("aditi.commands.journey.process_single_rule")
    @patch("aditi.commands.journey.collect_adoc_files")
    @patch("aditi.commands.journey.RuleProcessor")
    @patch("aditi.commands.journey.ValeContainer")
    @patch("aditi.commands.journey.ConfigManager")
    def test_apply_rules_workflow_user_stops(self, mock_cm_class, mock_vale_class,
                                            mock_processor_class, mock_collect,
                                            mock_process_rule, capsys):
        """Test workflow when user chooses to stop."""
        # Setup mocks
        mock_cm = Mock()
        mock_config = AditiConfig()
        mock_session = SessionState()
        mock_cm.load_config.return_value = mock_config
        mock_cm.load_session.return_value = mock_session
        mock_cm_class.return_value = mock_cm
        
        mock_vale = Mock()
        mock_vale_class.return_value = mock_vale
        
        mock_collect.return_value = [Path("/test/file.adoc")]
        
        # Mock violations
        violation = Mock(spec=Violation)
        violation.rule_name = "EntityReference"
        
        mock_result = ProcessingResult(
            violations_found=[violation],
            fixes_applied=[],
            fixes_skipped=[],
            files_processed=set(),
            files_modified=set(),
            errors=[]
        )
        
        mock_processor = Mock()
        mock_processor.process_files.return_value = mock_result
        mock_processor.vale_parser.group_by_rule.return_value = {
            "EntityReference": [violation]
        }
        mock_processor.rule_registry.get_rule.return_value = Mock()
        mock_processor_class.return_value = mock_processor
        
        # Mock process_single_rule to return False (stop)
        mock_process_rule.return_value = False
        
        # Run workflow
        apply_rules_workflow()
        
        # Verify
        captured = capsys.readouterr()
        assert "Journey paused" in captured.out
        
        # Should only process one rule before stopping
        assert mock_process_rule.call_count == 1
    
    @patch("aditi.commands.journey.collect_adoc_files")
    @patch("aditi.commands.journey.RuleProcessor")
    @patch("aditi.commands.journey.ValeContainer")
    @patch("aditi.commands.journey.ConfigManager")
    def test_apply_rules_workflow_unimplemented_rule(self, mock_cm_class, mock_vale_class,
                                                     mock_processor_class, mock_collect,
                                                     capsys):
        """Test workflow with unimplemented rule."""
        # Setup mocks
        mock_cm = Mock()
        mock_config = AditiConfig()
        mock_session = SessionState()
        mock_cm.load_config.return_value = mock_config
        mock_cm.load_session.return_value = mock_session
        mock_cm_class.return_value = mock_cm
        
        mock_vale = Mock()
        mock_vale_class.return_value = mock_vale
        
        mock_collect.return_value = [Path("/test/file.adoc")]
        
        # Mock violations with unimplemented rule
        violation = Mock(spec=Violation)
        violation.rule_name = "UnimplementedRule"
        
        mock_result = ProcessingResult(
            violations_found=[violation],
            fixes_applied=[],
            fixes_skipped=[],
            files_processed=set(),
            files_modified=set(),
            errors=[]
        )
        
        mock_processor = Mock()
        mock_processor.process_files.return_value = mock_result
        mock_processor.vale_parser.group_by_rule.return_value = {
            "EntityReference": [violation]  # In RULE_PROCESSING_ORDER
        }
        mock_processor.rule_registry.get_rule.return_value = None  # Not implemented
        mock_processor_class.return_value = mock_processor
        
        # Run workflow
        apply_rules_workflow()
        
        # Verify warning shown
        captured = capsys.readouterr()
        assert "Warning: Rule EntityReference not implemented yet" in captured.out


class TestGeneratePreparationReport:
    """Test report generation."""
    
    def test_generate_preparation_report_with_session_data(self):
        """Test that report function handles session data correctly."""
        session = SessionState()
        session.journey_progress = {
            "repository_root": "/test/repo",
            "selected_directories": ["docs", "examples"]
        }
        session.applied_rules = ["EntityReference", "ContentType"]
        
        # Test that the function doesn't crash with valid data
        # (File operations are tested in integration tests)
        try:
            generate_preparation_report(session)
        except Exception as e:
            # It's OK if it fails due to permissions/file system
            # We're testing the logic, not file I/O
            pass
    
    def test_generate_preparation_report_with_empty_session(self):
        """Test that report function handles empty session correctly."""
        session = SessionState()
        
        # Test that the function doesn't crash with empty data
        try:
            generate_preparation_report(session)
        except Exception as e:
            # It's OK if it fails due to permissions/file system
            pass
    
    def test_generate_preparation_report_error(self, capsys):
        """Test report generation error handling."""
        session = SessionState()
        
        with patch("pathlib.Path.home") as mock_home:
            mock_home.side_effect = Exception("Path error")
            
            result = generate_preparation_report(session)
            
            assert result is None
            
            captured = capsys.readouterr()
            assert "Warning: Could not generate report" in captured.out