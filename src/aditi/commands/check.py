"""Check command implementation for Aditi CLI."""

from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

from ..config import ConfigManager
from ..vale_container import ValeContainer
from ..processor import RuleProcessor
from ..rules import FixType

console = Console()


def check_command(
    paths: List[Path] = typer.Argument(
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
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed violation information",
    ),
) -> None:
    """Check AsciiDoc files for DITA compatibility issues.
    
    This command runs Vale with AsciiDocDITA rules to identify issues
    that need to be fixed before migration to DITA.
    """
    # Initialize configuration
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    # If no configuration exists, create one automatically
    if not config_manager.config_file.exists():
        console.print("📝 Creating configuration for the first time...")
        console.print("🔍 Scanning for AsciiDoc documentation directories...")
        config = config_manager.create_default_config(scan_for_docs=True)
        
        if config.allowed_paths:
            console.print(f"\n✅ Found documentation in {len(config.allowed_paths)} location(s):")
            for path in config.allowed_paths:
                console.print(f"  • {path}")
        else:
            console.print("\n[yellow]No .adoc files found in subdirectories.[/yellow]")
            console.print("You can specify paths directly: [bold]aditi check path/to/docs[/bold]")
    
    # Determine which paths to check
    if not paths:
        # Use configured directories
        if not config.allowed_paths:
            console.print("[yellow]No paths configured for checking.[/yellow]")
            console.print("To add paths, run: [bold]aditi journey[/bold] or specify paths directly:")
            console.print("  [bold]aditi check path/to/docs[/bold]")
            raise typer.Exit(1)
        paths_to_check = config.allowed_paths
    else:
        # If paths are provided and no config was just created, add them to allowed paths
        skipped_paths = []
        if not config.allowed_paths or all(not config.is_path_allowed(p) for p in paths):
            console.print("\n🔧 Adding specified paths to configuration...")
            for path in paths:
                if path.exists():
                    resolved_path = path.resolve()
                    if resolved_path not in config.allowed_paths:
                        config.allowed_paths.append(resolved_path)
                        console.print(f"  ✅ Added: {path}")
            config_manager.save_config(config)
            paths_to_check = paths
        else:
            # Validate paths against configuration
            paths_to_check = []
            for path in paths:
                if config.is_path_allowed(path):
                    paths_to_check.append(path)
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
                
    if not paths_to_check:
        console.print("[red]No valid paths to check.[/red]")
        if paths:
            console.print("All specified paths were outside the configured allowed directories.")
            console.print("Run [bold]aditi journey[/bold] to add the paths you want to check.")
        raise typer.Exit(1)
        
    # Collect all .adoc files with validation
    adoc_files = []
    invalid_files = []
    
    for path in paths_to_check:
        if path.is_file() and path.suffix == ".adoc":
            # Validate file is readable and not empty
            try:
                if path.stat().st_size == 0:
                    invalid_files.append(f"{path} (empty file)")
                    continue
                # Try to read first few bytes to ensure it's readable
                with open(path, 'r', encoding='utf-8') as f:
                    f.read(100)  # Just check if we can read the start
                adoc_files.append(path)
            except (OSError, UnicodeDecodeError, PermissionError) as e:
                invalid_files.append(f"{path} ({e})")
        elif path.is_dir():
            # Find all .adoc files recursively, handling symlinks based on config
            for adoc_file in path.rglob("*.adoc"):
                try:
                    # Check if file is accessible and not empty
                    if adoc_file.stat().st_size == 0:
                        invalid_files.append(f"{adoc_file} (empty file)")
                        continue
                        
                    if config.ignore_symlinks and adoc_file.is_symlink():
                        continue
                        
                    # Try to read first few bytes to ensure it's readable
                    with open(adoc_file, 'r', encoding='utf-8') as f:
                        f.read(100)  # Just check if we can read the start
                    adoc_files.append(adoc_file)
                except (OSError, UnicodeDecodeError, PermissionError) as e:
                    invalid_files.append(f"{adoc_file} ({e})")
    
    # Report any invalid files found
    if invalid_files:
        console.print(f"[yellow]Warning: Skipping {len(invalid_files)} invalid file(s):[/yellow]")
        for invalid_file in invalid_files[:5]:  # Show first 5
            console.print(f"  • {invalid_file}")
        if len(invalid_files) > 5:
            console.print(f"  ... and {len(invalid_files) - 5} more")
                    
    if not adoc_files:
        console.print("[yellow]No valid .adoc files found to check.[/yellow]")
        if invalid_files:
            console.print("All found .adoc files had issues (empty, unreadable, or permission errors).")
        raise typer.Exit(0)
        
    # Initialize Vale container
    try:
        vale_container = ValeContainer()
        # Ensure Vale image exists
        vale_container.ensure_image_exists()
            
        # Initialize processor
        processor = RuleProcessor(vale_container, config)
        
        # Process files (dry run mode for check command)
        console.print(f"\n🔍 Analyzing AsciiDoc files in {', '.join(str(p) for p in paths_to_check)}")
        result = processor.process_files(adoc_files, dry_run=True)
        
        # Display results
        if result.errors:
            console.print("\n[red]Errors occurred during processing:[/red]")
            for error in result.errors:
                console.print(f"  • {error}")
                
        if not result.violations_found:
            console.print("\n✅ No issues found! Your files are ready for DITA migration.")
            return
            
        # Display detailed results if verbose
        if verbose:
            _display_verbose_results(result, processor)
        else:
            # Display summary
            processor.display_summary(result)
            
    except Exception as e:
        console.print(f"[red]Error during check:[/red] {e}")
        raise typer.Exit(1)
    finally:
        # Cleanup Vale container
        if 'vale_container' in locals():
            vale_container.cleanup()


def _display_verbose_results(result, processor):
    """Display verbose results with detailed violation information."""
    console.print("\n📊 Detailed Analysis Results\n")
    
    # Group violations by rule
    parser = processor.vale_parser
    violations_by_rule = parser.group_by_rule(result.violations_found)
    
    # Get all rules for descriptions
    rules = processor.rule_registry.get_all_rules()
    rule_map = {rule.name: rule for rule in rules}
    
    for rule_name, violations in violations_by_rule.items():
        rule = rule_map.get(rule_name)
        
        # Determine fix type emoji and text
        if rule:
            if rule.fix_type == FixType.FULLY_DETERMINISTIC:
                emoji = "🔴"
                fix_text = "Fix: Auto-fix available"
            elif rule.fix_type == FixType.PARTIALLY_DETERMINISTIC:
                emoji = "🟡"
                fix_text = "Fix: Partial auto-fix with placeholders"
            else:
                emoji = "🔵"
                fix_text = "Fix: Manual intervention required"
        else:
            emoji = "❓"
            fix_text = "Fix: Unknown"
            
        console.print(f"{emoji} [bold]{rule_name}[/bold] ({len(violations)} {'issue' if len(violations) == 1 else 'issues'})")
        
        if rule and rule.description:
            console.print(f"{rule.description}")
            
        console.print(fix_text)
        
        # Show violation details
        table = Table(show_header=True, header_style="bold")
        table.add_column("File", style="cyan")
        table.add_column("Line", style="yellow")
        table.add_column("Message", style="white")
        
        # Limit to first 10 violations in non-verbose mode
        display_violations = violations[:10] if len(violations) > 10 else violations
        
        for violation in display_violations:
            rel_path = violation.file_path.relative_to(Path.cwd())
            table.add_row(
                str(rel_path),
                str(violation.line),
                violation.message
            )
            
        console.print(table)
        
        if len(violations) > 10:
            console.print(f"  ... and {len(violations) - 10} more\n")
        else:
            console.print()
            
    # Show summary
    processor.display_summary(result)