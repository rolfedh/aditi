"""Local repository configuration management for Aditi.

This module provides repository-local configuration stored in .aditi/ directories,
similar to how .git/ works. This ensures each repository has its own isolated
configuration that travels with the code.
"""

import json
import logging
from pathlib import Path
from typing import Optional, Tuple

from .config import (
    AditiConfig,
    RepositoryConfig,
    SessionState,
    ConfigManager,
    PermissionMode,
    SubdirectoryPermission,
)

logger = logging.getLogger(__name__)


class LocalConfigManager(ConfigManager):
    """Manager for repository-local configuration.
    
    This manager looks for and creates configuration in a .aditi/ directory
    within the repository, similar to how Git stores its configuration.
    """
    
    LOCAL_CONFIG_DIR = ".aditi"
    GLOBAL_CONFIG_DIR = Path.home() / "aditi-data"
    
    def __init__(self, start_path: Optional[Path] = None):
        """Initialize local configuration manager.
        
        Args:
            start_path: Path to start searching for .aditi directory (defaults to cwd)
        """
        self.start_path = start_path or Path.cwd()
        self.local_config_dir: Optional[Path] = None
        self.global_config_dir = self.GLOBAL_CONFIG_DIR
        
        # Find or determine local config directory
        self._find_local_config_dir()
        
        # Initialize parent with appropriate config directory
        super().__init__(config_dir=self.local_config_dir or self.global_config_dir)
        
    def _find_local_config_dir(self) -> Optional[Path]:
        """Find .aditi directory in current or parent directories.
        
        Returns:
            Path to .aditi directory if found, None otherwise
        """
        current = self.start_path.resolve()
        
        while current != current.parent:
            aditi_dir = current / self.LOCAL_CONFIG_DIR
            if aditi_dir.is_dir():
                self.local_config_dir = aditi_dir
                logger.info(f"Found local config directory at {aditi_dir}")
                return aditi_dir
            current = current.parent
            
        return None
    
    def find_repository_root(self) -> Optional[Path]:
        """Find the repository root (directory containing .aditi or .git).
        
        Returns:
            Path to repository root, or None if not in a repository
        """
        current = self.start_path.resolve()
        
        while current != current.parent:
            # Check for .aditi directory
            if (current / self.LOCAL_CONFIG_DIR).is_dir():
                return current
            # Also check for .git as a fallback
            if (current / ".git").is_dir():
                return current
            current = current.parent
            
        return None
    
    def init_local_config(self, force: bool = False) -> Tuple[Path, AditiConfig]:
        """Initialize local configuration in the current repository.
        
        Args:
            force: Force re-initialization even if config exists
            
        Returns:
            Tuple of (config_dir_path, config)
            
        Raises:
            RuntimeError: If not in a Git repository
        """
        # Find repository root
        repo_root = self.find_repository_root()
        if not repo_root:
            # If no .git directory found, use current directory
            repo_root = self.start_path.resolve()
            logger.warning(f"No Git repository found, using current directory: {repo_root}")
        
        # Create .aditi directory
        local_dir = repo_root / self.LOCAL_CONFIG_DIR
        if local_dir.exists() and not force:
            raise RuntimeError(f"Local configuration already exists at {local_dir}")
        
        local_dir.mkdir(exist_ok=True)
        self.local_config_dir = local_dir
        self.config_dir = local_dir
        self.config_file = local_dir / "config.json"
        self.session_file = local_dir / "session.json"
        
        # Create new configuration for this repository
        config = AditiConfig()
        repo_config = RepositoryConfig(
            root=repo_root,
            default_branch="main",  # Will be updated if Git repo exists
        )
        
        # Try to detect default branch from Git
        try:
            from .git import GitManager
            git = GitManager(repo_root)
            if git.is_git_repository():
                default_branch = git.get_default_branch()
                if default_branch:
                    repo_config.default_branch = default_branch
        except Exception as e:
            logger.debug(f"Could not detect Git branch: {e}")
        
        # Add repository to config
        repo_name = repo_root.name
        config.repositories[repo_name] = repo_config
        config.current_repository = repo_name
        
        # Save the configuration
        self.save_config(config)
        
        # Add .aditi to .gitignore if needed
        self._update_gitignore(repo_root)
        
        logger.info(f"Initialized local configuration at {local_dir}")
        return local_dir, config
    
    def _update_gitignore(self, repo_root: Path) -> None:
        """Add .aditi/session.json to .gitignore if needed.
        
        Args:
            repo_root: Repository root directory
        """
        gitignore = repo_root / ".gitignore"
        patterns_to_add = [
            f"{self.LOCAL_CONFIG_DIR}/session.json",
            f"{self.LOCAL_CONFIG_DIR}/*.log",
        ]
        
        existing_lines = []
        if gitignore.exists():
            existing_lines = gitignore.read_text().splitlines()
        
        lines_to_add = []
        for pattern in patterns_to_add:
            if pattern not in existing_lines:
                lines_to_add.append(pattern)
        
        if lines_to_add:
            with gitignore.open("a") as f:
                if existing_lines and not existing_lines[-1] == "":
                    f.write("\n")
                f.write("\n# Aditi local session files\n")
                for line in lines_to_add:
                    f.write(f"{line}\n")
            logger.info(f"Updated .gitignore with Aditi patterns")
    
    def can_migrate_from_global(self) -> bool:
        """Check if current repository can be migrated from global config.
        
        Returns:
            True if migration is possible, False otherwise
        """
        # If we already have local config, no migration needed
        if self.local_config_dir:
            return False
            
        global_config_file = self.global_config_dir / "config.json"
        if not global_config_file.exists():
            return False
            
        # Load global config to check if current repo is configured there
        temp_manager = ConfigManager(config_dir=self.global_config_dir)
        global_config = temp_manager.load_config()
        
        # Check if current directory is under any configured repository
        current_path = self.start_path.resolve()
        for repo_name, repo_config in global_config.repositories.items():
            try:
                current_path.relative_to(repo_config.root)
                # We're in a configured repository
                return True
            except ValueError:
                continue
                
        return False
    
    def get_migration_info(self) -> Optional[Tuple[str, RepositoryConfig, AditiConfig]]:
        """Get migration information if available.
        
        Returns:
            Tuple of (repo_name, repo_config, global_config) if migration possible,
            None otherwise
        """
        if self.local_config_dir:
            return None
            
        global_config_file = self.global_config_dir / "config.json"
        if not global_config_file.exists():
            return None
            
        # Load global config
        temp_manager = ConfigManager(config_dir=self.global_config_dir)
        global_config = temp_manager.load_config()
        
        # Find matching repository with intelligent detection
        current_path = self.start_path.resolve()
        
        # Collect all potential matches
        matches = []
        for repo_name, repo_config in global_config.repositories.items():
            try:
                relative_path = current_path.relative_to(repo_config.root)
                # Calculate match score
                score = 0
                
                # Priority 1: Exact match (current dir is the repo root)
                if relative_path == Path("."):
                    score += 100
                    
                # Priority 2: Current directory has .git (is a Git repository)
                if (current_path / ".git").is_dir():
                    score += 50
                    
                # Priority 3: Repo root has .git (is a Git repository)  
                if (repo_config.root / ".git").is_dir():
                    score += 25
                    
                # Priority 4: Directory name matches repo name
                if current_path.name == repo_name:
                    score += 20
                    
                # Priority 5: Fewer levels deep (prefer closer matches)
                depth = len(relative_path.parts)
                score -= depth * 5
                
                matches.append((score, repo_name, repo_config))
                
            except ValueError:
                # Not under this repository
                continue
        
        # Return the best match if any
        if matches:
            # Sort by score (highest first)
            matches.sort(key=lambda x: x[0], reverse=True)
            best_score, best_name, best_config = matches[0]
            
            # Use actual directory name if we're at a Git root
            if (current_path / ".git").is_dir():
                # Override the name with the actual directory name
                actual_name = current_path.name
                logger.info(f"Using actual repository name '{actual_name}' instead of '{best_name}'")
                best_name = actual_name
                
            return (best_name, best_config, global_config)
                
        return None
    
    def migrate_from_global(self) -> AditiConfig:
        """Perform migration from global to local config.
        
        Returns:
            Migrated configuration
            
        Raises:
            RuntimeError: If migration is not possible
        """
        migration_info = self.get_migration_info()
        if not migration_info:
            raise RuntimeError("No global configuration found for migration")
            
        repo_name, repo_config, global_config = migration_info
        return self._migrate_from_global(repo_name, repo_config, global_config)
    
    def load_config(self) -> AditiConfig:
        """Load configuration, preferring local over global.
        
        Returns:
            Loaded configuration
        """
        # If we have a local config directory, use it
        if self.local_config_dir:
            return super().load_config()
        
        # No automatic migration - just return empty config
        logger.info("No local configuration found")
        return AditiConfig()
    
    def _migrate_from_global(
        self,
        repo_name: str,
        repo_config: RepositoryConfig,
        global_config: AditiConfig
    ) -> AditiConfig:
        """Migrate repository configuration from global to local.
        
        Args:
            repo_name: Repository name in global config
            repo_config: Repository configuration from global
            global_config: Full global configuration
            
        Returns:
            New local configuration
        """
        logger.info(f"Migrating repository '{repo_name}' from global to local config")
        
        # Create local config directory
        try:
            local_dir, local_config = self.init_local_config(force=False)
        except RuntimeError:
            # Local config already exists, just load it
            return super().load_config()
        
        # Copy relevant settings from global config
        local_config.vale_styles_path = global_config.vale_styles_path
        
        # Only migrate the specific repository that matches
        # First, check if we already created the repo during init_local_config
        existing_repo_name = None
        if local_config.repositories:
            # Get the first (and should be only) repository name
            existing_repo_name = list(local_config.repositories.keys())[0]
            
        # Update or replace with migrated repository
        if existing_repo_name and existing_repo_name != repo_name:
            # Remove the auto-created entry
            del local_config.repositories[existing_repo_name]
            
        # Add the migrated repository with the correct name
        local_config.repositories[repo_name] = repo_config
        local_config.current_repository = repo_name
        
        # Copy allowed paths ONLY if they're under this repository
        repo_root = repo_config.root
        for allowed_path in global_config.allowed_paths:
            try:
                # Check if path is under the repository root
                allowed_path.relative_to(repo_root)
                if allowed_path not in local_config.allowed_paths:
                    local_config.allowed_paths.append(allowed_path)
                    logger.info(f"Migrated allowed path: {allowed_path}")
            except ValueError:
                # Path is outside this repository - skip it
                logger.info(f"Skipping path outside repository: {allowed_path}")
        
        # Save migrated config
        self.save_config(local_config)
        
        return local_config
    
    def has_local_config(self) -> bool:
        """Check if local configuration exists.
        
        Returns:
            True if local config exists, False otherwise
        """
        return self.local_config_dir is not None
    
    def get_config_location(self) -> str:
        """Get human-readable description of config location.
        
        Returns:
            Description of where config is stored
        """
        if self.local_config_dir:
            return f"local ({self.local_config_dir})"
        else:
            return f"global ({self.global_config_dir})"