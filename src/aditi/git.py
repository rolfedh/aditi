"""Git guidance and helper functions for Aditi."""

import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()


class GitCommand:
    """Container for a git command with description."""
    
    def __init__(self, command: str, description: str):
        """Initialize git command.
        
        Args:
            command: The git command to run
            description: Human-readable description of what the command does
        """
        self.command = command
        self.description = description

    def display(self) -> None:
        """Display the command with syntax highlighting."""
        syntax = Syntax(self.command, "bash", theme="monokai", line_numbers=False)
        panel = Panel(
            syntax,
            title=f"[bold blue]Git Command: {self.description}[/bold blue]",
            border_style="blue",
        )
        console.print(panel)


def is_git_repository(path: Path) -> bool:
    """Check if the given path is inside a git repository.
    
    Args:
        path: Path to check
        
    Returns:
        True if path is inside a git repository
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=path,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0
    except Exception:
        return False


def get_current_branch(path: Path) -> Optional[str]:
    """Get the current git branch name.
    
    Args:
        path: Repository path
        
    Returns:
        Current branch name or None if not in a git repository
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=path,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except Exception:
        return None


def get_default_branch(path: Path) -> str:
    """Get the default branch name (main/master).
    
    Args:
        path: Repository path
        
    Returns:
        Default branch name (defaults to 'main' if detection fails)
    """
    try:
        # Try to get the default branch from origin
        result = subprocess.run(
            ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
            cwd=path,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            # Extract branch name from refs/remotes/origin/main
            branch = result.stdout.strip().split("/")[-1]
            return branch
    except Exception:
        pass

    # Check if main or master exists
    for branch in ["main", "master"]:
        result = subprocess.run(
            ["git", "show-ref", f"refs/heads/{branch}"],
            cwd=path,
            capture_output=True,
            check=False,
        )
        if result.returncode == 0:
            return branch

    return "main"  # Default fallback


def has_uncommitted_changes(path: Path) -> bool:
    """Check if there are uncommitted changes in the repository.
    
    Args:
        path: Repository path
        
    Returns:
        True if there are uncommitted changes
    """
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=path,
            capture_output=True,
            text=True,
            check=True,
        )
        return bool(result.stdout.strip())
    except Exception:
        return False


def generate_branch_name(
    prefix: str = "aditi",
    description: str = "",
    include_date: bool = True,
) -> str:
    """Generate a branch name following best practices.
    
    Args:
        prefix: Branch prefix (e.g., 'aditi', 'fix', 'feature')
        description: Brief description of the changes
        include_date: Whether to include date in branch name
        
    Returns:
        Generated branch name
    """
    parts = [prefix]
    
    if include_date:
        date_str = datetime.now().strftime("%Y%m%d")
        parts.append(date_str)
    
    if description:
        # Clean description: lowercase, replace spaces with hyphens, remove special chars
        clean_desc = re.sub(r"[^a-z0-9\s-]", "", description.lower())
        clean_desc = re.sub(r"\s+", "-", clean_desc.strip())
        clean_desc = re.sub(r"-+", "-", clean_desc)  # Remove multiple hyphens
        if clean_desc:
            parts.append(clean_desc)
    
    return "/".join(parts)


def suggest_commit_message(
    files_changed: List[str],
    rule_fixes: List[str],
    manual_fixes: bool = False,
) -> str:
    """Generate a suggested commit message based on changes.
    
    Args:
        files_changed: List of changed file paths
        rule_fixes: List of rule names that were fixed
        manual_fixes: Whether manual fixes were required
        
    Returns:
        Suggested commit message
    """
    # Determine the type of change
    if len(rule_fixes) == 1:
        subject = f"Fix {rule_fixes[0]} issues in AsciiDoc files"
    elif len(rule_fixes) > 1:
        subject = f"Fix multiple AsciiDocDITA issues ({len(rule_fixes)} rules)"
    else:
        subject = "Update AsciiDoc files for DITA compatibility"
    
    # Build the body
    body_parts = []
    
    if rule_fixes:
        body_parts.append("Fixed the following AsciiDocDITA rules:")
        for rule in sorted(rule_fixes):
            body_parts.append(f"  - {rule}")
        body_parts.append("")
    
    if len(files_changed) <= 5:
        body_parts.append("Files updated:")
        for file in sorted(files_changed):
            body_parts.append(f"  - {file}")
    else:
        body_parts.append(f"Updated {len(files_changed)} files")
    
    if manual_fixes:
        body_parts.append("")
        body_parts.append("Note: Some fixes required manual intervention")
    
    return f"{subject}\n\n" + "\n".join(body_parts)


def guide_branch_creation(
    repo_path: Path,
    branch_name: str,
    from_branch: Optional[str] = None,
) -> List[GitCommand]:
    """Generate git commands for creating a new branch.
    
    Args:
        repo_path: Repository path
        branch_name: Name for the new branch
        from_branch: Base branch (defaults to current branch)
        
    Returns:
        List of git commands to execute
    """
    commands = []
    
    # Check for uncommitted changes
    if has_uncommitted_changes(repo_path):
        commands.append(
            GitCommand(
                "git stash",
                "Stash uncommitted changes before switching branches"
            )
        )
    
    # Switch to base branch if specified
    if from_branch:
        current = get_current_branch(repo_path)
        if current != from_branch:
            commands.append(
                GitCommand(
                    f"git checkout {from_branch}",
                    f"Switch to base branch '{from_branch}'"
                )
            )
            commands.append(
                GitCommand(
                    "git pull origin " + from_branch,
                    "Update base branch with latest changes"
                )
            )
    
    # Create and switch to new branch
    commands.append(
        GitCommand(
            f"git checkout -b {branch_name}",
            f"Create and switch to new branch '{branch_name}'"
        )
    )
    
    return commands


def guide_commit_creation(
    repo_path: Path,
    files: List[str],
    commit_message: str,
) -> List[GitCommand]:
    """Generate git commands for creating a commit.
    
    Args:
        repo_path: Repository path
        files: List of files to commit
        commit_message: Commit message
        
    Returns:
        List of git commands to execute
    """
    commands = []
    
    # Add files
    if files:
        if len(files) <= 5:
            # Add files individually for clarity
            for file in files:
                commands.append(
                    GitCommand(
                        f"git add {file}",
                        f"Stage changes in {file}"
                    )
                )
        else:
            # Add all files at once
            file_pattern = " ".join(files)
            commands.append(
                GitCommand(
                    f"git add {file_pattern}",
                    f"Stage changes in {len(files)} files"
                )
            )
    
    # Create commit
    # Escape quotes in commit message
    escaped_message = commit_message.replace('"', '\\"')
    commands.append(
        GitCommand(
            f'git commit -m "{escaped_message}"',
            "Create commit with changes"
        )
    )
    
    return commands


def guide_pr_creation(
    repo_path: Path,
    branch_name: str,
    base_branch: str,
    title: str,
    description: str = "",
) -> List[GitCommand]:
    """Generate git commands for creating a pull request.
    
    Args:
        repo_path: Repository path
        branch_name: Feature branch name
        base_branch: Base branch for PR
        title: PR title
        description: PR description
        
    Returns:
        List of git commands to execute
    """
    commands = []
    
    # Push branch
    commands.append(
        GitCommand(
            f"git push -u origin {branch_name}",
            f"Push branch '{branch_name}' to remote"
        )
    )
    
    # Note about creating PR
    console.print("\n[yellow]Note:[/yellow] After pushing, create a pull request:")
    console.print(f"  • From branch: [bold]{branch_name}[/bold]")
    console.print(f"  • To branch: [bold]{base_branch}[/bold]")
    console.print(f"  • Title: [bold]{title}[/bold]")
    if description:
        console.print(f"  • Description:\n{description}")
    
    # Platform-specific PR creation commands
    console.print("\n[dim]Platform-specific commands:[/dim]")
    
    # GitHub CLI
    gh_desc = description.replace('"', '\\"') if description else ""
    gh_cmd = f'gh pr create --base {base_branch} --title "{title}"'
    if gh_desc:
        gh_cmd += f' --body "{gh_desc}"'
    console.print(f"  • GitHub CLI: [cyan]{gh_cmd}[/cyan]")
    
    # GitLab CLI
    gl_cmd = f'glab mr create --target-branch {base_branch} --title "{title}"'
    if gh_desc:
        gl_cmd += f' --description "{gh_desc}"'
    console.print(f"  • GitLab CLI: [cyan]{gl_cmd}[/cyan]")
    
    return commands


def display_git_workflow(commands: List[GitCommand]) -> None:
    """Display a complete git workflow to the user.
    
    Args:
        commands: List of git commands to display
    """
    console.print("\n[bold green]Git Workflow Commands:[/bold green]")
    console.print("[dim]Run these commands in order:[/dim]\n")
    
    for i, cmd in enumerate(commands, 1):
        console.print(f"[bold]{i}.[/bold] {cmd.description}")
        cmd.display()
        console.print()  # Add spacing between commands


def prompt_to_continue() -> bool:
    """Prompt user to continue with git operations.
    
    Returns:
        True if user wants to continue
    """
    response = console.input("\n[yellow]Continue with these git operations? (y/n): [/yellow]")
    return response.lower() in ["y", "yes"]