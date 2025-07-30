"""Fix command implementation for applying DITA compatibility fixes."""

from pathlib import Path
from typing import List, Optional

import questionary
import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table

from ..config import ConfigManager
from ..vale_container import ValeContainer
from ..processor import RuleProcessor
from ..rules import FixType

console = Console()


def fix_command(
    paths: Optional[List[Path]] = None,
    rule: Optional[str] = None,
    interactive: bool = True,
    dry_run: bool = False,
) -> None:
    """Fix deterministic DITA compatibility issues in AsciiDoc files.
    
    Args:
        paths: Paths to fix (files or directories)
        rule: Specific rule to apply fixes for
        interactive: Whether to run in interactive mode
        dry_run: Whether to show what would be fixed without applying
    """
    # Initialize configuration
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    # Determine which paths to process
    if not paths:
        # Use configured directories
        if not config.allowed_paths and not config.selected_directories:
            console.print("[yellow]No paths configured for fixing.[/yellow]")
            console.print("To fix this, run: [bold]aditi journey[/bold] to configure your repository paths.")
            raise typer.Exit(1)
        paths_to_fix = config.allowed_paths or config.selected_directories
    else:
        # Validate paths against configuration
        paths_to_fix = []
        skipped_paths = []
        for path in paths:
            if config.is_path_allowed(path):
                paths_to_fix.append(path)
            else:
                skipped_paths.append(path)
                
        # Show informative message about skipped paths
        if skipped_paths:
            console.print(f"[yellow]Warning: Skipping {len(skipped_paths)} path(s) not in allowed directories:[/yellow]") 
            for path in skipped_paths:
                console.print(f"  • {path}")
            if config.allowed_paths:
                console.print(f"\n[dim]Allowed paths:[/dim]")
                for allowed in config.allowed_paths:
                    console.print(f"  • {allowed}")
            console.print("\nTo add paths, run: [bold]aditi journey[/bold] to configure repository access.")
                
    if not paths_to_fix:
        console.print("[red]No valid paths to fix.[/red]")
        if paths:
            console.print("All specified paths were outside the configured allowed directories.")
            console.print("Run [bold]aditi journey[/bold] to add the paths you want to fix.")
        raise typer.Exit(1)
        
    # Collect all .adoc files
    adoc_files = []
    for path in paths_to_fix:
        if path.is_file() and path.suffix == ".adoc":
            adoc_files.append(path)
        elif path.is_dir():
            # Find all .adoc files recursively, excluding symlinks
            for adoc_file in path.rglob("*.adoc"):
                if not adoc_file.is_symlink():
                    adoc_files.append(adoc_file)
                    
    if not adoc_files:
        console.print("[yellow]No .adoc files found to fix.[/yellow]")
        raise typer.Exit(0)
    
    # Initialize Vale container
    try:
        vale_container = ValeContainer()
        vale_container.ensure_image_exists()
        
        # Initialize processor
        processor = RuleProcessor(vale_container, config)
        
        # Run analysis first
        console.print(f"\n🔍 Analyzing {len(adoc_files)} AsciiDoc files...")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Running Vale analysis...", total=None)
            check_result = processor.process_files(adoc_files, dry_run=True)
            progress.stop()
        
        if not check_result.violations_found:
            console.print("\n✅ No issues found! Your files are ready for DITA migration.")
            return
        
        # Filter violations by rule if specified
        if rule:
            violations = [v for v in check_result.violations_found if v.rule_name == rule]
            if not violations:
                console.print(f"\n[yellow]No {rule} issues found.[/yellow]")
                return
        else:
            violations = check_result.violations_found
        
        # Group violations by fix type
        fixable_violations = []
        non_fixable_violations = []
        
        for violation in violations:
            rule_instance = processor.rule_registry.get_rule_for_violation(violation)
            if rule_instance and rule_instance.fix_type in [FixType.FULLY_DETERMINISTIC, FixType.PARTIALLY_DETERMINISTIC]:
                fixable_violations.append(violation)
            else:
                non_fixable_violations.append(violation)
        
        # Show summary
        console.print(f"\n📊 Fix Summary\n")
        console.print(f"Total issues found: {len(violations)}")
        console.print(f"Can be auto-fixed: {len(fixable_violations)}")
        console.print(f"Manual intervention required: {len(non_fixable_violations)}")
        
        if not fixable_violations:
            console.print("\n[yellow]No auto-fixable issues found.[/yellow]")
            return
        
        # Interactive mode - ask for confirmation
        if interactive and not dry_run:
            console.print("\n" + "─" * 50 + "\n")
            
            # Show breakdown by rule
            violations_by_rule = processor.vale_parser.group_by_rule(fixable_violations)
            
            table = Table(title="Auto-Fixable Issues")
            table.add_column("Rule", style="cyan")
            table.add_column("Fix Type", style="yellow")
            table.add_column("Count", style="green")
            
            for rule_name, rule_violations in violations_by_rule.items():
                rule_instance = processor.rule_registry.get_rule(rule_name)
                if rule_instance:
                    fix_type = "Fully Deterministic" if rule_instance.fix_type == FixType.FULLY_DETERMINISTIC else "Partially Deterministic"
                    table.add_row(rule_name, fix_type, str(len(rule_violations)))
            
            console.print(table)
            console.print()
            
            # Ask for confirmation
            proceed = questionary.confirm(
                f"Apply {len(fixable_violations)} auto-fixes?",
                default=True
            ).ask()
            
            if not proceed:
                console.print("[yellow]Fix cancelled.[/yellow]")
                return
        
        # Apply fixes
        if not dry_run:
            console.print(f"\n⚡ Applying fixes...\n")
            
            # Get unique files with fixable violations
            files_to_fix = list(set(v.file_path for v in fixable_violations))
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=console
            ) as progress:
                task = progress.add_task("Processing files...", total=len(files_to_fix))
                
                total_fixes_applied = 0
                files_modified = 0
                
                for file_path in files_to_fix:
                    # Process just this file with rule filter
                    result = processor.process_files([file_path], dry_run=False, rule_filter=rule)
                    
                    if result.fixes_applied:
                        total_fixes_applied += len(result.fixes_applied)
                        files_modified += 1
                    
                    progress.update(task, advance=1)
            
            # Show results
            console.print(f"\n✅ Fix complete!\n")
            console.print(f"Files modified: {files_modified}")
            console.print(f"Fixes applied: {total_fixes_applied}")
            
            if total_fixes_applied > 0:
                console.print(Panel(
                    "💡 [bold]Next steps:[/bold]\n"
                    "1. Review the changes made by Aditi\n"
                    "2. Search for `TBD` placeholders and replace with appropriate values\n"
                    "3. Run `aditi check` to verify remaining issues\n"
                    "4. Commit your changes to version control",
                    border_style="green"
                ))
        else:
            # Dry run - show what would be fixed
            console.print("\n🔍 [bold]Dry Run Results[/bold] (no changes made)\n")
            
            violations_by_file = processor.vale_parser.group_by_file(fixable_violations)
            
            for file_path, file_violations in list(violations_by_file.items())[:5]:
                try:
                    rel_path = file_path.relative_to(Path.cwd())
                except ValueError:
                    rel_path = file_path
                console.print(f"[cyan]{rel_path}[/cyan]")
                
                for violation in file_violations[:3]:
                    rule_instance = processor.rule_registry.get_rule_for_violation(violation)
                    if rule_instance:
                        console.print(f"  Line {violation.line}: {violation.rule_name} - {violation.message}")
                
                if len(file_violations) > 3:
                    console.print(f"  ... and {len(file_violations) - 3} more")
                console.print()
            
            if len(violations_by_file) > 5:
                console.print(f"... and {len(violations_by_file) - 5} more files\n")
            
            console.print(f"[yellow]Run without --dry-run to apply these fixes.[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Error during fix:[/red] {e}")
        raise typer.Exit(1)
    finally:
        # Cleanup Vale container
        if 'vale_container' in locals():
            vale_container.cleanup()