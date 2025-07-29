"""Unit tests for the journey command."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from aditi.commands.journey import (
    RULE_PROCESSING_ORDER,
    collect_adoc_files
)
from aditi.config import AditiConfig


class TestJourneyHelpers:
    """Test journey command helper functions."""
    
    def test_collect_adoc_files_with_allowed_paths(self):
        """Test collecting .adoc files from allowed paths."""
        config = AditiConfig()
        config.allowed_paths = [Path("/test/docs")]
        
        with patch("pathlib.Path.is_file") as mock_is_file:
            with patch("pathlib.Path.is_dir") as mock_is_dir:
                with patch("pathlib.Path.rglob") as mock_rglob:
                    mock_is_file.return_value = False
                    mock_is_dir.return_value = True
                    mock_rglob.return_value = [
                        Path("/test/docs/file1.adoc"),
                        Path("/test/docs/subdir/file2.adoc")
                    ]
                    
                    files = collect_adoc_files(config)
                    assert len(files) == 2
                    assert Path("/test/docs/file1.adoc") in files
    
    def test_collect_adoc_files_with_symlinks(self):
        """Test collecting .adoc files respecting symlink settings."""
        config = AditiConfig()
        config.allowed_paths = [Path("/test/docs")]
        config.ignore_symlinks = True
        
        mock_file1 = Mock(spec=Path)
        mock_file1.is_symlink.return_value = False
        mock_file2 = Mock(spec=Path)
        mock_file2.is_symlink.return_value = True
        
        with patch("pathlib.Path.is_file") as mock_is_file:
            with patch("pathlib.Path.is_dir") as mock_is_dir:
                with patch("pathlib.Path.rglob") as mock_rglob:
                    mock_is_file.return_value = False
                    mock_is_dir.return_value = True
                    mock_rglob.return_value = [mock_file1, mock_file2]
                    
                    files = collect_adoc_files(config)
                    assert len(files) == 1  # Only non-symlink file
    
    def test_collect_adoc_files_single_file(self):
        """Test collecting when path is a single .adoc file."""
        config = AditiConfig()
        config.allowed_paths = [Path("/test/file.adoc")]
        
        with patch("pathlib.Path.is_file") as mock_is_file:
            with patch("pathlib.Path.suffix", new_callable=lambda: ".adoc"):
                mock_is_file.return_value = True
                
                files = collect_adoc_files(config)
                assert len(files) == 1
                assert Path("/test/file.adoc") in files


class TestRuleProcessingOrder:
    """Test rule processing order configuration."""
    
    def test_rule_processing_order_structure(self):
        """Test that RULE_PROCESSING_ORDER is properly structured."""
        assert len(RULE_PROCESSING_ORDER) > 0
        
        # Check first rule is ContentType (prerequisite)
        assert RULE_PROCESSING_ORDER[0][0] == "ContentType"
        
        # Check all entries have correct structure
        for rule_name, severity, description in RULE_PROCESSING_ORDER:
            assert isinstance(rule_name, str)
            assert severity in ["error", "warning", "suggestion"]
            assert isinstance(description, str)
            assert len(description) > 0
    
    def test_rule_processing_order_coverage(self):
        """Test that all implemented rules are in processing order."""
        # List of all rules we've implemented
        expected_rules = {
            "ContentType", "EntityReference", "ExampleBlock", "NestedSection",
            "TaskSection", "TaskExample", "TaskStep", "TaskTitle", "TaskDuplicate",
            "ShortDescription", "AdmonitionTitle", "AuthorLine", "BlockTitle",
            "CrossReference", "DiscreteHeading", "EquationFormula", "LineBreak",
            "LinkAttribute", "PageBreak", "RelatedLinks", "SidebarBlock",
            "TableFooter", "ThematicBreak", "AttributeReference", "ConditionalCode",
            "IncludeDirective", "TagDirective"
        }
        
        # Get rules from processing order
        processing_rules = {rule[0] for rule in RULE_PROCESSING_ORDER}
        
        # Check all expected rules are present
        missing_rules = expected_rules - processing_rules
        assert len(missing_rules) == 0, f"Missing rules in RULE_PROCESSING_ORDER: {missing_rules}"


class TestJourneyCommand:
    """Test journey command integration points."""
    
    @patch("aditi.commands.journey.apply_rules_workflow")
    @patch("aditi.commands.journey.configure_repository")
    def test_journey_command_flow(self, mock_configure, mock_apply):
        """Test basic journey command flow."""
        # Import here to avoid circular imports
        from aditi.commands.journey import journey_command
        
        # Mock successful configuration
        mock_configure.return_value = True
        
        # Run command
        journey_command()
        
        # Verify workflow
        mock_configure.assert_called_once()
        mock_apply.assert_called_once()
    
    @patch("aditi.commands.journey.configure_repository")
    def test_journey_command_configuration_cancelled(self, mock_configure):
        """Test journey command when configuration is cancelled."""
        from aditi.commands.journey import journey_command
        
        # Mock cancelled configuration
        mock_configure.return_value = False
        
        # Run command
        journey_command()
        
        # Verify workflow stops
        mock_configure.assert_called_once()
    
    @patch("aditi.commands.journey.complete_journey")
    @patch("aditi.commands.journey.apply_rules_workflow")
    @patch("aditi.commands.journey.configure_repository")
    def test_journey_command_complete(self, mock_configure, mock_apply, mock_complete):
        """Test complete journey command execution."""
        from aditi.commands.journey import journey_command
        
        # Mock successful flow
        mock_configure.return_value = True
        
        # Run command
        journey_command()
        
        # Verify all steps called
        mock_configure.assert_called_once()
        mock_apply.assert_called_once()
        mock_complete.assert_called_once()