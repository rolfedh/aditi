"""Initialize command for Aditi.

Sets up Vale configuration and downloads AsciiDocDITA styles.
"""

import logging
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..vale_container import ValeContainer, check_container_runtime

logger = logging.getLogger(__name__)
console = Console()


def init_command(
    path: Optional[Path] = typer.Argument(
        None,
        help="Path to initialize Vale configuration. Defaults to current directory."
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force re-initialization even if configuration exists"
    ),
    use_docker: bool = typer.Option(
        False,
        "--docker",
        help="Use Docker instead of Podman"
    )
) -> None:
    """Initialize Aditi in your project.
    
    This command will:
    1. Check for Podman/Docker availability
    2. Pull the Vale container image
    3. Create a .vale.ini configuration file
    4. Download the AsciiDocDITA style rules
    """
    project_root = path or Path.cwd()
    
    console.print(f"[bold blue]Initializing Aditi in {project_root}[/bold blue]")
    
    # Check for existing configuration
    vale_ini = project_root / ".vale.ini"
    if vale_ini.exists() and not force:
        console.print(
            "[yellow]Vale configuration already exists.[/yellow]\n"
            "Use --force to reinitialize."
        )
        raise typer.Exit(1)
    
    try:
        # Determine container runtime
        if use_docker:
            runtime = "docker"
        else:
            try:
                runtime = check_container_runtime()
                if runtime == "docker":
                    console.print(
                        "[yellow]Using Docker as Podman is not available.[/yellow]\n"
                        "Consider installing Podman for better security."
                    )
            except RuntimeError as e:
                console.print(f"[red]Error: {e}[/red]")
                raise typer.Exit(1)
        
        # Initialize Vale container manager
        vale = ValeContainer(use_podman=(runtime == "podman"))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            # Pull Vale image
            task = progress.add_task("Pulling Vale container image...", total=None)
            vale.ensure_image_exists()
            progress.update(task, completed=True)
            
            # Initialize configuration
            task = progress.add_task("Creating Vale configuration...", total=None)
            vale.init_vale_config(project_root)
            progress.update(task, completed=True)
        
        console.print(
            "\n[green]✓ Aditi initialized successfully![/green]\n"
            f"Vale configuration created at: {vale_ini}\n"
            "AsciiDocDITA styles downloaded to: .vale/styles/\n\n"
            "[bold]Next steps:[/bold]\n"
            "1. Run 'aditi check' to validate your AsciiDoc files\n"
            "2. Run 'aditi journey' for a guided migration workflow"
        )
        
    except Exception as e:
        console.print(f"[red]Initialization failed: {e}[/red]")
        logger.exception("Failed to initialize Aditi")
        raise typer.Exit(1)