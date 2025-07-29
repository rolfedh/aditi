"""Integration tests for the check command."""

import pytest
from pathlib import Path
from typer.testing import CliRunner
from unittest.mock import Mock, patch

from aditi.cli import app
from aditi.config import AditiConfig, ConfigManager
from aditi.processor import ProcessingResult
from aditi.vale_parser import Violation, Severity


class TestCheckCommand:
    """Test the check command functionality."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()
    
    @pytest.fixture
    def mock_config(self, tmp_path):
        """Create a mock configuration."""
        config = AditiConfig()
        config.allowed_paths = [tmp_path / "docs"]
        return config
    
    @pytest.fixture
    def test_files(self, tmp_path):
        """Create test AsciiDoc files."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        
        # Create test files
        (docs_dir / "test1.adoc").write_text("= Test 1\n\nContent with &nbsp; entity.")
        (docs_dir / "test2.adoc").write_text("= Test 2\n\nAnother file.")
        
        return docs_dir
    
    def test_check_command_no_args_no_config(self, runner):
        """Test check command with no arguments and no configuration."""
        with patch('aditi.commands.check.ConfigManager') as mock_cm:
            mock_cm.return_value.load_config.return_value = AditiConfig()
            
            result = runner.invoke(app, ["check"])
            
            assert result.exit_code == 1
            assert "No paths configured" in result.output
    
    def test_check_command_with_path(self, runner, test_files, mock_config):
        """Test check command with explicit path."""
        with patch('aditi.commands.check.ConfigManager') as mock_cm, \
             patch('aditi.commands.check.ValeContainer') as mock_vc, \
             patch('aditi.commands.check.RuleProcessor') as mock_rp:
            
            # Setup mocks
            mock_cm.return_value.load_config.return_value = mock_config
            mock_vale = Mock()
            mock_vale.setup.return_value = True
            mock_vc.return_value = mock_vale
            
            # Mock processing result
            mock_result = ProcessingResult(
                violations_found=[
                    Violation(
                        test_files / "test1.adoc",
                        "EntityReference",
                        3, 14,
                        "Replace '&nbsp;' with '{nbsp}'",
                        Severity.ERROR,
                        "&nbsp;"
                    )
                ],
                fixes_applied=[],
                fixes_skipped=[Mock()],
                files_processed={test_files / "test1.adoc"},
                files_modified=set(),
                errors=[]
            )
            
            mock_processor = Mock()
            mock_processor.process_files.return_value = mock_result
            mock_rp.return_value = mock_processor
            
            # Run command
            result = runner.invoke(app, ["check", str(test_files)])
            
            assert result.exit_code == 0
            assert "Analyzing AsciiDoc files" in result.output
            
            # Verify Vale container was cleaned up
            mock_vale.cleanup.assert_called_once()
    
    def test_check_command_no_adoc_files(self, runner, tmp_path, mock_config):
        """Test check command when no .adoc files are found."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        
        with patch('aditi.commands.check.ConfigManager') as mock_cm:
            # Update mock config to allow the empty directory
            mock_config.allowed_paths = [empty_dir]
            mock_cm.return_value.load_config.return_value = mock_config
            
            result = runner.invoke(app, ["check", str(empty_dir)])
            
            assert result.exit_code == 0
            assert "No valid .adoc files found to check" in result.output
    
    def test_check_command_with_rule_filter(self, runner, test_files, mock_config):
        """Test check command with rule filter."""
        with patch('aditi.commands.check.ConfigManager') as mock_cm, \
             patch('aditi.commands.check.ValeContainer') as mock_vc, \
             patch('aditi.commands.check.RuleProcessor') as mock_rp:
            
            # Setup mocks
            mock_cm.return_value.load_config.return_value = mock_config
            mock_vale = Mock()
            mock_vale.setup.return_value = True
            mock_vc.return_value = mock_vale
            
            # Mock empty result
            mock_result = ProcessingResult(
                violations_found=[],
                fixes_applied=[],
                fixes_skipped=[],
                files_processed={test_files / "test1.adoc"},
                files_modified=set(),
                errors=[]
            )
            
            mock_processor = Mock()
            mock_processor.process_files.return_value = mock_result
            mock_rp.return_value = mock_processor
            
            # Run command with rule filter
            result = runner.invoke(app, ["check", str(test_files), "--rule", "EntityReference"])
            
            assert result.exit_code == 0
            assert "No issues found" in result.output
    
    def test_check_command_verbose_mode(self, runner, test_files, mock_config):
        """Test check command in verbose mode."""
        with patch('aditi.commands.check.ConfigManager') as mock_cm, \
             patch('aditi.commands.check.ValeContainer') as mock_vc, \
             patch('aditi.commands.check.RuleProcessor') as mock_rp:
            
            # Setup mocks
            mock_cm.return_value.load_config.return_value = mock_config
            mock_vale = Mock()
            mock_vale.setup.return_value = True
            mock_vc.return_value = mock_vale
            
            # Mock result with violations
            mock_result = ProcessingResult(
                violations_found=[
                    Violation(
                        test_files / "test1.adoc",
                        "EntityReference",
                        3, 14,
                        "Replace '&nbsp;' with '{nbsp}'",
                        Severity.ERROR,
                        "&nbsp;"
                    )
                ],
                fixes_applied=[],
                fixes_skipped=[],
                files_processed={test_files / "test1.adoc"},
                files_modified=set(),
                errors=[]
            )
            
            mock_processor = Mock()
            mock_processor.process_files.return_value = mock_result
            mock_processor.vale_parser.group_by_rule.return_value = {
                "EntityReference": mock_result.violations_found
            }
            mock_processor.rule_registry.get_all_rules.return_value = []
            mock_rp.return_value = mock_processor
            
            # Ensure the vale container mock has ensure_image_exists method
            mock_vale.ensure_image_exists.return_value = None
            
            # Run command in verbose mode
            # Patch Path.cwd() to return the test directory parent
            with patch('pathlib.Path.cwd', return_value=test_files.parent):
                result = runner.invoke(app, ["check", str(test_files), "--verbose"])
            
            assert result.exit_code == 0
            assert "Detailed Analysis Results" in result.output
    
    def test_check_command_with_errors(self, runner, test_files, mock_config):
        """Test check command when errors occur."""
        with patch('aditi.commands.check.ConfigManager') as mock_cm, \
             patch('aditi.commands.check.ValeContainer') as mock_vc, \
             patch('aditi.commands.check.RuleProcessor') as mock_rp:
            
            # Setup mocks
            mock_cm.return_value.load_config.return_value = mock_config
            mock_vale = Mock()
            mock_vale.setup.return_value = True
            mock_vc.return_value = mock_vale
            
            # Mock result with errors
            mock_result = ProcessingResult(
                violations_found=[],
                fixes_applied=[],
                fixes_skipped=[],
                files_processed=set(),
                files_modified=set(),
                errors=["Failed to parse file", "Another error"]
            )
            
            mock_processor = Mock()
            mock_processor.process_files.return_value = mock_result
            mock_rp.return_value = mock_processor
            
            # Run command
            result = runner.invoke(app, ["check", str(test_files)])
            
            assert result.exit_code == 0
            assert "Errors occurred during processing" in result.output
            assert "Failed to parse file" in result.output
    
    def test_check_command_vale_setup_failure(self, runner, test_files, mock_config):
        """Test check command when Vale setup fails."""
        with patch('aditi.commands.check.ConfigManager') as mock_cm, \
             patch('aditi.commands.check.ValeContainer') as mock_vc:
            
            # Setup mocks
            mock_cm.return_value.load_config.return_value = mock_config
            mock_vale = Mock()
            # Make ensure_image_exists raise an exception
            mock_vale.ensure_image_exists.side_effect = Exception("Failed to initialize Vale")
            mock_vc.return_value = mock_vale
            
            # Run command
            result = runner.invoke(app, ["check", str(test_files)])
            
            assert result.exit_code == 1
            assert "Failed to initialize Vale" in result.output