"""Unit tests for local configuration management."""

import json
import tempfile
from pathlib import Path
import pytest

from aditi.local_config import LocalConfigManager
from aditi.config import AditiConfig, RepositoryConfig


class TestLocalConfigManager:
    """Test cases for LocalConfigManager."""
    
    def test_find_repository_root(self, tmp_path):
        """Test finding repository root."""
        # Create a git repository structure
        repo_root = tmp_path / "my-repo"
        repo_root.mkdir()
        (repo_root / ".git").mkdir()
        
        # Create a subdirectory
        subdir = repo_root / "docs" / "guides"
        subdir.mkdir(parents=True)
        
        # Test from subdirectory
        manager = LocalConfigManager(start_path=subdir)
        found_root = manager.find_repository_root()
        assert found_root == repo_root
        
        # Test from non-repo directory
        non_repo = tmp_path / "not-a-repo"
        non_repo.mkdir()
        manager = LocalConfigManager(start_path=non_repo)
        assert manager.find_repository_root() is None
    
    def test_init_local_config(self, tmp_path):
        """Test initializing local configuration."""
        # Create a repository
        repo_root = tmp_path / "test-repo"
        repo_root.mkdir()
        (repo_root / ".git").mkdir()
        
        manager = LocalConfigManager(start_path=repo_root)
        
        # Initialize config
        config_dir, config = manager.init_local_config()
        
        # Check directory was created
        assert config_dir == repo_root / ".aditi"
        assert config_dir.exists()
        assert (config_dir / "config.json").exists()
        
        # Check config content
        assert len(config.repositories) == 1
        assert "test-repo" in config.repositories
        assert config.repositories["test-repo"].root == repo_root
        assert config.current_repository == "test-repo"
        
        # Check .gitignore was updated
        gitignore = repo_root / ".gitignore"
        assert gitignore.exists()
        content = gitignore.read_text()
        assert ".aditi/session.json" in content
    
    def test_load_config_local(self, tmp_path):
        """Test loading local configuration."""
        # Create repo with .aditi directory
        repo_root = tmp_path / "local-repo"
        repo_root.mkdir()
        aditi_dir = repo_root / ".aditi"
        aditi_dir.mkdir()
        
        # Create config
        config_data = {
            "version": "1.0",
            "repositories": {
                "local-repo": {
                    "root": str(repo_root),
                    "default_branch": "main",
                    "subdirectory_permissions": [],
                    "feature_branch_prefix": "aditi/"
                }
            },
            "current_repository": "local-repo"
        }
        
        config_file = aditi_dir / "config.json"
        config_file.write_text(json.dumps(config_data, indent=2))
        
        # Load config
        manager = LocalConfigManager(start_path=repo_root)
        config = manager.load_config()
        
        assert config.current_repository == "local-repo"
        assert len(config.repositories) == 1
        assert "local-repo" in config.repositories
    
    def test_load_config_no_migration(self, tmp_path):
        """Test that load_config doesn't automatically migrate."""
        # Create global config directory
        global_dir = tmp_path / "aditi-data"
        global_dir.mkdir()
        
        # Create repository
        repo_root = tmp_path / "no-auto-migrate"
        repo_root.mkdir()
        
        # Create global config with this repo
        global_config = {
            "version": "1.0",
            "repositories": {
                "no-auto-migrate": {
                    "root": str(repo_root),
                    "default_branch": "main",
                    "subdirectory_permissions": [],
                    "feature_branch_prefix": "aditi/"
                }
            }
        }
        
        (global_dir / "config.json").write_text(json.dumps(global_config, indent=2))
        
        # Create manager with mocked global dir
        manager = LocalConfigManager(start_path=repo_root)
        manager.global_config_dir = global_dir
        
        # Load config should NOT trigger migration
        config = manager.load_config()
        
        # Should get empty config, not migrated one
        assert not manager.has_local_config()
        assert len(config.repositories) == 0
        assert config.current_repository is None
    
    def test_has_local_config(self, tmp_path):
        """Test checking for local configuration."""
        # Without .aditi directory
        repo_root = tmp_path / "no-config"
        repo_root.mkdir()
        manager = LocalConfigManager(start_path=repo_root)
        assert not manager.has_local_config()
        
        # With .aditi directory
        repo_with_config = tmp_path / "with-config"
        repo_with_config.mkdir()
        (repo_with_config / ".aditi").mkdir()
        manager = LocalConfigManager(start_path=repo_with_config)
        assert manager.has_local_config()
    
    def test_can_migrate_from_global(self, tmp_path):
        """Test checking if migration from global is possible."""
        # Create global config directory
        global_dir = tmp_path / "aditi-data"
        global_dir.mkdir()
        
        # Create repository
        repo_root = tmp_path / "migrate-repo"
        repo_root.mkdir()
        (repo_root / ".git").mkdir()
        
        # Create global config with this repo
        global_config = {
            "version": "1.0",
            "repositories": {
                "migrate-repo": {
                    "root": str(repo_root),
                    "default_branch": "develop",
                    "subdirectory_permissions": [],
                    "feature_branch_prefix": "feature/"
                }
            },
            "current_repository": "migrate-repo",
            "allowed_paths": [str(repo_root / "docs")]
        }
        
        (global_dir / "config.json").write_text(json.dumps(global_config, indent=2))
        
        # Create manager with mocked global dir
        manager = LocalConfigManager(start_path=repo_root)
        manager.global_config_dir = global_dir
        
        # Check migration is possible
        assert manager.can_migrate_from_global() is True
        
        # Get migration info
        migration_info = manager.get_migration_info()
        assert migration_info is not None
        repo_name, repo_config, _ = migration_info
        assert repo_name == "migrate-repo"
        assert repo_config.default_branch == "develop"
        
        # Perform migration
        config = manager.migrate_from_global()
        
        # Check migration happened
        assert manager.has_local_config()
        assert config.current_repository == "migrate-repo"
        assert config.repositories["migrate-repo"].default_branch == "develop"
        
        # Check allowed paths were migrated
        assert len(config.allowed_paths) == 1
        assert config.allowed_paths[0] == repo_root / "docs"
        
        # Check can_migrate is now false after migration
        assert manager.can_migrate_from_global() is False
    
    def test_get_config_location(self, tmp_path):
        """Test getting config location description."""
        # Without local config
        repo_root = tmp_path / "location-test"
        repo_root.mkdir()
        manager = LocalConfigManager(start_path=repo_root)
        location = manager.get_config_location()
        assert "global" in location
        
        # With local config
        (repo_root / ".aditi").mkdir()
        manager = LocalConfigManager(start_path=repo_root)
        location = manager.get_config_location()
        assert "local" in location
        assert ".aditi" in location