"""Unit tests for git guidance module."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from aditi.git import (
    GitCommand,
    generate_branch_name,
    get_current_branch,
    get_default_branch,
    guide_branch_creation,
    guide_commit_creation,
    guide_pr_creation,
    has_uncommitted_changes,
    is_git_repository,
    suggest_commit_message,
)


class TestGitCommand:
    """Test GitCommand class."""
    
    def test_git_command_creation(self):
        """Test creating git command."""
        cmd = GitCommand("git status", "Show repository status")
        assert cmd.command == "git status"
        assert cmd.description == "Show repository status"
    
    @patch("aditi.git.console")
    def test_display(self, mock_console):
        """Test command display."""
        cmd = GitCommand("git add .", "Stage all changes")
        cmd.display()
        mock_console.print.assert_called()


class TestGitHelpers:
    """Test git helper functions."""
    
    def test_is_git_repository(self, temp_git_repo: Path):
        """Test git repository detection."""
        assert is_git_repository(temp_git_repo)
        
        # Test with a non-git directory
        non_git_dir = temp_git_repo.parent / "non_git"
        non_git_dir.mkdir()
        assert not is_git_repository(non_git_dir)
    
    def test_get_current_branch(self, temp_git_repo: Path):
        """Test getting current branch."""
        # In git repo
        branch = get_current_branch(temp_git_repo)
        assert branch in ["main", "master"]
        
        # Not in git repo
        non_git_dir = temp_git_repo.parent / "non_git2"
        non_git_dir.mkdir()
        assert get_current_branch(non_git_dir) is None
    
    def test_get_default_branch(self, temp_git_repo: Path):
        """Test getting default branch."""
        branch = get_default_branch(temp_git_repo)
        assert branch in ["main", "master"]
    
    def test_has_uncommitted_changes(self, temp_git_repo: Path):
        """Test checking for uncommitted changes."""
        # No changes initially
        assert not has_uncommitted_changes(temp_git_repo)
        
        # Create a change
        (temp_git_repo / "test.txt").write_text("test")
        assert has_uncommitted_changes(temp_git_repo)
    
    def test_generate_branch_name(self):
        """Test branch name generation."""
        # With all options
        name = generate_branch_name("fix", "entity references", include_date=False)
        assert name == "fix/entity-references"
        
        # With date
        name = generate_branch_name("aditi", "update docs")
        assert name.startswith("aditi/")
        assert "update-docs" in name
        
        # Clean special characters
        name = generate_branch_name("feature", "ADD: new-feature!", include_date=False)
        assert name == "feature/add-new-feature"
        
        # Empty description
        name = generate_branch_name("test", "", include_date=False)
        assert name == "test"
    
    def test_suggest_commit_message(self):
        """Test commit message generation."""
        # Single rule fix
        msg = suggest_commit_message(
            ["file1.adoc"],
            ["EntityReference"],
            manual_fixes=False
        )
        assert "Fix EntityReference issues" in msg
        assert "file1.adoc" in msg
        
        # Multiple rules
        msg = suggest_commit_message(
            ["file1.adoc", "file2.adoc"],
            ["EntityReference", "ContentType"],
            manual_fixes=True
        )
        assert "Fix multiple AsciiDocDITA issues (2 rules)" in msg
        assert "EntityReference" in msg
        assert "ContentType" in msg
        assert "manual intervention" in msg
        
        # Many files
        files = [f"file{i}.adoc" for i in range(10)]
        msg = suggest_commit_message(files, ["TestRule"], manual_fixes=False)
        assert "Updated 10 files" in msg


class TestGitWorkflows:
    """Test git workflow guidance functions."""
    
    @patch("aditi.git.has_uncommitted_changes")
    @patch("aditi.git.get_current_branch")
    def test_guide_branch_creation(self, mock_current, mock_changes):
        """Test branch creation guidance."""
        mock_current.return_value = "main"
        mock_changes.return_value = False
        
        # Simple branch creation
        commands = guide_branch_creation(
            Path("/repo"),
            "feature/test"
        )
        assert len(commands) == 1
        assert "checkout -b feature/test" in commands[0].command
        
        # With uncommitted changes
        mock_changes.return_value = True
        commands = guide_branch_creation(
            Path("/repo"),
            "feature/test"
        )
        assert len(commands) == 2
        assert "git stash" in commands[0].command
        
        # From different branch
        mock_changes.return_value = False
        commands = guide_branch_creation(
            Path("/repo"),
            "feature/test",
            from_branch="develop"
        )
        assert any("checkout develop" in cmd.command for cmd in commands)
        assert any("pull origin develop" in cmd.command for cmd in commands)
    
    def test_guide_commit_creation(self):
        """Test commit creation guidance."""
        # Few files
        commands = guide_commit_creation(
            Path("/repo"),
            ["file1.adoc", "file2.adoc"],
            "Fix: Update documentation"
        )
        assert len(commands) == 3  # 2 adds + 1 commit
        assert any("add file1.adoc" in cmd.command for cmd in commands)
        assert any("add file2.adoc" in cmd.command for cmd in commands)
        
        # Many files
        files = [f"file{i}.adoc" for i in range(10)]
        commands = guide_commit_creation(
            Path("/repo"),
            files,
            "Fix: Batch update"
        )
        assert len(commands) == 2  # 1 add + 1 commit
        
        # Escape quotes in message
        commands = guide_commit_creation(
            Path("/repo"),
            ["file.adoc"],
            'Fix "quoted" message'
        )
        assert 'Fix \\"quoted\\" message' in commands[-1].command
    
    @patch("aditi.git.console")
    def test_guide_pr_creation(self, mock_console):
        """Test PR creation guidance."""
        commands = guide_pr_creation(
            Path("/repo"),
            "feature/test",
            "main",
            "Add new feature",
            "This PR adds a new feature"
        )
        
        # Should have push command
        assert len(commands) == 1
        assert "push -u origin feature/test" in commands[0].command
        
        # Should print PR info
        assert mock_console.print.called