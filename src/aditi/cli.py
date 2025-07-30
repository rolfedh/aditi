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

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # Fallback for older Python
    except ImportError:
        tomllib = None

console = Console()

def get_version() -> str:
    """Get version from pyproject.toml or fallback."""
    if not tomllib:
        return "unknown (tomllib not available)"
    
    # Look for pyproject.toml in the package directory and up the tree
    current_dir = Path(__file__).parent
    for _ in range(5):  # Search up to 5 levels up
        pyproject_path = current_dir / "pyproject.toml"
        if pyproject_path.exists():
            try:
                with open(pyproject_path, "rb") as f:
                    data = tomllib.load(f)
                    return data.get("project", {}).get("version", "unknown")
            except Exception:
                break
        current_dir = current_dir.parent
        if current_dir == current_dir.parent:  # Reached filesystem root
            break
    
    # Fallback: try to get from package metadata
    try:
        from importlib.metadata import version
        return version("aditi")
    except Exception:
        return "unknown"

app = typer.Typer(
    name="aditi",
    help="""AsciiDoc DITA Integration - Prepare AsciiDoc files for migration to DITA

[bold yellow]⚠️  IMPORTANT:[/bold yellow]
[bold]- cd to the root directory of your repository before running aditi commands.
- Create a working branch with the latest changes in it.[/bold]""",
    no_args_is_help=True,
    rich_markup_mode="rich",
    add_completion=False,
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
    list_backups: bool = typer.Option(
        False,
        "--list-backups",
        help="List all available Vale configuration backups"
    ),
    restore_original: bool = typer.Option(
        False,
        "--restore-original",
        help="Restore the original Vale configuration from backup"
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
    init_command(path, force, use_docker, list_backups, restore_original)


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
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-d", 
        help="Show what would be configured and fixed without making changes",
    ),
    clear: bool = typer.Option(
        False,
        "--clear",
        help="Clear the current journey session and start fresh",
    ),
    status: bool = typer.Option(
        False,
        "--status",
        help="Show current journey session status without starting",
    ),
    verbose: bool = verbose_option,
) -> None:
    """Start an interactive journey to prepare AsciiDoc files for DITA migration.
    
    This guided workflow will:
    - Help you configure Aditi for your repository
    - Automatically fix or flag issues for you
    - Prompt you to review automatic fixes
    - Prompt you to fix flagged issues
    
    Use --dry-run to preview actions without making changes.
    Use --clear to clear the current session and start fresh.
    Use --status to view current session progress.
    """
    setup_logging(verbose)
    journey_command(dry_run=dry_run, clear=clear, status=status)


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


@app.command()
def completion(
    shell: Optional[str] = typer.Argument(
        None,
        help="Shell type (bash, zsh, fish, powershell). Auto-detected if not specified."
    ),
    install: bool = typer.Option(
        False,
        "--install",
        help="Install completion for the current shell"
    ),
    show: bool = typer.Option(
        False,
        "--show",
        help="Show completion script for the current shell"
    ),
) -> None:
    """Manage shell completion for Aditi.
    
    This command helps you set up shell completion so you can use Tab
    to complete Aditi commands and options.
    
    Examples:
    - aditi completion --show           # Show completion script
    - aditi completion --install        # Install completion
    - aditi completion bash --show      # Show bash completion script
    - aditi completion zsh --install    # Install zsh completion
    """
    import click
    from typer.main import get_command
    
    # Get the click command from typer app
    click_command = get_command(app)
    
    # Check if completion is available
    completion_available = False
    get_completion_func = None
    
    if hasattr(click_command, 'get_completion_script'):
        # Older Click/Typer version
        completion_available = True
        get_completion_func = click_command.get_completion_script
    else:
        try:
            from click.completion import get_completion_script as click_get_completion
            completion_available = True
            get_completion_func = lambda shell, prog: click_get_completion(click_command, {}, shell, prog)
        except ImportError:
            pass
    
    if not completion_available:
        console.print("[yellow]Shell completion generation not available in this environment.[/yellow]")
        console.print("\n[bold]Manual setup instructions:[/bold]")
        console.print("For bash, add this to your ~/.bashrc or ~/.bash_profile:")
        console.print(f"[dim]eval \"$(_ADITI_COMPLETE=bash_source aditi)\"[/dim]")
        console.print("\nFor zsh, add this to your ~/.zshrc:")
        console.print(f"[dim]eval \"$(_ADITI_COMPLETE=zsh_source aditi)\"[/dim]")
        console.print("\nFor fish, add this to your ~/.config/fish/config.fish:")
        console.print(f"[dim]eval (env _ADITI_COMPLETE=fish_source aditi)[/dim]")
        return
    
    # Detect shell if not provided
    if not shell:
        import os
        shell_env = os.environ.get('SHELL', '')
        if 'bash' in shell_env:
            shell = 'bash'
        elif 'zsh' in shell_env:
            shell = 'zsh'
        elif 'fish' in shell_env:
            shell = 'fish'
        else:
            shell = 'bash'  # Default fallback
    
    # Validate shell
    valid_shells = ['bash', 'zsh', 'fish', 'powershell']
    if shell not in valid_shells:
        console.print(f"[red]Error: Unsupported shell '{shell}'. Supported shells: {', '.join(valid_shells)}[/red]")
        raise typer.Exit(1)
    
    if show:
        # Show completion script
        try:
            if shell == 'bash':
                script = get_completion_func('bash', 'aditi')
            elif shell == 'zsh':
                script = get_completion_func('zsh', '_aditi')
            elif shell == 'fish':
                script = get_completion_func('fish', 'aditi')
            else:
                console.print(f"[red]Completion script generation not supported for {shell}[/red]")
                raise typer.Exit(1)
            
            console.print(f"[dim]# Completion script for {shell}[/dim]")
            console.print(script)
        except Exception as e:
            console.print(f"[red]Error generating completion script: {e}[/red]")
            raise typer.Exit(1)
    
    elif install:
        # Install completion
        console.print(f"[bold]Installing completion for {shell}...[/bold]")
        
        try:
            if shell == 'bash':
                if hasattr(click_command, 'get_completion_script'):
                    script = click_command.get_completion_script('bash', 'aditi')
                else:
                    script = get_completion_script(click_command, {}, 'bash', 'aditi')
                completion_file = Path.home() / '.bash_completion'
                marker = "# Aditi completion"
                
                # Read existing file or create empty
                if completion_file.exists():
                    content = completion_file.read_text()
                else:
                    content = ""
                
                # Check if already installed
                if marker in content:
                    console.print("[yellow]Completion already installed for bash[/yellow]")
                else:
                    # Append completion
                    with completion_file.open('a') as f:
                        f.write(f"\n{marker}\n{script}\n")
                    console.print(f"[green]✓ Completion installed to {completion_file}[/green]")
                    console.print("[dim]Restart your shell or run: source ~/.bash_completion[/dim]")
            
            elif shell == 'zsh':
                # For zsh, we need to add to a completion directory
                zsh_completions = Path.home() / '.zsh' / 'completions'
                zsh_completions.mkdir(parents=True, exist_ok=True)
                completion_file = zsh_completions / '_aditi'
                
                if hasattr(click_command, 'get_completion_script'):
                    script = click_command.get_completion_script('zsh', '_aditi')
                else:
                    script = get_completion_script(click_command, {}, 'zsh', '_aditi')
                completion_file.write_text(script)
                
                console.print(f"[green]✓ Completion installed to {completion_file}[/green]")
                console.print("[dim]Add this to your ~/.zshrc if not already present:[/dim]")
                console.print(f"[dim]fpath=(~/.zsh/completions $fpath)[/dim]")
                console.print("[dim]autoload -U compinit && compinit[/dim]")
            
            elif shell == 'fish':
                # Fish completions go in ~/.config/fish/completions/
                fish_completions = Path.home() / '.config' / 'fish' / 'completions'
                fish_completions.mkdir(parents=True, exist_ok=True)
                completion_file = fish_completions / 'aditi.fish'
                
                if hasattr(click_command, 'get_completion_script'):
                    script = click_command.get_completion_script('fish', 'aditi')
                else:
                    script = get_completion_script(click_command, {}, 'fish', 'aditi')
                completion_file.write_text(script)
                
                console.print(f"[green]✓ Completion installed to {completion_file}[/green]")
                console.print("[dim]Restart your shell or run: source ~/.config/fish/completions/aditi.fish[/dim]")
            
            else:
                console.print(f"[red]Installation not supported for {shell}[/red]")
                raise typer.Exit(1)
                
        except Exception as e:
            console.print(f"[red]Error installing completion: {e}[/red]")
            raise typer.Exit(1)
    
    else:
        # Default: show help for completion command
        console.print("[yellow]Use --show to display completion script or --install to install it.[/yellow]")
        console.print(f"[dim]Detected shell: {shell}[/dim]")


def version_callback(value: bool) -> None:
    """Version callback function."""
    if value:
        version = get_version()
        console.print(f"aditi version {version}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
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
    if ctx.invoked_subcommand is None:
        # No subcommand was invoked, show help
        console.print(ctx.get_help())
        raise typer.Exit(2)


if __name__ == "__main__":
    app()