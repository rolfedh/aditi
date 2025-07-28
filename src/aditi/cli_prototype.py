#!/usr/bin/env python3
"""Aditi CLI prototype matching the phase-2 mockup specification."""

import typer
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

app = typer.Typer(
    name="aditi",
    help="AsciiDoc DITA Integration - Prepare AsciiDoc files for migration to DITA",
    add_completion=False,
    rich_markup_mode="rich",
    pretty_exceptions_show_locals=False,
    context_settings={"help_option_names": ["--help"]},
)

console = Console()

# Version info
__version__ = "0.1.0"


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        console.print(f"aditi version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-V",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
):
    """
    AsciiDoc DITA Integration - Prepare AsciiDoc files for migration to DITA
    
    [bold yellow]IMPORTANT:[/bold yellow]
    - cd to the root directory of your repository before running aditi commands.
    - Create a working branch with the latest changes in it.
    """
    pass


@app.command()
def init():
    """Initialize Vale configuration for AsciiDocDITA rules."""
    console.print("\n[bold green]Initializing Vale configuration...[/bold green]\n")
    
    # Simulate the initialization process shown in mockup
    console.print("[17:21:26] INFO     Existing .vale.ini backed up to .vale.ini.backup.20250727172126")
    console.print("           INFO     Created Vale configuration at .vale.ini")
    console.print("           INFO     Downloading AsciiDocDITA styles...")
    console.print("[17:21:27] INFO     Successfully downloaded AsciiDocDITA v0.2.0")
    console.print("           INFO     Vale configuration initialized successfully\n")
    
    console.print("[bold green]✓[/bold green] Vale initialized with AsciiDocDITA rules")
    console.print("\nNext steps:")
    console.print("  • Run [bold]aditi journey[/bold] to start an interactive migration journey")
    console.print("  • Run [bold]aditi check[/bold] to check files for DITA compatibility issues")


@app.command()
def journey():
    """Start an interactive journey to migrate AsciiDoc files to DITA."""
    console.print("\n[bold blue]Welcome to the Aditi Migration Journey![/bold blue]\n")
    
    # Check for Vale configuration
    console.print("Checking Vale configuration... ", end="")
    console.print("[green]✓ Found[/green]\n")
    
    console.print("📁 Repository: /home/sarah/docs/product-docs")
    console.print("🌿 Current branch: feature/dita-migration")
    console.print("📄 AsciiDoc files found: 52\n")
    
    console.print("[bold]Ready to start?[/bold] This journey will:")
    console.print("  1. Run prerequisite checks (ContentType)")
    console.print("  2. Check and fix Error-level issues")
    console.print("  3. Check and fix Warning-level issues")
    console.print("  4. Check and fix Suggestion-level issues")
    console.print("  5. Create a pull request with all changes\n")
    
    console.print("[dim]Press Enter to continue or Ctrl+C to exit[/dim]")


@app.command()
def check(
    path: Optional[str] = typer.Argument(None, help="Path to check (defaults to current directory)"),
    rule: Optional[str] = typer.Option(None, "--rule", "-r", help="Specific rule to check"),
):
    """Check AsciiDoc files for DITA compatibility issues."""
    check_path = path or "."
    
    console.print(f"\n[bold]Checking AsciiDoc files in:[/bold] {check_path}")
    
    if rule:
        console.print(f"[bold]Rule:[/bold] {rule}\n")
    else:
        console.print("[bold]Rules:[/bold] All AsciiDocDITA rules\n")
    
    # Simulate check output
    console.print("Running Vale with AsciiDocDITA rules...")
    console.print("\n[yellow]⚠[/yellow]  assemblies/assembly_configuring.adoc")
    console.print("   16:1  [red]error[/red]    Missing content type attribute    AsciiDocDITA.ContentType")
    console.print("\n[yellow]⚠[/yellow]  modules/proc_installing.adoc")
    console.print("   1:1   [red]error[/red]    Missing content type attribute    AsciiDocDITA.ContentType")
    console.print("\n[green]✓[/green]  modules/con_prerequisites.adoc")
    console.print("\n[bold]Summary:[/bold] 2 errors, 0 warnings in 3 files")


@app.command()
def fix(
    path: Optional[str] = typer.Argument(None, help="Path to fix (defaults to current directory)"),
    rule: Optional[str] = typer.Option(None, "--rule", "-r", help="Specific rule to fix"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be fixed without making changes"),
):
    """Fix deterministic DITA compatibility issues in AsciiDoc files."""
    fix_path = path or "."
    
    console.print(f"\n[bold]Fixing deterministic issues in:[/bold] {fix_path}")
    
    if rule:
        console.print(f"[bold]Rule:[/bold] {rule}")
    else:
        console.print("[bold]Rules:[/bold] All deterministic AsciiDocDITA rules")
    
    if dry_run:
        console.print("[yellow]Mode: DRY RUN (no changes will be made)[/yellow]\n")
    else:
        console.print("\n")
    
    # Simulate fix output
    console.print("Scanning for deterministic fixes...")
    console.print("\n[bold]EntityReference[/bold] (Fully deterministic)")
    console.print("  [green]✓[/green] modules/ref_api.adoc: Replaced &rarr; with →")
    console.print("  [green]✓[/green] modules/ref_api.adoc: Replaced &nbsp; with &#160;")
    console.print("\n[bold]ContentType[/bold] (Partially deterministic)")
    console.print("  [yellow]![/yellow] assemblies/assembly_configuring.adoc: Added placeholder")
    console.print("     [dim]// TODO: Review and set content type to one of:[/dim]")
    console.print("     [dim]// ASSEMBLY, CONCEPT, PROCEDURE, REFERENCE, SNIPPET[/dim]")
    console.print("     [dim]:_mod-docs-content-type: <PLACEHOLDER>[/dim]")
    
    if not dry_run:
        console.print("\n[bold green]✓[/bold green] Fixed 3 issues in 2 files")
        console.print("\nRun [bold]git diff[/bold] to review changes")


if __name__ == "__main__":
    app()