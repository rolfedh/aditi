"""Main CLI entry point for Aditi."""

import logging
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.logging import RichHandler

from aditi.commands import init_command

console = Console()
app = typer.Typer(
    name="aditi",
    help="AsciiDoc DITA Integration - Prepare AsciiDoc files for migration to DITA",
    no_args_is_help=True,
    rich_markup_mode="rich",
    add_completion=True,
    pretty_exceptions_show_locals=False,
)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the application.
    
    Args:
        verbose: If True, set logging level to DEBUG
    """
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                console=console,
                rich_tracebacks=True,
                tracebacks_show_locals=verbose,
            )
        ],
    )
    
    # Suppress verbose output from third-party libraries unless in verbose mode
    if not verbose:
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("docker").setLevel(logging.WARNING)


# Global verbose option
verbose_option = typer.Option(
    False,
    "--verbose",
    "-v",
    help="Enable verbose output",
)


@app.command()
def init(
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
    ),
    verbose: bool = verbose_option,
) -> None:
    """Initialize Vale configuration for AsciiDocDITA rules.
    
    This command will:
    - Pull the Vale container image if needed
    - Download AsciiDocDITA styles
    - Create a .vale.ini configuration file
    """
    setup_logging(verbose)
    init_command(path, force, use_docker)


@app.command()
def check(
    path: Optional[Path] = typer.Argument(
        None,
        help="Path to check (file or directory). Defaults to current directory.",
    ),
    verbose: bool = verbose_option,
) -> None:
    """Check AsciiDoc files for DITA compatibility issues.
    
    Runs Vale with AsciiDocDITA rules to identify issues that need
    to be addressed before migration to DITA.
    """
    setup_logging(verbose)
    console.print("[yellow]The 'check' command is not yet implemented.[/yellow]")
    console.print(
        "This command will analyze your AsciiDoc files and report "
        "DITA compatibility issues."
    )
    raise typer.Exit(1)


@app.command()
def fix(
    path: Optional[Path] = typer.Argument(
        None,
        help="Path to fix (file or directory). Defaults to current directory.",
    ),
    interactive: bool = typer.Option(
        True,
        "--interactive/--non-interactive",
        "-i/-n",
        help="Run in interactive mode (prompt for non-deterministic fixes)",
    ),
    verbose: bool = verbose_option,
) -> None:
    """Fix deterministic DITA compatibility issues in AsciiDoc files.
    
    Automatically applies fixes for issues that can be resolved
    deterministically. In interactive mode, prompts for user input
    on non-deterministic issues.
    """
    setup_logging(verbose)
    console.print("[yellow]The 'fix' command is not yet implemented.[/yellow]")
    console.print(
        "This command will automatically fix deterministic issues "
        "and guide you through manual fixes."
    )
    raise typer.Exit(1)


@app.command()
def journey(
    verbose: bool = verbose_option,
) -> None:
    """Start an interactive journey to migrate AsciiDoc files to DITA.
    
    This guided workflow will:
    - Help you configure Aditi for your repository
    - Create a feature branch
    - Run checks and apply fixes
    - Guide you through the git workflow
    - Create a pull request when ready
    """
    setup_logging(verbose)
    console.print("[yellow]The 'journey' command is not yet implemented.[/yellow]")
    console.print(
        "This command will provide an interactive, guided experience "
        "for migrating your AsciiDoc files to DITA."
    )
    raise typer.Exit(1)


def version_callback(value: bool) -> None:
    """Version callback function."""
    if value:
        console.print("aditi version 0.1.0")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
) -> None:
    """Aditi - AsciiDoc DITA Integration.
    
    A CLI tool to help prepare AsciiDoc files for migration to DITA
    by identifying and fixing compatibility issues.
    """
    pass


if __name__ == "__main__":
    app()