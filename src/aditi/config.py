"""Configuration management for Aditi."""

import json
import logging
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class PermissionMode(str, Enum):
    """Permission mode for subdirectories."""
    
    ALLOW = "allow"
    BLOCK = "block"


class SubdirectoryPermission(BaseModel):
    """Permission configuration for a subdirectory."""
    
    path: str = Field(
        description="Relative path from repository root"
    )
    mode: PermissionMode = Field(
        description="Permission mode: allow or block"
    )
    reason: Optional[str] = Field(
        None,
        description="Optional reason for the permission setting"
    )

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        """Ensure path doesn't contain dangerous patterns."""
        if ".." in v or v.startswith("/"):
            raise ValueError("Path must be relative and not contain '..'")
        return v.strip().rstrip("/")


class RepositoryConfig(BaseModel):
    """Configuration for a single repository."""
    
    root: Path = Field(
        description="Absolute path to repository root"
    )
    default_branch: str = Field(
        "main",
        description="Default branch name"
    )
    release_branch: Optional[str] = Field(
        None,
        description="Release branch name if different from default"
    )
    subdirectory_permissions: List[SubdirectoryPermission] = Field(
        default_factory=list,
        description="List of subdirectory permissions"
    )
    feature_branch_prefix: str = Field(
        "aditi/",
        description="Prefix for feature branches created by Aditi"
    )

    @field_validator("root")
    @classmethod
    def validate_root(cls, v: Path) -> Path:
        """Ensure root path exists and is a directory."""
        if not v.exists():
            raise ValueError(f"Repository root does not exist: {v}")
        if not v.is_dir():
            raise ValueError(f"Repository root is not a directory: {v}")
        return v.resolve()

    def is_path_allowed(self, path: Path) -> bool:
        """Check if a path is allowed based on permissions.
        
        Args:
            path: Path to check (can be absolute or relative to root)
            
        Returns:
            True if path is allowed, False otherwise
        """
        # Convert to relative path if absolute
        if path.is_absolute():
            try:
                rel_path = path.relative_to(self.root)
            except ValueError:
                # Path is outside repository
                return False
        else:
            rel_path = path

        # Convert to string for comparison
        path_str = str(rel_path).replace("\\", "/")

        # Check permissions, preferring more specific (longer) paths
        matching_perms = []
        for perm in self.subdirectory_permissions:
            perm_path = perm.path
            
            # Check if path matches or is subdirectory of permission path
            if path_str == perm_path or path_str.startswith(perm_path + "/"):
                matching_perms.append(perm)
        
        if matching_perms:
            # Use the most specific (longest path) permission
            most_specific = max(matching_perms, key=lambda p: len(p.path))
            return most_specific.mode == PermissionMode.ALLOW

        # Default to allow if no specific permission
        return True


class SessionState(BaseModel):
    """Session state for tracking current operations."""
    
    current_branch: Optional[str] = Field(
        None,
        description="Current git branch"
    )
    feature_branch: Optional[str] = Field(
        None,
        description="Feature branch created for this session"
    )
    processed_files: Set[str] = Field(
        default_factory=set,
        description="Set of files already processed"
    )
    pending_fixes: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Files with pending fixes mapped to rule names"
    )
    journey_state: Optional[str] = Field(
        None,
        description="Current state of journey command execution"
    )
    journey_progress: Dict[str, Any] = Field(
        default_factory=dict,
        description="Progress tracking for journey command"
    )
    applied_rules: List[str] = Field(
        default_factory=list,
        description="Rules that have been applied in current journey"
    )
    # Enhanced tracking fields
    current_rule: Optional[str] = Field(
        None,
        description="Rule currently being processed"
    )
    total_rules: Optional[int] = Field(
        None,
        description="Total number of rules to process"
    )
    files_fixed_by_rule: Dict[str, int] = Field(
        default_factory=dict,
        description="Number of files fixed per rule"
    )
    session_started: Optional[str] = Field(
        None,
        description="ISO timestamp when session started"
    )
    last_updated: Optional[str] = Field(
        None,
        description="ISO timestamp of last update"
    )

    class Config:
        """Pydantic configuration."""
        
        arbitrary_types_allowed = True


class AditiConfig(BaseModel):
    """Main configuration for Aditi."""
    
    version: str = Field(
        "1.0",
        description="Configuration schema version"
    )
    repositories: Dict[str, RepositoryConfig] = Field(
        default_factory=dict,
        description="Repository configurations keyed by name"
    )
    current_repository: Optional[str] = Field(
        None,
        description="Name of currently active repository"
    )
    vale_styles_path: Optional[Path] = Field(
        None,
        description="Custom path for Vale styles (defaults to ~/.config/aditi/styles)"
    )
    allowed_paths: List[Path] = Field(
        default_factory=list,
        description="List of paths allowed for checking"
    )
    selected_directories: List[Path] = Field(
        default_factory=list,
        description="Directories selected during journey configuration"
    )
    excluded_directories: List[Path] = Field(
        default_factory=list,
        description="Directories explicitly excluded by user"
    )
    ignore_symlinks: bool = Field(
        True,
        description="Whether to ignore symlinks when scanning"
    )

    def get_current_repository(self) -> Optional[RepositoryConfig]:
        """Get the current repository configuration."""
        if self.current_repository and self.current_repository in self.repositories:
            return self.repositories[self.current_repository]
        return None
    
    def is_path_allowed(self, path: Path) -> bool:
        """Check if a path is allowed for processing.
        
        Args:
            path: Path to check
            
        Returns:
            True if path is allowed or no restrictions are set
        """
        # If no allowed paths are configured, allow all paths
        if not self.allowed_paths:
            return True
            
        # Convert to absolute path for comparison
        abs_path = path.resolve()
        
        # Check if path is under any allowed path
        for allowed_path in self.allowed_paths:
            allowed_abs = allowed_path.resolve()
            try:
                abs_path.relative_to(allowed_abs)
                return True
            except ValueError:
                continue
                
        return False

    def add_repository(
        self,
        name: str,
        root: Path,
        default_branch: str = "main",
        set_current: bool = True,
    ) -> RepositoryConfig:
        """Add a new repository configuration.
        
        Args:
            name: Repository name
            root: Repository root path
            default_branch: Default branch name
            set_current: Whether to set as current repository
            
        Returns:
            The created repository configuration
        """
        repo_config = RepositoryConfig(
            root=root,
            default_branch=default_branch,
        )
        self.repositories[name] = repo_config
        
        if set_current:
            self.current_repository = name
            
        return repo_config


class ConfigManager:
    """Manager for Aditi configuration."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize configuration manager.
        
        Args:
            config_dir: Configuration directory (defaults to ~/aditi-data)
        """
        self.config_dir = config_dir or Path.home() / "aditi-data"
        self.config_file = self.config_dir / "config.json"
        self.session_file = self.config_dir / "session.json"
        self._config: Optional[AditiConfig] = None
        self._session: Optional[SessionState] = None

    def ensure_config_dir(self) -> None:
        """Ensure configuration directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def load_config(self) -> AditiConfig:
        """Load configuration from disk.
        
        Returns:
            Loaded configuration or new instance if file doesn't exist
        """
        if self._config is not None:
            return self._config

        self.ensure_config_dir()

        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    self._config = AditiConfig(**data)
                    logger.info(f"Loaded configuration from {self.config_file}")
            except Exception as e:
                logger.error(f"Failed to load configuration: {e}")
                self._config = AditiConfig()
        else:
            logger.info("No configuration file found, creating new configuration")
            self._config = AditiConfig()

        return self._config

    def save_config(self, config: Optional[AditiConfig] = None) -> None:
        """Save configuration to disk.
        
        Args:
            config: Configuration to save (uses cached if not provided)
        """
        if config is not None:
            self._config = config
        elif self._config is None:
            raise ValueError("No configuration to save")

        self.ensure_config_dir()

        try:
            with open(self.config_file, "w") as f:
                json.dump(
                    self._config.model_dump(mode="json"),
                    f,
                    indent=2,
                    default=str,  # Handle Path objects
                )
            logger.info(f"Saved configuration to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise

    def load_session(self) -> SessionState:
        """Load session state from disk.
        
        Returns:
            Loaded session state or new instance if file doesn't exist
        """
        if self._session is not None:
            return self._session

        self.ensure_config_dir()

        if self.session_file.exists():
            try:
                with open(self.session_file, "r") as f:
                    data = json.load(f)
                    self._session = SessionState(**data)
                    logger.info(f"Loaded session state from {self.session_file}")
            except Exception as e:
                logger.error(f"Failed to load session state: {e}")
                self._session = SessionState()
        else:
            logger.info("No session file found, creating new session")
            self._session = SessionState()

        return self._session

    def save_session(self, session: Optional[SessionState] = None) -> None:
        """Save session state to disk.
        
        Args:
            session: Session state to save (uses cached if not provided)
        """
        if session is not None:
            self._session = session
        elif self._session is None:
            raise ValueError("No session state to save")

        self.ensure_config_dir()

        try:
            with open(self.session_file, "w") as f:
                # Convert sets to lists for JSON serialization
                data = self._session.model_dump(mode="json")
                if "processed_files" in data:
                    data["processed_files"] = list(data["processed_files"])
                json.dump(data, f, indent=2)
            logger.info(f"Saved session state to {self.session_file}")
        except Exception as e:
            logger.error(f"Failed to save session state: {e}")
            raise

    def clear_session(self) -> None:
        """Clear session state."""
        self._session = SessionState()
        if self.session_file.exists():
            self.session_file.unlink()
            logger.info("Cleared session state")
            
    def create_default_config(self, scan_for_docs: bool = True) -> AditiConfig:
        """Create a default configuration with automatic path discovery.
        
        Args:
            scan_for_docs: Whether to scan for documentation directories
            
        Returns:
            Newly created configuration
        """
        from .scanner import DirectoryScanner
        
        config = AditiConfig()
        current_dir = Path.cwd()
        
        if scan_for_docs:
            # Scan for .adoc files in subdirectories
            scanner = DirectoryScanner(ignore_symlinks=True)
            adoc_dirs = scanner.scan_for_adoc_files(current_dir)
            
            if adoc_dirs:
                # Find documentation roots (common parent directories)
                doc_roots = scanner.find_documentation_roots(adoc_dirs)
                
                # Add the most significant documentation roots as allowed paths
                for path, direct_count, total_count in doc_roots:
                    config.allowed_paths.append(path)
                    logger.info(f"Added documentation directory to allowed paths: {path} ({total_count} .adoc files)")
                    
                # If no roots found but we have directories, add them all
                if not config.allowed_paths and adoc_dirs:
                    for path in sorted(adoc_dirs.keys())[:5]:  # Limit to top 5 directories
                        config.allowed_paths.append(path)
                        logger.info(f"Added directory to allowed paths: {path}")
            else:
                # No .adoc files found, add current directory as fallback
                config.allowed_paths.append(current_dir)
                logger.info(f"No .adoc files found. Added current directory to allowed paths: {current_dir}")
        else:
            # Just add current directory without scanning
            config.allowed_paths.append(current_dir)
            logger.info(f"Added current directory to allowed paths: {current_dir}")
            
        # Save the configuration
        self._config = config
        self.save_config()
        
        return config

    @property
    def config(self) -> AditiConfig:
        """Get current configuration (loads if needed)."""
        if self._config is None:
            self.load_config()
        return self._config

    @property
    def session(self) -> SessionState:
        """Get current session state (loads if needed)."""
        if self._session is None:
            self.load_session()
        return self._session


# Global config manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager