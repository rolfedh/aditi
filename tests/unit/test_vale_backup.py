"""Unit tests for Vale configuration backup functionality."""

import shutil
import tempfile
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from aditi.vale_container import ValeContainer


class TestValeBackup:
    """Test Vale configuration backup functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def vale_container(self):
        """Create a ValeContainer instance with mocked runtime check."""
        with patch.object(ValeContainer, '_check_runtime_available'):
            return ValeContainer(use_podman=True)
    
    def test_backup_creates_original_and_timestamped(self, vale_container, temp_dir):
        """Test that backup creates both original and timestamped backups."""
        # Create a test .vale.ini file
        vale_ini = temp_dir / ".vale.ini"
        vale_ini.write_text("# Original Vale config\nMinAlertLevel = suggestion\n")
        
        # Run backup
        vale_container._backup_vale_config(vale_ini)
        
        # Check original backup was created
        original_backup = temp_dir / ".vale.ini.original"
        assert original_backup.exists()
        assert original_backup.read_text() == "# Original Vale config\nMinAlertLevel = suggestion\n"
        
        # Check timestamped backup was created
        timestamped_backups = list(temp_dir.glob(".vale.ini.backup.*"))
        assert len(timestamped_backups) == 1
        assert timestamped_backups[0].read_text() == "# Original Vale config\nMinAlertLevel = suggestion\n"
    
    def test_backup_preserves_original(self, vale_container, temp_dir):
        """Test that original backup is never overwritten."""
        # Create a test .vale.ini file
        vale_ini = temp_dir / ".vale.ini"
        vale_ini.write_text("# Original config")
        
        # First backup
        vale_container._backup_vale_config(vale_ini)
        
        # Sleep to ensure different timestamp
        time.sleep(1.1)
        
        # Modify the file
        vale_ini.write_text("# Modified config")
        
        # Second backup
        vale_container._backup_vale_config(vale_ini)
        
        # Check original backup still has original content
        original_backup = temp_dir / ".vale.ini.original"
        assert original_backup.read_text() == "# Original config"
        
        # Check we have 2 timestamped backups
        timestamped_backups = list(temp_dir.glob(".vale.ini.backup.*"))
        assert len(timestamped_backups) == 2
    
    def test_cleanup_old_backups(self, vale_container, temp_dir):
        """Test that old timestamped backups are cleaned up."""
        # Create 8 timestamped backups
        for i in range(8):
            backup_file = temp_dir / f".vale.ini.backup.2025010{i}_120000"
            backup_file.write_text(f"Backup {i}")
        
        # Also create an original backup (should not be deleted)
        original = temp_dir / ".vale.ini.original"
        original.write_text("Original")
        
        # Run cleanup
        vale_container._cleanup_old_backups(temp_dir, keep_count=5)
        
        # Check that only 5 timestamped backups remain
        timestamped_backups = list(temp_dir.glob(".vale.ini.backup.*"))
        assert len(timestamped_backups) == 5
        
        # Check original backup still exists
        assert original.exists()
    
    def test_list_backups(self, vale_container, temp_dir):
        """Test listing available backups."""
        # Create some backups
        original = temp_dir / ".vale.ini.original"
        original.write_text("Original")
        
        backup1 = temp_dir / ".vale.ini.backup.20250101_120000"
        backup1.write_text("Backup 1")
        
        backup2 = temp_dir / ".vale.ini.backup.20250102_120000"
        backup2.write_text("Backup 2")
        
        # List backups
        backups = vale_container.list_backups(temp_dir)
        
        # Should have 3 backups (original + 2 timestamped)
        assert len(backups) == 3
        assert original in backups
        assert backup1 in backups
        assert backup2 in backups
    
    def test_restore_original_backup(self, vale_container, temp_dir):
        """Test restoring from original backup."""
        # Create current config and original backup
        vale_ini = temp_dir / ".vale.ini"
        vale_ini.write_text("# Current config")
        
        original = temp_dir / ".vale.ini.original"
        original.write_text("# Original config")
        
        # Restore
        result = vale_container.restore_backup(temp_dir)
        
        assert result is True
        assert vale_ini.read_text() == "# Original config"
        
        # Check that a pre-restore backup was created
        pre_restore_backups = list(temp_dir.glob(".vale.ini.before_restore.*"))
        assert len(pre_restore_backups) == 1
        assert pre_restore_backups[0].read_text() == "# Current config"
    
    def test_restore_specific_backup(self, vale_container, temp_dir):
        """Test restoring from a specific backup."""
        # Create current config and a backup
        vale_ini = temp_dir / ".vale.ini"
        vale_ini.write_text("# Current config")
        
        backup = temp_dir / ".vale.ini.backup.20250101_120000"
        backup.write_text("# Backup config")
        
        # Restore specific backup
        result = vale_container.restore_backup(temp_dir, ".vale.ini.backup.20250101_120000")
        
        assert result is True
        assert vale_ini.read_text() == "# Backup config"
    
    def test_restore_nonexistent_backup(self, vale_container, temp_dir):
        """Test restoring from nonexistent backup returns False."""
        result = vale_container.restore_backup(temp_dir, ".vale.ini.nonexistent")
        assert result is False
    
    def test_init_vale_config_with_force(self, vale_container, temp_dir):
        """Test that init_vale_config calls backup when force=True."""
        # Create existing config
        vale_ini = temp_dir / ".vale.ini"
        vale_ini.write_text("# Existing config")
        
        # Create a template file structure
        src_dir = temp_dir / "src"
        src_dir.mkdir()
        vale_dir = src_dir / "vale"
        vale_dir.mkdir()
        template_path = vale_dir / "vale_config_template.ini"
        template_path.write_text("# Aditi Vale config template")
        
        # Mock __file__ to point to our test directory and _run_vale_sync
        fake_file = str(src_dir / "vale_container.py")
        with patch('aditi.vale_container.__file__', fake_file), \
             patch.object(vale_container, '_run_vale_sync') as mock_sync:
            
            # Call init with force=True
            vale_container.init_vale_config(temp_dir, force=True)
            
            # Check backups were created
            assert (temp_dir / ".vale.ini.original").exists()
            assert len(list(temp_dir.glob(".vale.ini.backup.*"))) > 0
            
            # Check new config was written
            assert vale_ini.read_text() == "# Aditi Vale config template"
            
            # Check vale sync was called
            mock_sync.assert_called_once()