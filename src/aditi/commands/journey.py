"""Journey command implementation for guided DITA preparation workflow."""

import sys
from datetime import datetime
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


def journey_command() -> None:
    """Start an interactive journey to prepare AsciiDoc files for DITA migration."""
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

    # Phase 1: Repository Configuration
    if not configure_repository():
        return

    # Phase 2: Rule Application Workflow
    apply_rules_workflow()

    # Phase 3: Completion
    complete_journey()


def configure_repository() -> bool:
    """Configure repository and directory selection.

    Returns:
        True if configuration was successful, False otherwise
    """
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

    # Ask about customizing subdirectory access
    customize = questionary.confirm(
        "Customize subdirectory access?",
        default=False
    ).ask()

    if customize:
        selected_dirs = select_directories(current_dir)
        if not selected_dirs:
            console.print("[red]No directories selected. Exiting.[/red]")
            return False
    else:
        # Use all directories with .adoc files
        selected_dirs = None

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
    config_manager.save_session(session)


def apply_rules_workflow() -> None:
    """Apply rules in the correct order with user interaction."""
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
        return

    # Initialize processor
    processor = RuleProcessor(vale_container, config)

    # First, run a full check to get all violations
    console.print("\n🔍 Analyzing AsciiDoc files...\n")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Running Vale analysis...", total=None)
        result = processor.process_files(adoc_files, dry_run=True)
        progress.stop()

    # Group violations by rule
    violations_by_rule = processor.vale_parser.group_by_rule(result.violations_found)

    # Process each rule in order
    for rule_name, severity, description in RULE_PROCESSING_ORDER:
        if rule_name not in violations_by_rule:
            continue  # No violations for this rule

        violations = violations_by_rule[rule_name]

        # Get the rule instance
        rule = processor.rule_registry.get_rule(rule_name)
        if not rule:
            console.print(f"[yellow]Warning: Rule {rule_name} not implemented yet.[/yellow]")
            continue

        # Process this rule
        if not process_single_rule(rule, violations, description, processor, config_manager):
            # User chose to stop
            console.print("\n[yellow]Journey paused. You can resume later.[/yellow]")
            return

        # Update session
        session.applied_rules.append(rule_name)
        config_manager.save_session(session)

    # Cleanup
    vale_container.cleanup()


def process_single_rule(rule, violations, description, processor, config_manager) -> bool:
    """Process a single rule with user interaction.

    Returns:
        True to continue, False to stop
    """
    # Create a visual separator and prominent rule announcement
    console.print("\n" + "─" * 80)
    console.print(f"\n🔧 [bold cyan]Processing {rule.name} issues[/bold cyan] [yellow]({len(violations)} found)[/yellow]\n")
    console.print(f"[bold]{rule.name}:[/bold] {description}\n")

    # Show affected files
    files_affected = list(set(v.file_path for v in violations))
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
    
    # Use default if user just pressed Enter
    if not action or action.strip() == "":
        action = default_letter

    if not action:  # User cancelled
        return False

    action_char = action.strip().lower()

    # Validate input
    valid_choices = [c.lower() for c in choice_letters]
    if action_char not in valid_choices:
        console.print(f"[red]Invalid choice '{action}'. Please enter one of: {'/'.join(choice_letters)}[/red]")
        return process_single_rule(rule, violations, description, processor, config_manager)

    if action_char == 's':
        console.print("[yellow]Skipped.[/yellow]")
        return continue_prompt()

    # Apply fixes or flags
    if action_char == 'a':
        apply_auto_fixes(rule, violations, processor, files_affected)
    else:  # 'f'
        apply_flags(rule, violations, processor, files_affected)

    # Show completion message
    show_completion_message(rule, len(files_affected))

    return continue_prompt()


def apply_auto_fixes(rule, violations, processor, files_affected):
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
            file_violations = [v for v in violations if v.file_path == file_path]

            # Apply fixes to this file
            result = processor.process_files([file_path], dry_run=False)
            fixes_applied += len(result.fixes_applied)

            progress.update(task, advance=1)

    # Show summary
    console.print(f"\n✓ Applied {fixes_applied} {rule.name} fixes.")
    for i, file_path in enumerate(files_affected[:5]):
        rel_path = file_path.relative_to(Path.cwd())
        file_fixes = len([v for v in violations if v.file_path == file_path])
        console.print(f"  • {rel_path} ({file_fixes} {'fix' if file_fixes == 1 else 'fixes'})")
    if len(files_affected) > 5:
        console.print(f"  • ...")
        console.print(f"  [show the full list of files]")


def apply_flags(rule, violations, processor, files_affected):
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

        # Flag each violation with a comment
        flags_applied = 0
        for file_path in files_affected:
            file_violations = [v for v in violations if v.file_path == file_path]

            try:
                content = file_path.read_text(encoding='utf-8')
                lines = content.splitlines(keepends=True)

                # Sort violations by line number (reverse to avoid offset issues)
                sorted_violations = sorted(file_violations, key=lambda v: v.line, reverse=True)

                for violation in sorted_violations:
                    if 0 < violation.line <= len(lines):
                        # Insert comment before the line
                        comment = f"// ADITI-{rule.name}: {violation.message}\n"
                        lines.insert(violation.line - 1, comment)
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
        file_flags = len([v for v in violations if v.file_path == file_path])
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