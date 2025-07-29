"""Vale container management module for Aditi.

This module provides a wrapper around Podman/Docker to run Vale with AsciiDocDITA styles.
It handles container lifecycle, mounting volumes, and processing Vale output.
"""

import json
import logging
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List

from rich.console import Console

logger = logging.getLogger(__name__)
console = Console()


class ValeContainer:
    """Manages Vale container lifecycle and execution."""

    VALE_IMAGE = "docker.io/jdkato/vale:latest"
    CONTAINER_NAME = "aditi-vale"

    def __init__(self, use_podman: bool = True):
        """Initialize Vale container manager.

        Args:
            use_podman: Use Podman instead of Docker. Defaults to True.
        """
        self.runtime = "podman" if use_podman else "docker"
        self._check_runtime_available()
        self._image_pulled = False  # Cache image pull status

    def _check_runtime_available(self) -> None:
        """Check if container runtime is available."""
        try:
            subprocess.run(
                [self.runtime, "--version"],
                check=True,
                capture_output=True,
                text=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                f"{self.runtime} is not installed or not available in PATH. "
                f"Please install {self.runtime} to use Aditi."
            )

    def pull_image(self) -> None:
        """Pull the Vale container image."""
        logger.info(f"Pulling Vale image: {self.VALE_IMAGE}")
        try:
            result = subprocess.run(
                [self.runtime, "pull", self.VALE_IMAGE],
                check=True,
                capture_output=True,
                text=True
            )
            logger.debug(f"Pull output: {result.stdout}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to pull Vale image: {e.stderr}")
            raise

    def ensure_image_exists(self) -> None:
        """Ensure the Vale image exists locally, pull if needed."""
        # Return early if we've already verified the image exists
        if self._image_pulled:
            return
            
        try:
            subprocess.run(
                [self.runtime, "image", "inspect", self.VALE_IMAGE],
                check=True,
                capture_output=True,
                text=True
            )
            logger.debug(f"Vale image {self.VALE_IMAGE} already exists")
            self._image_pulled = True
        except subprocess.CalledProcessError:
            logger.info(f"Vale image not found locally, pulling...")
            self.pull_image()
            self._image_pulled = True

    def init_vale_config(self, project_root: Path, force: bool = False) -> None:
        """Initialize Vale configuration in the project.

        Args:
            project_root: Root directory of the project to lint
            force: Force overwrite existing configuration
        """
        vale_ini = project_root / ".vale.ini"

        if vale_ini.exists() and not force:
            logger.info(f"Vale configuration already exists at {vale_ini}")
            return

        # Backup existing configuration if forcing
        if vale_ini.exists() and force:
            self._backup_vale_config(vale_ini)

        # Copy template configuration
        template_path = Path(__file__).parent / "vale" / "vale_config_template.ini"
        shutil.copy(template_path, vale_ini)
        logger.info(f"Created Vale configuration at {vale_ini}")

        # Run vale sync to download styles
        self._run_vale_sync(project_root)

    def _backup_vale_config(self, vale_ini: Path) -> None:
        """Create backups of existing Vale configuration.
        
        Creates:
        - .vale.ini.original (if it doesn't exist) - permanent backup of pre-Aditi config
        - .vale.ini.backup.YYYYMMDD_HHMMSS - timestamped backup
        
        Args:
            vale_ini: Path to the .vale.ini file to backup
        """
        # Create original backup if it doesn't exist
        original_backup = vale_ini.parent / ".vale.ini.original"
        if not original_backup.exists():
            shutil.copy2(vale_ini, original_backup)
            logger.info(f"Created permanent backup: {original_backup}")
            console.print(f"[green]Backing up original .vale.ini to {original_backup.name} (preserved permanently)[/green]")
        else:
            console.print(f"[dim]Original configuration preserved in {original_backup.name}[/dim]")
        
        # Create timestamped backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamped_backup = vale_ini.parent / f".vale.ini.backup.{timestamp}"
        shutil.copy2(vale_ini, timestamped_backup)
        logger.info(f"Created timestamped backup: {timestamped_backup}")
        console.print(f"[green]Creating timestamped backup: {timestamped_backup.name}[/green]")
        
        # Clean up old timestamped backups (keep only 5 most recent)
        self._cleanup_old_backups(vale_ini.parent)
    
    def _cleanup_old_backups(self, directory: Path, keep_count: int = 5) -> None:
        """Remove old timestamped backups, keeping only the most recent ones.
        
        Never deletes .vale.ini.original.
        
        Args:
            directory: Directory containing backups
            keep_count: Number of recent backups to keep
        """
        # Find all timestamped backups
        backups = sorted(directory.glob(".vale.ini.backup.*"), key=lambda p: p.stat().st_mtime, reverse=True)
        
        # Remove old backups beyond keep_count
        for backup in backups[keep_count:]:
            backup.unlink()
            logger.info(f"Removed old backup: {backup}")
    
    def list_backups(self, project_root: Path) -> List[Path]:
        """List all available Vale configuration backups.
        
        Args:
            project_root: Project directory
            
        Returns:
            List of backup file paths
        """
        backups = []
        
        # Check for original backup
        original = project_root / ".vale.ini.original"
        if original.exists():
            backups.append(original)
        
        # Find timestamped backups
        timestamped = sorted(project_root.glob(".vale.ini.backup.*"), 
                           key=lambda p: p.stat().st_mtime, reverse=True)
        backups.extend(timestamped)
        
        return backups
    
    def restore_backup(self, project_root: Path, backup_name: Optional[str] = None) -> bool:
        """Restore a Vale configuration from backup.
        
        Args:
            project_root: Project directory
            backup_name: Name of backup to restore (e.g., '.vale.ini.original').
                        If None, restores the original.
                        
        Returns:
            True if restore was successful
        """
        vale_ini = project_root / ".vale.ini"
        
        if backup_name is None:
            backup_name = ".vale.ini.original"
        
        backup_path = project_root / backup_name
        
        if not backup_path.exists():
            logger.error(f"Backup not found: {backup_path}")
            return False
        
        # Backup current config before restoring
        if vale_ini.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pre_restore_backup = project_root / f".vale.ini.before_restore.{timestamp}"
            shutil.copy2(vale_ini, pre_restore_backup)
            logger.info(f"Backed up current config to: {pre_restore_backup}")
        
        # Restore the backup
        shutil.copy2(backup_path, vale_ini)
        logger.info(f"Restored Vale configuration from: {backup_path}")
        return True

    def _run_vale_sync(self, project_root: Path) -> None:
        """Run vale sync to download style packages.

        Args:
            project_root: Directory containing .vale.ini
        """
        logger.info("Downloading AsciiDocDITA styles...")

        cmd = [
            self.runtime, "run", "--rm",
            "-v", f"{project_root}:/docs",
            "-w", "/docs",
            self.VALE_IMAGE,
            "sync"
        ]

        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            logger.debug(f"Vale sync output: {result.stdout}")
            logger.info("Successfully downloaded AsciiDocDITA styles")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to sync Vale styles: {e.stderr}")
            raise

    def run_vale(
        self,
        target_path: Path,
        project_root: Optional[Path] = None,
        output_format: str = "JSON"
    ) -> Dict:
        """Run Vale on the specified target.

        Args:
            target_path: File or directory to lint
            project_root: Project root containing .vale.ini. Defaults to target's parent.
            output_format: Vale output format. Defaults to JSON.

        Returns:
            Dictionary containing Vale results
        """
        if project_root is None:
            project_root = target_path.parent if target_path.is_file() else target_path

        # Ensure configuration exists
        if not (project_root / ".vale.ini").exists():
            raise FileNotFoundError(
                f"No .vale.ini found in {project_root}. "
                "Run 'aditi init' first to set up Vale configuration."
            )

        # Prepare paths for container
        abs_project_root = project_root.absolute()
        abs_target = target_path.absolute()

        # Calculate relative path from project root to target
        try:
            rel_target = abs_target.relative_to(abs_project_root)
        except ValueError:
            raise ValueError(
                f"Target path {abs_target} is not within project root {abs_project_root}"
            )

        # Run Vale in container with resource limits and timeout
        cmd = [
            self.runtime, "run", "--rm",
            "--memory=512m",      # Limit memory usage
            "--cpus=2",           # Limit CPU usage  
            "--security-opt=no-new-privileges",  # Security hardening
            "-v", f"{abs_project_root}:/docs:ro",  # Read-only mount for security
            "-w", "/docs",
            self.VALE_IMAGE,
            "--output", output_format,
            str(rel_target)
        ]

        logger.debug(f"Running Vale command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                check=False,  # Vale returns non-zero on violations
                capture_output=True,
                text=True,
                timeout=300   # 5-minute timeout for large files
            )

            if output_format == "JSON":
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse Vale JSON output: {result.stdout}")
                    logger.error(f"Vale stderr: {result.stderr}")
                    raise
            else:
                return {"output": result.stdout, "errors": result.stderr}

        except subprocess.TimeoutExpired:
            logger.error(f"Vale execution timed out after 5 minutes for {target_path}")
            raise RuntimeError(f"Vale processing timed out - {target_path} may be too large or complex")
        except subprocess.CalledProcessError as e:
            logger.error(f"Vale command failed: {e.stderr}")
            raise

    def run_vale_raw(self, args: list[str], project_root: Optional[Path] = None) -> str:
        """Run Vale with specified arguments and return raw output.
        
        Args:
            args: Command line arguments for Vale
            project_root: Project root directory. Defaults to current directory.
            
        Returns:
            Vale output as string
        """
        if project_root is None:
            project_root = Path.cwd()
        
        # Ensure configuration exists
        if not (project_root / ".vale.ini").exists():
            raise FileNotFoundError(
                f"No .vale.ini found in {project_root}. "
                "Run 'aditi init' first to set up Vale configuration."
            )
        
        # Run Vale in container with optimized flags
        cmd = [
            self.runtime, "run", "--rm", 
            "--memory=512m",  # Limit memory usage
            "--cpus=2",       # Limit CPU usage
            "-v", f"{project_root.absolute()}:/docs",
            "-w", "/docs",
            self.VALE_IMAGE,
        ] + args
        
        logger.debug(f"Running Vale command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                check=False,  # Vale returns non-zero on violations
                capture_output=True,
                text=True,
                timeout=300   # 5-minute timeout for large files
            )
            
            if result.stderr:
                logger.warning(f"Vale stderr: {result.stderr}")
                
            return result.stdout
            
        except subprocess.TimeoutExpired:
            logger.error("Vale execution timed out after 5 minutes")
            raise RuntimeError("Vale processing timed out - file may be too large")
        except subprocess.CalledProcessError as e:
            logger.error(f"Vale command failed: {e.stderr}")
            raise

    def cleanup(self) -> None:
        """Clean up any running containers."""
        try:
            # Check if container exists
            result = subprocess.run(
                [self.runtime, "ps", "-a", "--format", "{{.Names}}"],
                capture_output=True,
                text=True
            )

            if self.CONTAINER_NAME in result.stdout:
                logger.info(f"Removing container {self.CONTAINER_NAME}")
                subprocess.run(
                    [self.runtime, "rm", "-f", self.CONTAINER_NAME],
                    check=True
                )
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to cleanup container: {e}")


def check_container_runtime() -> str:
    """Check which container runtime is available.

    Returns:
        'podman' or 'docker' based on availability

    Raises:
        RuntimeError: If neither Podman nor Docker is available
    """
    for runtime in ["podman", "docker"]:
        try:
            subprocess.run(
                [runtime, "--version"],
                check=True,
                capture_output=True,
                text=True
            )
            return runtime
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue

    raise RuntimeError(
        "Neither Podman nor Docker is available. "
        "Please install Podman (recommended) or Docker to use Aditi."
    )