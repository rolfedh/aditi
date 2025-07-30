"""Vale command implementation for Aditi CLI."""

import json
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.table import Table

from ..config import ConfigManager
from ..vale_container import ValeContainer

console = Console()


def vale_command(
    paths: List[Path] = typer.Argument(
        default_factory=list,
        help="Paths to check (files or directories). If not specified, checks configured directories.",
        exists=True,
        file_okay=True,
        dir_okay=True,
        readable=True,
    ),
    output_format: str = typer.Option(
        "JSON",
        "--output",
        "-o",
        help="Output format: JSON, line, or CLI (default: JSON)",
    ),
    pretty: bool = typer.Option(
        True,
        "--pretty/--no-pretty",
        help="Pretty print JSON output (default: True)",
    ),
) -> None:
    """Run Vale directly and show the raw output.
    
    This command runs Vale with the AsciiDocDITA styles and shows
    the unprocessed output, useful for debugging and advanced users.
    """
    # Initialize configuration
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    # Determine which paths to check
    if not paths:
        # Use configured directories
        if not config.allowed_paths:
            console.print("[yellow]No paths configured. Run 'aditi journey' to configure paths.[/yellow]")
            raise typer.Exit(1)
        # Convert allowed_paths to Path objects, handling both string and Path inputs
        paths_to_check = []
        for p in config.allowed_paths:
            if isinstance(p, Path):
                paths_to_check.append(p)
            else:
                paths_to_check.append(Path(p))
    else:
        # Validate paths against configuration
        paths_to_check = []
        for path in paths:
            if config.is_path_allowed(path):
                paths_to_check.append(path)
            else:
                console.print(f"[yellow]Warning: Skipping {path} (not in allowed paths)[/yellow]")
                
    if not paths_to_check:
        console.print("[red]No valid paths to check.[/red]")
        raise typer.Exit(1)
        
    # Collect all .adoc files
    adoc_files = []
    for path in paths_to_check:
        if path.is_file() and path.suffix == ".adoc":
            adoc_files.append(path)
        elif path.is_dir():
            # Find all .adoc files recursively, handling symlinks based on config
            for adoc_file in path.rglob("*.adoc"):
                if config.ignore_symlinks:
                    # Only add if it's NOT a symlink
                    if not adoc_file.is_symlink():
                        adoc_files.append(adoc_file)
                else:
                    # Add all files (including symlinks)
                    adoc_files.append(adoc_file)
                    
    if not adoc_files:
        console.print("[yellow]No .adoc files found to check.[/yellow]")
        raise typer.Exit(0)
        
    # Initialize Vale container
    try:
        vale_container = ValeContainer()
        # Ensure Vale image exists
        vale_container.ensure_image_exists()
            
        # Convert paths to relative paths for container
        project_root = Path.cwd()
        path_args = []
        for p in adoc_files:
            try:
                rel_path = p.relative_to(project_root)
                path_args.append(str(rel_path))
            except ValueError:
                # If file is outside project root, use absolute path
                path_args.append(str(p))
        
        # Run Vale with specified output format
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task(
                f"Running Vale on {len(adoc_files)} files with output format: {output_format}",
                total=None
            )
            
            if output_format.upper() == "JSON":
                # Use JSON output and pretty print if requested
                output = vale_container.run_vale_raw(["--output=JSON"] + path_args)
                
                if pretty:
                    try:
                        # Parse and pretty print JSON
                        data = json.loads(output)
                        formatted = json.dumps(data, indent=2, sort_keys=True)
                        syntax = Syntax(formatted, "json", theme="monokai", line_numbers=True)
                        console.print(syntax)
                    except json.JSONDecodeError:
                        # Fallback to raw output if JSON parsing fails
                        console.print(output)
                else:
                    console.print(output)
            else:
                # Use specified format directly
                output = vale_container.run_vale_raw([f"--output={output_format}"] + path_args)
                # For non-JSON output, print raw text without Rich formatting
                print(output, end='')
            
    except Exception as e:
        console.print(f"[red]Error running Vale:[/red] {e}")
        raise typer.Exit(1)
    finally:
        # Cleanup Vale container
        if 'vale_container' in locals():
            vale_container.cleanup()


def show_vale_version() -> None:
    """Show Vale version information."""
    try:
        vale_container = ValeContainer()
        vale_container.ensure_image_exists()
        
        # Get Vale version
        version_output = vale_container.run_vale_raw(["--version"])
        console.print(f"Vale version: {version_output.strip()}")
        
    except Exception as e:
        console.print(f"[red]Error getting Vale version:[/red] {e}")
        raise typer.Exit(1)
    finally:
        if 'vale_container' in locals():
            vale_container.cleanup()


def list_vale_styles() -> None:
    """List installed Vale styles."""
    try:
        vale_container = ValeContainer()
        vale_container.ensure_image_exists()
        
        console.print("📋 Listing Vale styles...")
        
        # Try to list styles (this might not work in container, but we can try)
        try:
            styles_output = vale_container.run_vale_raw(["ls-config"])
            console.print(styles_output)
        except Exception:
            console.print("[yellow]Could not list styles directly. Checking configuration...[/yellow]")
            
            # Check for .vale.ini in current directory
            vale_config = Path.cwd() / ".vale.ini"
            if vale_config.exists():
                console.print(f"\n📄 Vale configuration found: {vale_config}")
                content = vale_config.read_text()
                syntax = Syntax(content, "ini", theme="monokai", line_numbers=True)
                console.print(syntax)
            else:
                console.print("[red]No .vale.ini found. Run 'aditi init' to set up Vale configuration.[/red]")
        
    except Exception as e:
        console.print(f"[red]Error listing Vale styles:[/red] {e}")
        raise typer.Exit(1)
    finally:
        if 'vale_container' in locals():
            vale_container.cleanup()