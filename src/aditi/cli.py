"""Main CLI entry point for Aditi."""

import logging
import sys
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.logging import RichHandler

from aditi.commands import init_command, check_command, journey_command, fix_command
from aditi.commands.vale import vale_command, show_vale_version, list_vale_styles

console = Console()
app = typer.Typer(
    name="aditi",
    help="""AsciiDoc DITA Integration - Prepare AsciiDoc files for migration to DITA

IMPORTANT:
- cd to the root directory of your repository before running aditi commands.
- Create a working branch with the latest changes in it.""",
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
    paths: Optional[list[Path]] = typer.Argument(
        None,
        help="Paths to check (files or directories). If not specified, checks configured directories.",
        exists=True,
        file_okay=True,
        dir_okay=True,
        readable=True,
    ),
    rule: Optional[str] = typer.Option(
        None,
        "--rule",
        "-r",
        help="Check only specific rule (e.g., EntityReference)",
    ),
    verbose: bool = verbose_option,
) -> None:
    """Check AsciiDoc files for DITA compatibility issues.
    
    Runs Vale with AsciiDocDITA rules to identify issues that need
    to be addressed before migration to DITA.
    """
    setup_logging(verbose)
    check_command(paths, rule, verbose)


@app.command()
def fix(
    paths: Optional[List[Path]] = typer.Argument(
        None,
        help="Paths to fix (files or directories). If not specified, uses configured directories.",
        exists=True,
        file_okay=True,
        dir_okay=True,
        readable=True,
    ),
    rule: Optional[str] = typer.Option(
        None,
        "--rule",
        "-r",
        help="Fix only specific rule (e.g., EntityReference)",
    ),
    interactive: bool = typer.Option(
        True,
        "--interactive/--non-interactive",
        "-i/-n",
        help="Run in interactive mode (prompt for confirmation)",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-d",
        help="Show what would be fixed without applying changes",
    ),
    verbose: bool = verbose_option,
) -> None:
    """Fix deterministic DITA compatibility issues in AsciiDoc files.
    
    Automatically applies fixes for issues that can be resolved
    deterministically. In interactive mode, prompts for user confirmation
    before applying fixes.
    """
    setup_logging(verbose)
    fix_command(paths, rule, interactive, dry_run)


@app.command()
def journey(
    verbose: bool = verbose_option,
) -> None:
    """Start an interactive journey to prepare AsciiDoc files for DITA migration.
    
    This guided workflow will:
    - Help you configure Aditi for your repository
    - Automatically fix or flag issues for you
    - Prompt you to review automatic fixes
    - Prompt you to fix flagged issues
    """
    setup_logging(verbose)
    journey_command()


@app.command()
def vale(
    paths: Optional[list[Path]] = typer.Argument(
        None,
        help="Paths to check (files or directories). If not specified, checks configured directories."
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
    verbose: bool = verbose_option,
) -> None:
    """Run Vale directly and show the raw output.
    
    This command runs Vale with the AsciiDocDITA styles and shows
    the unprocessed output, useful for debugging and advanced users.
    
    Examples:
    - aditi vale                    # Run on configured paths with JSON output
    - aditi vale --output=line      # Use line output format
    - aditi vale file.adoc          # Check specific file
    - aditi vale --no-pretty        # JSON without pretty printing
    """
    setup_logging(verbose)
    vale_command(paths, output_format, pretty)


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