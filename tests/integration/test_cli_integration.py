"""Integration tests for CLI functionality."""

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from aditi.cli import app
from aditi.config import AditiConfig


class TestCLIIntegration:
    """Test CLI integration."""
    
    @pytest.fixture
    def runner(self):
        """Create CLI test runner."""
        return CliRunner()
    
    def test_help_command(self, runner):
        """Test help output."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "AsciiDoc DITA Integration" in result.stdout
        assert "init" in result.stdout
        assert "check" in result.stdout
        assert "fix" in result.stdout
        assert "journey" in result.stdout
    
    def test_version_command(self, runner):
        """Test version output."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        # Check that version output is present without hardcoding the version
        assert "aditi version" in result.stdout
        # Ensure it's not "unknown"
        assert "unknown" not in result.stdout.lower()
    
    @patch("aditi.cli.init_command")
    def test_init_command(self, mock_init, runner):
        """Test init command invocation."""
        # Mock init_command to not actually run Vale operations
        mock_init.return_value = None
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0
        mock_init.assert_called_once_with(None, False, False, False, False)
    
    @patch("aditi.commands.check.ConfigManager")
    def test_check_placeholder(self, mock_cm, runner):
        """Test check command without configuration."""
        # Mock empty configuration that returns empty allowed_paths
        config = AditiConfig()
        config.allowed_paths = []
        mock_cm.return_value.load_config.return_value = config
        result = runner.invoke(app, ["check"])
        assert result.exit_code == 1
        assert "No paths configured" in result.stdout
    
    @patch("aditi.commands.fix.ConfigManager")
    def test_fix_placeholder(self, mock_cm, runner):
        """Test fix command without configuration."""
        # Mock empty configuration that returns empty allowed_paths
        config = AditiConfig()
        config.allowed_paths = []
        mock_cm.return_value.load_config.return_value = config
        result = runner.invoke(app, ["fix"])
        assert result.exit_code == 1
        assert "No paths configured" in result.stdout
    
    @patch("questionary.confirm")
    @patch("aditi.commands.journey.ConfigManager")
    def test_journey_placeholder(self, mock_cm, mock_confirm, runner):
        """Test journey command exit on first prompt."""
        # Mock user saying no to first prompt
        mock_confirm.return_value.ask.return_value = False
        result = runner.invoke(app, ["journey"])
        assert result.exit_code == 1
    
    @patch("aditi.commands.fix.ConfigManager") 
    @patch("aditi.commands.check.ConfigManager")
    def test_verbose_option(self, mock_check_cm, mock_fix_cm, runner):
        """Test verbose option."""
        # Mock empty configuration for both commands
        config = AditiConfig()
        config.allowed_paths = []
        mock_check_cm.return_value.load_config.return_value = config
        mock_fix_cm.return_value.load_config.return_value = config
        
        result = runner.invoke(app, ["check", "--verbose"])
        assert result.exit_code == 1  # Still fails due to no paths, but accepts the option
        
        result = runner.invoke(app, ["fix", "-v"])
        assert result.exit_code == 1  # Still fails due to no paths, but accepts the option
    
    def test_no_args(self, runner):
        """Test running without arguments shows help."""
        result = runner.invoke(app, [])
        # With the callback implementation, we expect exit code 2
        # But if the implementation changes, accept 0 with help text
        if result.exit_code == 0:
            assert "Usage:" in result.stdout or "AsciiDoc DITA Integration" in result.stdout
        else:
            assert result.exit_code == 2
            assert "Usage:" in result.stdout or "AsciiDoc DITA Integration" in result.stdout