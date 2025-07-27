"""Integration tests for CLI functionality."""

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from aditi.cli import app


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
        assert "aditi version 0.1.0" in result.stdout
    
    @patch("aditi.commands.init.init_command")
    def test_init_command(self, mock_init, runner):
        """Test init command invocation."""
        # Mock init_command to not actually run Vale operations
        mock_init.return_value = None
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0
        mock_init.assert_called_once_with(None, False, False)
    
    def test_check_placeholder(self, runner):
        """Test check command placeholder."""
        result = runner.invoke(app, ["check"])
        assert result.exit_code == 1
        assert "not yet implemented" in result.stdout
    
    def test_fix_placeholder(self, runner):
        """Test fix command placeholder."""
        result = runner.invoke(app, ["fix"])
        assert result.exit_code == 1
        assert "not yet implemented" in result.stdout
    
    def test_journey_placeholder(self, runner):
        """Test journey command placeholder."""
        result = runner.invoke(app, ["journey"])
        assert result.exit_code == 1
        assert "not yet implemented" in result.stdout
    
    def test_verbose_option(self, runner):
        """Test verbose option."""
        result = runner.invoke(app, ["check", "--verbose"])
        assert result.exit_code == 1  # Still fails, but should accept the option
        
        result = runner.invoke(app, ["fix", "-v"])
        assert result.exit_code == 1  # Still fails, but should accept the option
    
    def test_no_args(self, runner):
        """Test running without arguments shows help."""
        result = runner.invoke(app, [])
        # Typer returns exit code 2 for missing command when no_args_is_help=True
        assert result.exit_code == 2
        assert "Usage:" in result.stdout