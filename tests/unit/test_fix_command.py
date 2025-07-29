"""Unit tests for the fix command."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typer import Exit

from aditi.config import AditiConfig
from aditi.vale_parser import Violation, Severity
from aditi.processor import ProcessingResult


class TestFixCommand:
    """Test the main fix command."""
    
    @patch("aditi.commands.fix.ConfigManager")
    def test_fix_command_no_paths_configured(self, mock_cm_class, capsys):
        """Test fix command when no paths are configured."""
        mock_cm = Mock()
        mock_config = AditiConfig()
        mock_config.allowed_paths = []
        mock_config.selected_directories = []
        mock_cm.load_config.return_value = mock_config
        mock_cm_class.return_value = mock_cm
        
        from aditi.commands.fix import fix_command
        
        with pytest.raises(Exit) as exc_info:
            fix_command()
        
        assert exc_info.value.exit_code == 1
        captured = capsys.readouterr()
        assert "No paths configured" in captured.out
    
    def test_fix_command_imports_successfully(self):
        """Test that fix command can be imported without errors."""
        from aditi.commands.fix import fix_command
        # Just test that the function exists and is callable
        assert callable(fix_command)
    
    @patch("aditi.commands.fix.ValeContainer")
    @patch("aditi.commands.fix.ConfigManager")
    def test_fix_command_no_adoc_files(self, mock_cm_class, mock_vale_class, capsys):
        """Test fix command when no .adoc files are found."""
        mock_cm = Mock()
        mock_config = AditiConfig()
        mock_config.allowed_paths = [Path("/test")]
        mock_config.selected_directories = []
        mock_cm.load_config.return_value = mock_config
        mock_cm_class.return_value = mock_cm
        
        mock_vale = Mock()
        mock_vale_class.return_value = mock_vale
        
        # Mock path operations to return no .adoc files
        with patch("pathlib.Path.is_file", return_value=False):
            with patch("pathlib.Path.is_dir", return_value=True):
                with patch("pathlib.Path.rglob", return_value=[]):
                    from aditi.commands.fix import fix_command
                    
                    with pytest.raises(Exit) as exc_info:
                        fix_command()
                    
                    assert exc_info.value.exit_code == 0
                    captured = capsys.readouterr()
                    assert "No .adoc files found" in captured.out


class TestFixCommandIntegration:
    """Test fix command integration scenarios."""
    
    def test_fix_command_has_expected_signature(self):
        """Test that fix command has the expected function signature."""
        from aditi.commands.fix import fix_command
        import inspect
        
        sig = inspect.signature(fix_command)
        param_names = list(sig.parameters.keys())
        
        # Check that expected parameters exist
        expected_params = ['paths', 'rule', 'interactive', 'dry_run']
        for param in expected_params:
            assert param in param_names