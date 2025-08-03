"""Unit tests for repository detection intelligence."""

import json
from pathlib import Path
import pytest

from aditi.local_config import LocalConfigManager
from aditi.config import AditiConfig, RepositoryConfig


class TestRepositoryDetection:
    """Test cases for intelligent repository detection."""
    
    def test_exact_match_preferred(self, tmp_path):
        """Test that exact repository root matches are preferred."""
        # Create global config directory
        global_dir = tmp_path / "aditi-data"
        global_dir.mkdir()
        
        # Create repository structure
        parent_repo = tmp_path / "parent-repo"
        parent_repo.mkdir()
        
        child_repo = parent_repo / "child-repo"
        child_repo.mkdir()
        (child_repo / ".git").mkdir()  # Make it a Git repo
        
        # Create global config with both repositories
        global_config = {
            "version": "1.0",
            "repositories": {
                "parent-repo": {
                    "root": str(parent_repo),
                    "default_branch": "main",
                    "subdirectory_permissions": [],
                    "feature_branch_prefix": "aditi/"
                },
                "child-repo": {
                    "root": str(child_repo),
                    "default_branch": "develop",
                    "subdirectory_permissions": [],
                    "feature_branch_prefix": "feature/"
                }
            }
        }
        
        (global_dir / "config.json").write_text(json.dumps(global_config, indent=2))
        
        # Test from child repo (exact match should win)
        manager = LocalConfigManager(start_path=child_repo)
        manager.global_config_dir = global_dir
        
        migration_info = manager.get_migration_info()
        assert migration_info is not None
        repo_name, repo_config, _ = migration_info
        
        # Should prefer child-repo (exact match + has .git)
        assert repo_name == "child-repo"
        assert repo_config.root == child_repo
    
    def test_git_repository_preferred(self, tmp_path):
        """Test that Git repositories are preferred over non-Git directories."""
        # Create global config directory
        global_dir = tmp_path / "aditi-data"
        global_dir.mkdir()
        
        # Create repository structure
        parent_dir = tmp_path / "projects"
        parent_dir.mkdir()
        
        docs_repo = parent_dir / "docs"
        docs_repo.mkdir()
        (docs_repo / ".git").mkdir()  # Make it a Git repo
        
        # Create global config
        global_config = {
            "version": "1.0",
            "repositories": {
                "projects": {
                    "root": str(parent_dir),
                    "default_branch": "main",
                    "subdirectory_permissions": [],
                    "feature_branch_prefix": "aditi/"
                }
            }
        }
        
        (global_dir / "config.json").write_text(json.dumps(global_config, indent=2))
        
        # Test from Git repo subdirectory
        manager = LocalConfigManager(start_path=docs_repo)
        manager.global_config_dir = global_dir
        
        migration_info = manager.get_migration_info()
        assert migration_info is not None
        repo_name, repo_config, _ = migration_info
        
        # Should use actual directory name since it's a Git repo
        assert repo_name == "docs"  # Not "projects"
        assert repo_config.root == parent_dir
    
    def test_directory_name_match_bonus(self, tmp_path):
        """Test that matching directory names get bonus points."""
        # Create global config directory
        global_dir = tmp_path / "aditi-data"
        global_dir.mkdir()
        
        # Create repository structure
        home = tmp_path / "home"
        home.mkdir()
        
        myproject = home / "myproject"
        myproject.mkdir()
        
        # Create global config
        global_config = {
            "version": "1.0",
            "repositories": {
                "home": {
                    "root": str(home),
                    "default_branch": "main",
                    "subdirectory_permissions": [],
                    "feature_branch_prefix": "aditi/"
                },
                "myproject": {  # Name matches directory
                    "root": str(home),  # But root is parent
                    "default_branch": "main",
                    "subdirectory_permissions": [],
                    "feature_branch_prefix": "aditi/"
                }
            }
        }
        
        (global_dir / "config.json").write_text(json.dumps(global_config, indent=2))
        
        # Test from myproject directory
        manager = LocalConfigManager(start_path=myproject)
        manager.global_config_dir = global_dir
        
        migration_info = manager.get_migration_info()
        assert migration_info is not None
        repo_name, repo_config, _ = migration_info
        
        # Should prefer myproject due to name match
        assert repo_name == "myproject"
    
    def test_path_filtering_during_migration(self, tmp_path):
        """Test that only paths under the repository are migrated."""
        # Create global config directory
        global_dir = tmp_path / "aditi-data"
        global_dir.mkdir()
        
        # Create repositories
        repo1 = tmp_path / "repo1"
        repo1.mkdir()
        (repo1 / ".git").mkdir()
        
        repo2 = tmp_path / "repo2"
        repo2.mkdir()
        
        # Create global config with allowed paths
        global_config = {
            "version": "1.0",
            "repositories": {
                "repo1": {
                    "root": str(repo1),
                    "default_branch": "main",
                    "subdirectory_permissions": [],
                    "feature_branch_prefix": "aditi/"
                }
            },
            "allowed_paths": [
                str(repo1 / "docs"),  # Under repo1
                str(repo2 / "docs"),  # Outside repo1
                str(tmp_path / "other")  # Outside both
            ]
        }
        
        (global_dir / "config.json").write_text(json.dumps(global_config, indent=2))
        
        # Perform migration from repo1
        manager = LocalConfigManager(start_path=repo1)
        manager.global_config_dir = global_dir
        
        config = manager.migrate_from_global()
        
        # Should only migrate paths under repo1
        assert len(config.allowed_paths) == 1
        assert config.allowed_paths[0] == repo1 / "docs"
        
        # Should only have one repository (not all from global)
        assert len(config.repositories) == 1
        assert "repo1" in config.repositories