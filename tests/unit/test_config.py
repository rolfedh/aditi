"""Unit tests for configuration management."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from aditi.config import (
    AditiConfig,
    ConfigManager,
    PermissionMode,
    RepositoryConfig,
    SessionState,
    SubdirectoryPermission,
)


class TestSubdirectoryPermission:
    """Test SubdirectoryPermission model."""
    
    def test_valid_permission(self):
        """Test creating valid permission."""
        perm = SubdirectoryPermission(
            path="docs/internal",
            mode=PermissionMode.BLOCK,
            reason="Internal documentation"
        )
        assert perm.path == "docs/internal"
        assert perm.mode == PermissionMode.BLOCK
        assert perm.reason == "Internal documentation"
    
    def test_path_normalization(self):
        """Test path normalization."""
        perm = SubdirectoryPermission(
            path="  docs/internal/  ",
            mode=PermissionMode.ALLOW
        )
        assert perm.path == "docs/internal"
    
    def test_invalid_path(self):
        """Test invalid path patterns."""
        with pytest.raises(ValidationError):
            SubdirectoryPermission(
                path="../outside",
                mode=PermissionMode.ALLOW
            )
        
        with pytest.raises(ValidationError):
            SubdirectoryPermission(
                path="/absolute/path",
                mode=PermissionMode.ALLOW
            )


class TestRepositoryConfig:
    """Test RepositoryConfig model."""
    
    def test_valid_repository(self, temp_dir: Path):
        """Test creating valid repository config."""
        repo = RepositoryConfig(
            root=temp_dir,
            default_branch="main",
            release_branch="release/1.0",
            feature_branch_prefix="feature/"
        )
        assert repo.root == temp_dir.resolve()
        assert repo.default_branch == "main"
        assert repo.release_branch == "release/1.0"
        assert repo.feature_branch_prefix == "feature/"
    
    def test_invalid_root(self):
        """Test invalid repository root."""
        with pytest.raises(ValidationError):
            RepositoryConfig(root=Path("/nonexistent/path"))
    
    def test_is_path_allowed(self, temp_dir: Path):
        """Test path permission checking."""
        repo = RepositoryConfig(
            root=temp_dir,
            subdirectory_permissions=[
                SubdirectoryPermission(path="blocked", mode=PermissionMode.BLOCK),
                SubdirectoryPermission(path="allowed", mode=PermissionMode.ALLOW),
                SubdirectoryPermission(path="blocked/except", mode=PermissionMode.ALLOW),
            ]
        )
        
        # Test blocked paths
        assert not repo.is_path_allowed(Path("blocked/file.adoc"))
        assert not repo.is_path_allowed(Path("blocked/subdir/file.adoc"))
        
        # Test allowed paths
        assert repo.is_path_allowed(Path("allowed/file.adoc"))
        assert repo.is_path_allowed(Path("allowed/subdir/file.adoc"))
        
        # Test exception within blocked (more specific path takes precedence)
        assert repo.is_path_allowed(Path("blocked/except/file.adoc"))
        
        # Test default (no specific permission)
        assert repo.is_path_allowed(Path("other/file.adoc"))
        
        # Test absolute paths
        assert repo.is_path_allowed(temp_dir / "allowed/file.adoc")
        assert not repo.is_path_allowed(temp_dir / "blocked/file.adoc")


class TestSessionState:
    """Test SessionState model."""
    
    def test_default_session(self):
        """Test default session state."""
        session = SessionState()
        assert session.current_branch is None
        assert session.feature_branch is None
        assert len(session.processed_files) == 0
        assert len(session.pending_fixes) == 0
    
    def test_session_with_data(self):
        """Test session with data."""
        session = SessionState(
            current_branch="main",
            feature_branch="aditi/20240115-fix-entities",
            processed_files={"file1.adoc", "file2.adoc"},
            pending_fixes={
                "file3.adoc": ["EntityReference", "ContentType"]
            }
        )
        assert session.current_branch == "main"
        assert session.feature_branch == "aditi/20240115-fix-entities"
        assert "file1.adoc" in session.processed_files
        assert "EntityReference" in session.pending_fixes["file3.adoc"]


class TestAditiConfig:
    """Test AditiConfig model."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = AditiConfig()
        assert config.version == "1.0"
        assert len(config.repositories) == 0
        assert config.current_repository is None
        assert config.vale_styles_path is None
    
    def test_add_repository(self, temp_dir: Path):
        """Test adding repository."""
        config = AditiConfig()
        repo = config.add_repository(
            "test-repo",
            temp_dir,
            default_branch="develop",
            set_current=True
        )
        
        assert "test-repo" in config.repositories
        assert config.current_repository == "test-repo"
        assert repo.root == temp_dir.resolve()
        assert repo.default_branch == "develop"
    
    def test_get_current_repository(self, temp_dir: Path):
        """Test getting current repository."""
        config = AditiConfig()
        assert config.get_current_repository() is None
        
        config.add_repository("repo1", temp_dir)
        repo = config.get_current_repository()
        assert repo is not None
        assert repo.root == temp_dir.resolve()


class TestConfigManager:
    """Test ConfigManager class."""
    
    def test_init(self, temp_dir: Path):
        """Test initialization."""
        manager = ConfigManager(config_dir=temp_dir)
        assert manager.config_dir == temp_dir
        assert manager.config_file == temp_dir / "config.json"
        assert manager.session_file == temp_dir / "session.json"
    
    def test_ensure_config_dir(self, temp_dir: Path):
        """Test config directory creation."""
        config_dir = temp_dir / "subdir" / "config"
        manager = ConfigManager(config_dir=config_dir)
        
        assert not config_dir.exists()
        manager.ensure_config_dir()
        assert config_dir.exists()
        assert config_dir.is_dir()
    
    def test_save_and_load_config(self, temp_dir: Path):
        """Test saving and loading configuration."""
        manager = ConfigManager(config_dir=temp_dir)
        
        # Create config
        config = AditiConfig()
        repo_dir = temp_dir / "repo"
        repo_dir.mkdir()
        config.add_repository("test", repo_dir)
        
        # Save
        manager.save_config(config)
        assert manager.config_file.exists()
        
        # Clear cache and reload
        manager._config = None
        loaded = manager.load_config()
        
        assert "test" in loaded.repositories
        assert loaded.current_repository == "test"
        assert loaded.repositories["test"].root == repo_dir.resolve()
    
    def test_save_and_load_session(self, temp_dir: Path):
        """Test saving and loading session state."""
        manager = ConfigManager(config_dir=temp_dir)
        
        # Create session
        session = SessionState(
            current_branch="main",
            feature_branch="aditi/test",
            processed_files={"file1.adoc", "file2.adoc"}
        )
        
        # Save
        manager.save_session(session)
        assert manager.session_file.exists()
        
        # Clear cache and reload
        manager._session = None
        loaded = manager.load_session()
        
        assert loaded.current_branch == "main"
        assert loaded.feature_branch == "aditi/test"
        assert "file1.adoc" in loaded.processed_files
    
    def test_clear_session(self, temp_dir: Path):
        """Test clearing session state."""
        manager = ConfigManager(config_dir=temp_dir)
        
        # Create and save session
        session = SessionState(current_branch="main")
        manager.save_session(session)
        assert manager.session_file.exists()
        
        # Clear
        manager.clear_session()
        assert not manager.session_file.exists()
        assert manager.session.current_branch is None
    
    def test_property_access(self, temp_dir: Path):
        """Test property access auto-loads."""
        manager = ConfigManager(config_dir=temp_dir)
        
        # Access config property (should create new)
        config = manager.config
        assert isinstance(config, AditiConfig)
        
        # Access session property (should create new)
        session = manager.session
        assert isinstance(session, SessionState)