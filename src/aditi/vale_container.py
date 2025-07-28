"""Vale container management module for Aditi.

This module provides a wrapper around Podman/Docker to run Vale with AsciiDocDITA styles.
It handles container lifecycle, mounting volumes, and processing Vale output.
"""

import json
import logging
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


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
        try:
            subprocess.run(
                [self.runtime, "image", "inspect", self.VALE_IMAGE],
                check=True,
                capture_output=True,
                text=True
            )
            logger.debug(f"Vale image {self.VALE_IMAGE} already exists")
        except subprocess.CalledProcessError:
            logger.info(f"Vale image not found locally, pulling...")
            self.pull_image()

    def init_vale_config(self, project_root: Path) -> None:
        """Initialize Vale configuration in the project.

        Args:
            project_root: Root directory of the project to lint
        """
        vale_ini = project_root / ".vale.ini"

        if vale_ini.exists():
            logger.info(f"Vale configuration already exists at {vale_ini}")
            return

        # Copy template configuration
        template_path = Path(__file__).parent / "vale" / "vale_config_template.ini"
        shutil.copy(template_path, vale_ini)
        logger.info(f"Created Vale configuration at {vale_ini}")

        # Run vale sync to download styles
        self._run_vale_sync(project_root)

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

        # Run Vale in container
        cmd = [
            self.runtime, "run", "--rm",
            "-v", f"{abs_project_root}:/docs",
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
                text=True
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

        except subprocess.CalledProcessError as e:
            logger.error(f"Vale command failed: {e.stderr}")
            raise

    def run_vale(self, args: list[str]) -> str:
        """Run Vale with specified arguments.
        
        Args:
            args: Command line arguments for Vale
            
        Returns:
            Vale output as string
        """
        # Find project root (current directory)
        project_root = Path.cwd()
        
        # Ensure configuration exists
        if not (project_root / ".vale.ini").exists():
            raise FileNotFoundError(
                f"No .vale.ini found in {project_root}. "
                "Run 'aditi init' first to set up Vale configuration."
            )
        
        # Run Vale in container
        cmd = [
            self.runtime, "run", "--rm",
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
                text=True
            )
            
            if result.stderr:
                logger.warning(f"Vale stderr: {result.stderr}")
                
            return result.stdout
            
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