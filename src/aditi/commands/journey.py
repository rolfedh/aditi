"""Journey command implementation for guided DITA preparation workflow."""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any

import questionary
import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table

from ..config import ConfigManager
from ..scanner import DirectoryScanner
from ..vale_container import ValeContainer
from ..processor import RuleProcessor
from ..rules import FixType

console = Console()


def get_session_age(session_started: Optional[str]) -> Optional[str]:
    """Get human-readable age of session.
    
    Args:
        session_started: ISO timestamp of session start
        
    Returns:
        Human-readable age string or None if no session
    """
    if not session_started:
        return None
        
    try:
        start_time = datetime.fromisoformat(session_started)
        age = datetime.now() - start_time
        
        if age.days > 0:
            return f"{age.days} day{'s' if age.days > 1 else ''}"
        elif age.seconds >= 3600:
            hours = age.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''}"
        elif age.seconds >= 60:
            minutes = age.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''}"
        else:
            return "less than a minute"
    except Exception:
        return "unknown time"


def display_session_info(session) -> None:
    """Display current session information."""
    if not session.session_started:
        return
        
    age = get_session_age(session.session_started)
    console.print(f"\n📋 [bold]Found existing journey session[/bold] ({age} old)")
    
    if session.journey_progress:
        repo = session.journey_progress.get("repository_root", "Unknown")
        console.print(f"   Repository: [cyan]{repo}[/cyan]")
    
    if session.total_rules and session.applied_rules:
        progress = len(session.applied_rules)
        console.print(f"   Progress: {progress} of {session.total_rules} rules completed")
        
        if session.current_rule:
            console.print(f"   Last rule: {session.current_rule}")
    
    # TODO: Add file count when we implement file tracking
    console.print()


def backup_session(config_manager: ConfigManager) -> None:
    """Backup current session to session-backups directory."""
    import json
    import shutil
    
    session_file = config_manager.session_file
    if not session_file.exists():
        return
        
    # Create backup directory
    backup_dir = config_manager.config_dir / "session-backups"
    backup_dir.mkdir(exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    backup_file = backup_dir / f"session-{timestamp}.json"
    
    # Copy session file
    shutil.copy2(session_file, backup_file)
    
    # Keep only last 5 backups
    backups = sorted(backup_dir.glob("session-*.json"))
    if len(backups) > 5:
        for old_backup in backups[:-5]:
            old_backup.unlink()
    
    console.print(f"[dim]Session backed up to {backup_file.name}[/dim]")


def validate_session(session) -> List[str]:
    """Validate session data and return list of validation errors.
    
    Args:
        session: SessionState to validate
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    # Check if repository path exists
    if session.journey_progress:
        repo_path = session.journey_progress.get("repository_root")
        if repo_path:
            repo_path = Path(repo_path)
            if not repo_path.exists():
                errors.append(f"Repository path no longer exists: {repo_path}")
            elif not repo_path.is_dir():
                errors.append(f"Repository path is not a directory: {repo_path}")
            elif not (repo_path / ".git").exists():
                errors.append(f"Repository path is no longer a git repository: {repo_path}")
                
            # Check if we're in the same directory
            if repo_path.exists() and repo_path != Path.cwd():
                errors.append(f"Current directory differs from session repository: {Path.cwd()}")
    
    # Check if selected directories still exist
    if session.journey_progress:
        dirs = session.journey_progress.get("selected_directories", [])
        missing_dirs = []
        for dir_path in dirs:
            if not Path(dir_path).exists():
                missing_dirs.append(dir_path)
        if missing_dirs:
            errors.append(f"Some selected directories no longer exist: {', '.join(missing_dirs[:3])}")
    
    # TODO: Add git branch validation when git integration is added
    
    return errors


# Rule processing order as defined in the mockup
RULE_PROCESSING_ORDER = [
    # Prerequisites - must run first
    ("ContentType", "warning", "Without a clear content type definition, the Vale style cannot reliably report type-specific issues for modules such as TaskSection, TaskExample, TaskDuplicate, TaskStep, and TaskTitle."),

    # Error-level rules
    ("EntityReference", "error", "DITA 1.3 supports five character entity references defined in the XML standard: &amp;, &lt;, &gt;, &apos;, and &quot;. Replace any other character entity references with an appropriate built-in AsciiDoc attribute."),

    # Warning-level rules
    ("ExampleBlock", "warning", "DITA 1.3 allows the <example> element to appear only within the main body of the topic. Do not use example blocks in sections, within other blocks, or as part of lists."),
    ("NestedSection", "warning", "DITA 1.3 allows the <section> element to appear only within the main body of the topic. If a level 2 section is needed, move it to a separate file."),
    ("AdmonitionTitle", "warning", "DITA 1.3 does not support titles on note elements. Consider restructuring admonition blocks with titles."),
    ("AuthorLine", "warning", "Add an empty line after the document title to improve DITA conversion. This helps separate title metadata from content."),
    ("BlockTitle", "warning", "DITA 1.3 only supports titles on specific block elements. Consider restructuring or removing unsupported block titles."),
    ("CrossReference", "warning", "DITA cross-references should be limited to the current document. External cross-references may need restructuring."),
    ("DiscreteHeading", "warning", "Discrete headings don't have direct DITA equivalents. Consider using regular sections or restructuring content."),
    ("EquationFormula", "warning", "DITA conversion doesn't support LaTeX or AsciiMath equations. Consider converting to images or MathML."),
    ("LineBreak", "warning", "DITA prefers semantic markup over manual line breaks. Consider using paragraphs or other block elements."),
    ("LinkAttribute", "warning", "DITA may not resolve attribute references in link URLs correctly. Use direct URLs or restructure links."),
    ("PageBreak", "warning", "DITA doesn't support page breaks like print formats. Consider restructuring content into logical sections or topics."),
    ("RelatedLinks", "warning", "DITA has specific requirements for related links formatting. Ensure links follow DITA conventions for proper conversion."),
    ("SidebarBlock", "warning", "DITA doesn't have direct sidebar equivalents. Consider restructuring into separate topics or sections."),
    ("TableFooter", "warning", "DITA 1.3 doesn't support table footers. Consider moving footer content to table caption or following content."),
    ("ThematicBreak", "warning", "DITA doesn't have direct thematic break equivalents. Consider restructuring content into logical sections or topics."),

    # Suggestion-level rules
    ("TaskSection", "suggestion", "DITA 1.3 does not allow sections in a task topic. If a section is needed, move it to a separate file."),
    ("TaskExample", "suggestion", "DITA 1.3 allows only one <example> element in a task topic. If multiple examples are needed, combine them in a single example block."),
    ("TaskStep", "suggestion", "DITA task steps should contain simple instructions. Complex content may need to be moved to separate topics or simplified."),
    ("TaskTitle", "suggestion", "DITA task titles should clearly describe the task using imperative verbs (e.g., 'Install the software', 'Configure settings')."),
    ("TaskDuplicate", "suggestion", "DITA task topics should avoid duplicate content. Consider consolidating redundant steps or using cross-references."),
    ("ShortDescription", "suggestion", "DITA topics require a short description element. In AsciiDoc, add [role=\"_abstract\"] above a paragraph to create one."),
    ("AttributeReference", "suggestion", "Informational: Lists attribute references that may need attention during DITA conversion."),
    ("ConditionalCode", "suggestion", "Informational: Identifies conditional statements that may need special handling during DITA conversion."),
    ("IncludeDirective", "suggestion", "Informational: Lists include directives that may need attention during DITA conversion."),
    ("TagDirective", "suggestion", "Informational: Identifies tag directives that may need attention during DITA conversion."),
]


def journey_command(dry_run: bool = False, clear: bool = False, status: bool = False) -> None:
    """Start an interactive journey to prepare AsciiDoc files for DITA migration."""
    config_manager = ConfigManager()
    
    # Handle --clear flag
    if clear:
        session = config_manager.load_session()
        if session.session_started:
            console.print("\n🗑️  [bold]Clearing journey session[/bold]")
            display_session_info(session)
            
            confirm = questionary.confirm(
                "Are you sure you want to clear this session?",
                default=False
            ).ask()
            
            if confirm:
                backup_session(config_manager)
                config_manager.clear_session()
                console.print("[green]✓ Session cleared and backed up.[/green]")
            else:
                console.print("[yellow]Cancelled.[/yellow]")
        else:
            console.print("[yellow]No active journey session to clear.[/yellow]")
        return
    
    # Handle --status flag
    if status:
        session = config_manager.load_session()
        if session.session_started:
            display_session_info(session)
            
            # Show more detailed status
            if session.journey_state == "configured":
                console.print("\n[bold]Session Details:[/bold]")
                
                # Show repository info
                if session.journey_progress:
                    dirs = session.journey_progress.get("selected_directories", [])
                    if dirs:
                        console.print(f"   Selected directories: {len(dirs)}")
                        for dir_path in dirs[:3]:  # Show first 3
                            console.print(f"     • {dir_path}")
                        if len(dirs) > 3:
                            console.print(f"     ... and {len(dirs) - 3} more")
                
                # Show rules progress
                if session.applied_rules:
                    console.print(f"\n   [bold]Completed rules:[/bold]")
                    for rule in session.applied_rules[-5:]:  # Show last 5
                        console.print(f"     ✓ {rule}")
                    if len(session.applied_rules) > 5:
                        console.print(f"     ... and {len(session.applied_rules) - 5} more")
                
                # Show next rule
                if session.current_rule:
                    console.print(f"\n   [bold]Next rule:[/bold] {session.current_rule}")
                elif session.total_rules and len(session.applied_rules) < session.total_rules:
                    # Find next rule
                    applied_set = set(session.applied_rules)
                    for rule_name, _, _ in RULE_PROCESSING_ORDER:
                        if rule_name not in applied_set:
                            console.print(f"\n   [bold]Next rule:[/bold] {rule_name}")
                            break
                
                console.print(f"\n[dim]Run 'aditi journey' to resume[/dim]")
            else:
                console.print("\n[yellow]Session exists but configuration not complete.[/yellow]")
                console.print("[dim]Run 'aditi journey' to continue setup[/dim]")
        else:
            console.print("[yellow]No active journey session.[/yellow]")
            console.print("[dim]Run 'aditi journey' to start[/dim]")
        return
    
    if dry_run:
        console.print(Panel.fit(
            "🔍 [bold]Aditi Journey - Dry Run Mode[/bold]\n\n"
            "This will preview what the journey would do:\n"
            "  ✓ Show repository configuration options\n"
            "  ✓ Display what fixes would be applied\n"
            "  ✓ Preview rule processing without changes\n\n"
            "[dim]No files will be modified in dry-run mode.[/dim]",
            title="Aditi Journey (Dry Run)",
            border_style="yellow"
        ))
    else:
        console.print(Panel.fit(
            "🚀 [bold]Welcome to Aditi's guided journey![/bold]\n\n"
            "This interactive workflow will help you:\n"
            "  ✓ Configure Aditi for your repository\n"
            "  ✓ Automatically fix or flag issues for you\n"
            "  ✓ Prompt you to review automatic fixes\n"
            "  ✓ Prompt you to fix flagged issues",
            title="Aditi Journey",
            border_style="green"
        ))

    if dry_run:
        # In dry-run mode, show what would be done but don't actually do it
        console.print("\n[yellow]Dry-run mode: Showing what would be configured and processed[/yellow]\n")
        
        # Show current directory and potential repository detection
        current_dir = Path.cwd()
        console.print(f"📁 Would analyze directory: [cyan]{current_dir}[/cyan]")
        
        # Check for AsciiDoc files
        adoc_files = list(current_dir.rglob("*.adoc"))
        if adoc_files:
            console.print(f"📝 Found {len(adoc_files)} AsciiDoc files that would be analyzed")
            for file in adoc_files[:5]:  # Show first 5
                console.print(f"   • {file.relative_to(current_dir)}")
            if len(adoc_files) > 5:
                console.print(f"   ... and {len(adoc_files) - 5} more")
        else:
            console.print("📝 No AsciiDoc files found in current directory")
        
        # Show what rules would be processed
        console.print(f"\n🔍 Would process {len(RULE_PROCESSING_ORDER)} AsciiDocDITA rules:")
        for rule, level, desc in RULE_PROCESSING_ORDER:
            emoji = "🔴" if level == "error" else "🟡" if level == "warning" else "🔵"
            console.print(f"   {emoji} {rule} ({level})")
        
        console.print("\n[dim]To actually perform these actions, run without --dry-run[/dim]")
        return
    
    # Normal interactive mode
    config_manager = ConfigManager()
    session = config_manager.load_session()
    
    # Check if we have an existing session
    if session.session_started and session.journey_state:
        # Validate session before showing it
        validation_errors = validate_session(session)
        
        display_session_info(session)
        
        # Show validation warnings if any
        if validation_errors:
            console.print("\n⚠️  [yellow]Session validation warnings:[/yellow]")
            for error in validation_errors:
                console.print(f"   • {error}")
            console.print()
        
        # Add age warning for old sessions
        age = get_session_age(session.session_started)
        if age and ("day" in age and int(age.split()[0]) >= 7):
            console.print("⚠️  [yellow]Session is more than 7 days old. Repository may have changed significantly.[/yellow]\n")
        
        # Ask if they want to resume
        resume = questionary.confirm(
            "Resume from where you left off?",
            default=True if not validation_errors else False
        ).ask()
        
        if not resume:
            # Back up existing session before starting fresh
            backup_session(config_manager)
            config_manager.clear_session()
            session = config_manager.load_session()  # Get fresh session
            console.print("[yellow]Starting fresh journey. Previous session backed up.[/yellow]\n")
            
    # Phase 1: Repository Configuration  
    if not session.journey_state or session.journey_state != "configured":
        if not configure_repository():
            return

    # Phase 2: Rule Application Workflow
    completed = apply_rules_workflow()

    # Phase 3: Completion
    if completed:
        complete_journey()
    else:
        console.print("\n[yellow]Journey paused. Run 'aditi journey' again to resume.[/yellow]")


def configure_repository() -> bool:
    """Configure repository and directory selection.

    Returns:
        True if configuration was successful, False otherwise
    """
    # Initialize configuration manager
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    # If no configuration exists, create one automatically
    if not config_manager.config_file.exists():
        console.print("\n📝 Creating configuration for the first time...")
        console.print("🔍 Scanning for AsciiDoc documentation directories...")
        config = config_manager.create_default_config(scan_for_docs=True)
        
        if config.allowed_paths:
            console.print(f"\n✅ Found documentation in {len(config.allowed_paths)} location(s):")
            for path in config.allowed_paths:
                console.print(f"  • {path}")
        else:
            console.print("\n[yellow]No .adoc files found in subdirectories.[/yellow]")
            console.print("We'll help you configure the paths in the next steps.")
    
    # Check if we're in a git repository root
    current_dir = Path.cwd()
    console.print(f"\n📁 Current directory: [cyan]{current_dir}[/cyan]")

    # Check for .git directory
    if not (current_dir / ".git").exists():
        console.print("[yellow]Warning: No .git directory found. This may not be a repository root.[/yellow]")

    # Ask if this is the repository root
    is_root = questionary.confirm(
        "Is this the root directory of your repository?",
        default=True
    ).ask()

    if not is_root:
        console.print(
            "\n[red]Please cd to the root directory of your repository and rerun the 'aditi journey' command.[/red]"
        )
        raise typer.Exit(1)

    # Ask about path selection method
    console.print("\n📂 Directory Selection")
    path_choice = questionary.select(
        "How would you like to specify directories to scan?",
        choices=[
            "Use all auto-detected paths",
            "Review and customize auto-detected paths",
            "Enter custom directory paths"
        ]
    ).ask()

    if path_choice == "Use all auto-detected paths":
        # Use all directories with .adoc files
        selected_dirs = None
    elif path_choice == "Review and customize auto-detected paths":
        selected_dirs = select_directories(current_dir)
        if not selected_dirs:
            console.print("[red]No directories selected. Exiting.[/red]")
            return False
    else:
        # Enter custom paths
        custom_paths = []
        console.print("\nEnter directory paths (relative to repository root).")
        console.print(f"[dim]Repository root: {current_dir}[/dim]")
        console.print("Press Enter with empty input when done.\n")
        
        while True:
            path_str = questionary.text("Directory path:").ask()
            if not path_str:
                break
                
            # Clean up the path - remove leading slash if present
            path_str = path_str.strip()
            if path_str.startswith('/'):
                path_str = path_str[1:]
            
            path = Path(path_str)
            full_path = current_dir / path
            
            if full_path.exists() and full_path.is_dir():
                custom_paths.append(path)
                console.print(f"  ✓ Added: {path}")
            else:
                console.print(f"  [red]✗ Invalid path: {path}[/red]")
                console.print(f"    [dim]Looking for: {full_path}[/dim]")
                if not full_path.exists():
                    console.print(f"    [dim]Path does not exist[/dim]")
                    # Check what directories DO exist to help the user
                    parent = full_path.parent
                    while parent != current_dir and not parent.exists():
                        parent = parent.parent
                    if parent.exists() and parent != current_dir:
                        console.print(f"    [dim]Last existing directory: {parent}[/dim]")
                        # List subdirectories to help
                        try:
                            subdirs = [d.name for d in parent.iterdir() if d.is_dir()][:5]
                            if subdirs:
                                console.print(f"    [dim]Available subdirectories: {', '.join(subdirs)}[/dim]")
                        except:
                            pass
                elif not full_path.is_dir():
                    console.print(f"    [dim]Path exists but is not a directory[/dim]")
        
        if not custom_paths:
            console.print("[red]No valid paths entered. Exiting.[/red]")
            return False
            
        selected_dirs = custom_paths

    # Save configuration
    save_configuration(current_dir, selected_dirs)

    # Workflow tip
    console.print(Panel(
        "💡 [bold]Workflow Tip:[/bold]\n"
        "Before starting, create a feature branch for your changes.\n"
        "This keeps your work organized and makes it easy to review.",
        border_style="blue"
    ))

    # Ready to start?
    ready = questionary.confirm(
        "Ready to start preparing your files?",
        default=True
    ).ask()

    if not ready:
        console.print("[yellow]Journey cancelled.[/yellow]")
        return False

    console.print("\n✓ Great! Let's start.\n")
    return True


def select_directories(root_path: Path) -> Optional[List[Path]]:
    """Interactive directory selection.

    Args:
        root_path: Repository root path

    Returns:
        List of selected directory paths or None if cancelled
    """
    console.print("\n🔍 Scanning for AsciiDoc files...")

    # Scan for directories
    scanner = DirectoryScanner(ignore_symlinks=True)
    adoc_dirs = scanner.scan_for_adoc_files(root_path)

    if not adoc_dirs:
        console.print("[yellow]No AsciiDoc files found in the repository.[/yellow]")
        return []

    # Find documentation roots
    doc_roots = scanner.find_documentation_roots(adoc_dirs)

    # Prepare choices for questionary
    choices = []
    for path, direct_count, total_count in doc_roots:
        if direct_count == total_count:
            label = f"{path} ({total_count} .adoc files)"
        else:
            label = f"{path} ({total_count} .adoc files total, {direct_count} direct)"
        choices.append(questionary.Choice(title=label, value=str(path), checked=True))

    # Also add individual directories that aren't under any root
    all_roots = {str(path) for path, _, _ in doc_roots}
    for path, count in sorted(adoc_dirs.items()):
        if str(path) not in all_roots:
            choices.append(questionary.Choice(
                title=f"{path} ({count} .adoc files)",
                value=str(path),
                checked=False
            ))

    # Multi-select prompt
    selected = questionary.checkbox(
        "Detected documentation in (↑/↓ arrows to navigate, Space to select/deselect, Enter to confirm):",
        choices=choices
    ).ask()

    if selected is None:  # User cancelled
        return None

    # Convert back to Path objects
    selected_paths = [Path(p) for p in selected]

    # Ask about using detected paths or custom
    use_detected = questionary.select(
        "Use these auto-detected paths or specify custom directory?",
        choices=[
            "Use detected paths",
            "Enter custom directory paths"
        ]
    ).ask()

    if use_detected == "Enter custom directory paths":
        custom_paths = []
        console.print("\nEnter directory paths (relative to repository root).")
        console.print("Press Enter with empty input when done.\n")

        while True:
            path_str = questionary.text("Directory path:").ask()
            if not path_str:
                break

            path = Path(path_str)
            if (root_path / path).exists() and (root_path / path).is_dir():
                custom_paths.append(path)
                console.print(f"  ✓ Added: {path}")
            else:
                console.print(f"  [red]✗ Invalid path: {path}[/red]")

        selected_paths = custom_paths

    # Display selected directories
    if selected_paths:
        console.print("\n✓ Configuration saved to ~/aditi-data/config.json\n")
        console.print("Selected directories:")
        for path in selected_paths:
            count = adoc_dirs.get(path, 0)
            console.print(f"  • {path} ({count} .adoc files)")

    # Confirmation
    console.print()
    choice = questionary.select(
        "These directory selections look correct?",
        choices=[
            "Y = Yes, continue",
            "n = Exit",
            "r = Reconfigure directories"
        ],
        default="Y = Yes, continue"
    ).ask()

    if choice == "n = Exit":
        return None
    elif choice == "r = Reconfigure directories":
        return select_directories(root_path)  # Recursive call

    return selected_paths


def save_configuration(root_path: Path, selected_dirs: Optional[List[Path]]) -> None:
    """Save journey configuration.

    Args:
        root_path: Repository root path
        selected_dirs: Selected directories or None for all
    """
    config_manager = ConfigManager()
    config = config_manager.load_config()

    # Update configuration
    if selected_dirs is not None:
        config.selected_directories = [root_path / d for d in selected_dirs]
        config.allowed_paths = config.selected_directories
    else:
        # Use all directories
        config.selected_directories = []
        config.allowed_paths = [root_path]

    # Save repository info if not already configured
    repo_name = root_path.name
    if repo_name not in config.repositories:
        config.add_repository(repo_name, root_path)

    config_manager.save_config(config)

    # Initialize session
    session = config_manager.load_session()
    session.journey_state = "configured"
    session.journey_progress = {
        "repository_root": str(root_path),
        "selected_directories": [str(d) for d in (selected_dirs or [])],
        "timestamp": datetime.now().isoformat()
    }
    # Set session timing if this is a new session
    if not session.session_started:
        session.session_started = datetime.now().isoformat()
    session.last_updated = datetime.now().isoformat()
    config_manager.save_session(session)


def apply_rules_workflow() -> bool:
    """Apply rules in the correct order with user interaction.
    
    Returns:
        True if workflow completed, False if cancelled by user
    """
    config_manager = ConfigManager()
    config = config_manager.load_config()
    session = config_manager.load_session()

    # Initialize Vale container
    try:
        vale_container = ValeContainer()
        vale_container.ensure_image_exists()
    except Exception as e:
        console.print(f"[red]Failed to initialize Vale:[/red] {e}")
        raise typer.Exit(1)

    # Get files to process
    adoc_files = collect_adoc_files(config)
    if not adoc_files:
        console.print("[yellow]No .adoc files found to process.[/yellow]")
        return True  # Consider this as completed since there's nothing to do

    # Initialize processor
    processor = RuleProcessor(vale_container, config)
    
    # Track total rules to process
    session.total_rules = len(RULE_PROCESSING_ORDER)
    config_manager.save_session(session)

    # Determine starting point for rule processing
    start_index = 0
    if session.applied_rules:
        # Find where we left off
        applied_set = set(session.applied_rules)
        for i, (rule_name, _, _) in enumerate(RULE_PROCESSING_ORDER):
            if rule_name not in applied_set:
                start_index = i
                break
        else:
            # All rules have been applied
            console.print("[green]All rules have already been applied![/green]")
            return True
            
        if start_index > 0:
            console.print(f"\n[yellow]Resuming from rule {start_index + 1}/{len(RULE_PROCESSING_ORDER)}[/yellow]")
            console.print(f"[dim]Already completed: {', '.join(session.applied_rules)}[/dim]\n")

    # Process each rule in order with fresh Vale runs
    for rule_index, (rule_name, severity, description) in enumerate(RULE_PROCESSING_ORDER[start_index:], start=start_index):
        # Get the rule instance first to check if it's implemented
        rule = processor.rule_registry.get_rule(rule_name)
        if not rule:
            console.print(f"[yellow]Warning: Rule {rule_name} not implemented yet.[/yellow]")
            continue
        
        # Update session with current rule
        session.current_rule = rule_name
        session.last_updated = datetime.now().isoformat()
        config_manager.save_session(session)

        # Run Vale for just this specific rule
        console.print(f"\n🔍 Checking for {rule_name} issues... (Rule {rule_index + 1}/{session.total_rules})\n")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task(f"Running Vale {rule_name} analysis...", total=None)
            
            # Convert paths to relative paths for Vale
            relative_paths = []
            for path in adoc_files:
                try:
                    relative_paths.append(str(path.relative_to(Path.cwd())))
                except ValueError:
                    relative_paths.append(str(path))
            
            # Run Vale with single rule
            vale_output = processor.vale_container.run_vale_single_rule(
                rule_name, 
                relative_paths,
                project_root=Path.cwd()
            )
            progress.stop()

        # Parse the Vale output
        violations = processor.vale_parser.parse_json_output(vale_output)
        
        # Filter to just this rule's issues (in case Vale returns others)
        rule_violations = [v for v in violations if v.rule_name == rule_name]
        
        if not rule_violations:
            continue  # No issues for this rule

        # Process this rule
        if not process_single_rule(rule, rule_violations, description, processor, config_manager):
            # User chose to stop
            return False

        # Update session
        session.applied_rules.append(rule_name)
        config_manager.save_session(session)

    # Cleanup
    vale_container.cleanup()
    
    # Clear current rule since we're done
    session.current_rule = None
    session.last_updated = datetime.now().isoformat()
    config_manager.save_session(session)
    
    # All rules processed successfully
    return True


def process_single_rule(rule, issues, description, processor, config_manager) -> bool:
    """Process a single rule with user interaction.

    Returns:
        True to continue, False to stop
    """
    # Create a visual separator and prominent rule announcement
    console.print("\n" + "─" * 80)
    console.print(f"\n🔧 [bold cyan]Processing {rule.name} issues[/bold cyan] [yellow]({len(issues)} found)[/yellow]\n")
    console.print(f"[bold]{rule.name}:[/bold] {description}\n")

    # Show affected files
    files_affected = list(set(v.file_path for v in issues))
    console.print("These files have this issue:")
    for i, file_path in enumerate(files_affected[:10]):
        rel_path = file_path.relative_to(Path.cwd())
        console.print(f"  • {rel_path}")
    if len(files_affected) > 10:
        console.print(f"  ... and {len(files_affected) - 10} more")

    console.print()

    # Determine fix type and options
    if rule.fix_type == FixType.FULLY_DETERMINISTIC:
        fix_description = "Fix: Replace with valid entity references"
        choices = ["A = Auto-fix", "f = Flag", "s = Skip"]
        default = "A = Auto-fix"
    elif rule.fix_type == FixType.PARTIALLY_DETERMINISTIC:
        fix_description = "Fix: Replace missing content type attributes or insert `TBD` for reviewer."
        choices = ["A = Auto-fix", "f = Flag", "s = Skip"]
        default = "A = Auto-fix"
    else:
        fix_description = "Fix: Flag the issue for user review"
        choices = ["F = Flag", "s = Skip"]
        default = "F = Flag"

    console.print(fix_description)
    console.print()

    # Get user choice with text input
    choice_letters = [c[0] for c in choices]
    default_letter = default[0]
    
    # Create appropriate prompt text based on available choices
    if rule.fix_type == FixType.NON_DETERMINISTIC:
        prompt_text = f"Flag or skip? ({'/'.join(choice_letters)})"
    else:
        prompt_text = f"Auto-fix, flag, or skip? ({'/'.join(choice_letters)})"

    action = questionary.text(prompt_text).ask()
    
    if action is None:  # User cancelled (Ctrl+C)
        return False
    
    # Use default if user just pressed Enter
    if action.strip() == "":
        action = default_letter

    action_char = action.strip().lower()

    # Validate input
    valid_choices = [c.lower() for c in choice_letters]
    if action_char not in valid_choices:
        console.print(f"[red]Invalid choice '{action}'. Please enter one of: {'/'.join(choice_letters)}[/red]")
        return process_single_rule(rule, issues, description, processor, config_manager)

    if action_char == 's':
        console.print("[yellow]Skipped.[/yellow]")
        return continue_prompt()

    # Apply fixes or flags
    if action_char == 'a':
        apply_auto_fixes(rule, issues, processor, files_affected)
    else:  # 'f'
        apply_flags(rule, issues, processor, files_affected)

    # Show completion message
    show_completion_message(rule, len(files_affected))

    return continue_prompt()


def apply_auto_fixes(rule, issues, processor, files_affected):
    """Apply automatic fixes for a rule."""
    console.print()
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        task = progress.add_task(f"Applying {rule.name} fixes...", total=len(files_affected))

        # Process each file
        fixes_applied = 0
        for file_path in files_affected:
            file_issues = [v for v in issues if v.file_path == file_path]

            # Apply fixes to this file for the specific rule only
            result = processor.process_files([file_path], dry_run=False, rule_filter=rule.name)
            fixes_applied += len(result.fixes_applied)

            progress.update(task, advance=1)

    # Show summary
    console.print(f"\n✓ Applied {fixes_applied} {rule.name} fixes.")
    for i, file_path in enumerate(files_affected[:5]):
        rel_path = file_path.relative_to(Path.cwd())
        file_fixes = len([v for v in issues if v.file_path == file_path])
        console.print(f"  • {rel_path} ({file_fixes} {'fix' if file_fixes == 1 else 'fixes'})")
    if len(files_affected) > 5:
        console.print(f"  • ...")
        console.print(f"  [show the full list of files]")


def apply_flags(rule, issues, processor, files_affected):
    """Apply comment flags for a rule."""
    console.print()
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        task = progress.add_task("Applying flags...", total=len(files_affected))

        # Flag each issue with a comment
        flags_applied = 0
        for file_path in files_affected:
            file_issues = [v for v in issues if v.file_path == file_path]

            try:
                content = file_path.read_text(encoding='utf-8')
                lines = content.splitlines(keepends=True)

                # Sort issues by line number (reverse to avoid offset issues)
                sorted_issues = sorted(file_issues, key=lambda v: v.line, reverse=True)

                for issue in sorted_issues:
                    if 0 < issue.line <= len(lines):
                        # Insert comment before the line (not at the line position)
                        comment = rule.create_comment_flag(issue) + "\n"
                        # Insert at the line position, which pushes the original line down
                        lines.insert(issue.line - 1, comment)
                        flags_applied += 1

                # Write back
                file_path.write_text(''.join(lines), encoding='utf-8')

            except Exception as e:
                console.print(f"[red]Error flagging {file_path}:[/red] {e}")

            progress.update(task, advance=1)

    # Show summary
    console.print(f"\n✓ Applied {flags_applied} {rule.name} flags.")
    for i, file_path in enumerate(files_affected[:5]):
        rel_path = file_path.relative_to(Path.cwd())
        file_flags = len([v for v in issues if v.file_path == file_path])
        console.print(f"  • {rel_path} ({file_flags} {'flag' if file_flags == 1 else 'flags'})")
    if len(files_affected) > 5:
        console.print(f"  • ...")
        console.print(f"  [show the full list of files]")


def show_completion_message(rule, file_count):
    """Show completion message with to-do items."""
    console.print(Panel(
        "💡 [bold]To do:[/bold]\n"
        "- Review and fix all changes before continuing.\n" +
        (f"- Search for `TBD` and replace it with valid attribute values.\n"
         if rule.name == "ContentType" else "") +
        "- Optional: Commit and push your changes to a pull request.\n"
        "- Ensure these changes are available in the current working branch before proceeding.\n\n"
        "For more information, see [link=https://docs.google.com/presentation/d/1TaFY_qIL_-hYzKUXIps-CfXDI8SxrGvRXR8wuzdJ2Rk/edit?usp=sharing]Preparing Modules and Assemblies for DITA[/link]",
        border_style="blue"
    ))


def continue_prompt() -> bool:
    """Ask user if they want to continue with next rule.

    Returns:
        True to continue, False to stop
    """
    console.print()
    cont = questionary.confirm(
        "Continue with next rule?",
        default=True
    ).ask()
    return cont if cont is not None else False


def collect_adoc_files(config) -> List[Path]:
    """Collect all .adoc files from configured directories.

    Args:
        config: Aditi configuration

    Returns:
        List of .adoc file paths
    """
    adoc_files = []
    paths_to_check = config.allowed_paths or config.selected_directories or [Path.cwd()]

    for path in paths_to_check:
        if path.is_file() and path.suffix == ".adoc":
            adoc_files.append(path)
        elif path.is_dir():
            # Find all .adoc files recursively, excluding symlinks if configured
            for adoc_file in path.rglob("*.adoc"):
                if config.ignore_symlinks:
                    # Only add if it's NOT a symlink
                    if not adoc_file.is_symlink():
                        adoc_files.append(adoc_file)
                else:
                    # Add all files (including symlinks)
                    adoc_files.append(adoc_file)

    return adoc_files


def complete_journey():
    """Complete the journey and generate report."""
    config_manager = ConfigManager()
    session = config_manager.load_session()

    # Generate report
    report_path = generate_preparation_report(session)

    console.print("\n🎉 [bold green]Preparation journey complete![/bold green]\n")

    if report_path:
        console.print(f"📋 Preparation Report Generated:\n  {report_path}\n")

    console.print("Thank you for using Aditi! 🚀")

    # Clear journey state
    session.journey_state = None
    session.journey_progress = {}
    session.applied_rules = []
    config_manager.save_session(session)


def generate_preparation_report(session) -> Optional[Path]:
    """Generate a preparation report.

    Args:
        session: Session state with journey progress

    Returns:
        Path to generated report or None
    """
    try:
        # Create reports directory
        reports_dir = Path.home() / "aditi-data" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)

        # Generate report filename
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        report_path = reports_dir / f"{timestamp}-preparation-report.md"

        # Write report
        with open(report_path, 'w') as f:
            f.write("# Aditi Preparation Report\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Summary\n\n")
            f.write(f"- Repository: {session.journey_progress.get('repository_root', 'Unknown')}\n")
            f.write(f"- Rules Applied: {len(session.applied_rules)}\n")

            if session.applied_rules:
                f.write("\n## Rules Applied\n\n")
                for rule in session.applied_rules:
                    f.write(f"- {rule}\n")

            f.write("\n## Next Steps\n\n")
            f.write("1. Review all changes made by Aditi\n")
            f.write("2. Search for `TBD` placeholders and replace with appropriate values\n")
            f.write("3. Fix any issues that were flagged with comments\n")
            f.write("4. Run `aditi check` to verify no issues remain\n")
            f.write("5. Create a pull request with your changes\n")

        return report_path

    except Exception as e:
        console.print(f"[yellow]Warning: Could not generate report:[/yellow] {e}")
        return None