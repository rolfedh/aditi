#!/usr/bin/env python3
"""Tests for the improved CLAUDE.md updater."""

import pytest
from pathlib import Path
import tempfile
import shutil
from unittest.mock import patch, MagicMock
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from claude_md_updater_v2 import ImprovedClaudeMdUpdater, CommitInfo


class TestCommitInfo:
    """Test the CommitInfo parser."""
    
    def test_conventional_commit_parsing(self):
        """Test parsing of conventional commits."""
        commit = CommitInfo("abc123", "feat(auth): add login functionality")
        assert commit.type == "feat"
        assert commit.scope == "auth"
        assert commit.description == "add login functionality"
        assert not commit.breaking
    
    def test_breaking_change_detection(self):
        """Test detection of breaking changes."""
        commit = CommitInfo("abc123", "feat!: remove deprecated API")
        assert commit.breaking
        
        commit2 = CommitInfo("abc123", "fix!: change return type")
        assert commit2.breaking
    
    def test_non_conventional_commit(self):
        """Test parsing of non-conventional commits."""
        commit = CommitInfo("abc123", "Updated README file")
        assert commit.type == "other"
        assert commit.scope is None
        assert commit.description == "Updated README file"
    
    def test_commit_without_scope(self):
        """Test conventional commit without scope."""
        commit = CommitInfo("abc123", "fix: resolve memory leak")
        assert commit.type == "fix"
        assert commit.scope is None
        assert commit.description == "resolve memory leak"
    
    def test_empty_commit_message(self):
        """Test handling of empty commit message."""
        commit = CommitInfo("abc123", "")
        assert commit.type == "other"
        assert commit.scope is None
        assert commit.description == ""


class TestImprovedClaudeMdUpdater:
    """Test the improved updater."""
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            
            # Create CLAUDE.md with markers
            claude_md = project_dir / "CLAUDE.md"
            claude_md.write_text("""# CLAUDE.md

## Dependencies
<!-- AUTO-GENERATED:DEPENDENCIES -->
Old dependencies
<!-- /AUTO-GENERATED:DEPENDENCIES -->

## Recent Development
<!-- AUTO-GENERATED:RECENT -->
Old recent content
<!-- /AUTO-GENERATED:RECENT -->

## Architecture
<!-- AUTO-GENERATED:ARCHITECTURE -->
Old architecture
<!-- /AUTO-GENERATED:ARCHITECTURE -->

## Commands
<!-- AUTO-GENERATED:COMMANDS -->
Old commands
<!-- /AUTO-GENERATED:COMMANDS -->
""")
            
            # Create pyproject.toml
            pyproject = project_dir / "pyproject.toml"
            pyproject.write_text("""
[project]
dependencies = [
    "typer>=0.9.0",
    "pydantic>=2.0",
    "pytest>=7.0"
]

[project.optional-dependencies]
dev = [
    "black>=23.0",
    "ruff>=0.1.0",
    "mypy>=1.0"
]
""")
            
            yield project_dir
    
    def test_update_section(self, temp_project):
        """Test updating a single section."""
        updater = ImprovedClaudeMdUpdater(temp_project)
        
        content = "<!-- AUTO-GENERATED:TEST -->\nOld content\n<!-- /AUTO-GENERATED:TEST -->"
        updated = updater._update_section(content, "TEST", "New content")
        
        assert "New content" in updated
        assert "Old content" not in updated
    
    def test_parse_commits_safely(self, temp_project):
        """Test safe commit parsing."""
        updater = ImprovedClaudeMdUpdater(temp_project)
        
        # Mock git log output
        mock_output = """abc123 feat: add new feature
def456 fix(api): resolve issue
789ghi Updated documentation
        """
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=mock_output
            )
            
            commits = updater._parse_commits_safely()
            
            assert len(commits) == 3
            assert commits[0].type == "feat"
            assert commits[1].type == "fix"
            assert commits[1].scope == "api"
            assert commits[2].type == "other"
    
    def test_parse_commits_with_malformed_lines(self, temp_project):
        """Test parsing with malformed commit lines."""
        updater = ImprovedClaudeMdUpdater(temp_project)
        
        # Mock git log output with problematic lines
        mock_output = """abc123 feat: good commit
def456
789ghi
jkl012 fix: another good commit"""
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=mock_output
            )
            
            commits = updater._parse_commits_safely()
            
            # Should handle malformed lines gracefully
            assert len(commits) == 4
            assert commits[0].message == "feat: good commit"
            assert commits[3].message == "fix: another good commit"
    
    def test_validate_content(self, temp_project):
        """Test content validation."""
        updater = ImprovedClaudeMdUpdater(temp_project)
        
        # Test truncated word detection
        bad_content = "✅ Implemented ation"
        errors = updater._validate_content(bad_content)
        assert any("truncated" in error for error in errors)
        
        # Test unmatched code blocks
        bad_markdown = "```python\ncode here"
        errors = updater._validate_content(bad_markdown)
        assert any("code block" in error for error in errors)
        
        # Test valid content
        good_content = "✅ Implemented authentication\n```python\ncode\n```"
        errors = updater._validate_content(good_content)
        assert len(errors) == 0
    
    def test_analyze_recent_development(self, temp_project):
        """Test recent development analysis."""
        updater = ImprovedClaudeMdUpdater(temp_project)
        
        # Mock commits
        mock_commits = [
            CommitInfo("abc", "feat: add new feature"),
            CommitInfo("def", "fix(api): resolve bug"),
            CommitInfo("ghi", "test: add unit tests"),
            CommitInfo("jkl", "feat!: breaking change"),
        ]
        
        with patch.object(updater, '_parse_commits_safely', return_value=mock_commits):
            with patch.object(updater, '_get_top_changed_files', return_value=[]):
                analysis = updater._analyze_recent_development()
                
                # Should have 2 achievements (feat commits only, breaking change is also a feat)
                assert len(analysis['achievements']) == 2
                # Check they're both there
                assert any('add new feature' in a.lower() for a in analysis['achievements'])
                assert any('breaking change' in a.lower() for a in analysis['achievements'])
                assert analysis['statistics']['total_commits'] == 4
                assert analysis['statistics']['breaking_changes'] == 1
                assert 'api' in analysis['focus_areas']
                assert 'testing' in analysis['focus_areas']
    
    def test_format_recent_analysis_deterministic(self, temp_project):
        """Test that formatting is deterministic."""
        updater = ImprovedClaudeMdUpdater(temp_project)
        
        analysis = {
            'achievements': ['✅ Feature A', '✅ Feature B'],
            'focus_areas': {'testing': 3, 'features': 2, 'docs': 1},
            'statistics': {'total_commits': 10, 'breaking_changes': 0},
            'top_changed_files': []
        }
        
        # Format multiple times - should be identical
        result1 = updater._format_recent_analysis(analysis)
        result2 = updater._format_recent_analysis(analysis)
        
        assert result1 == result2
        assert '✅ Feature A' in result1
        assert 'Testing**: 3 commits' in result1  # Format includes bold
    
    def test_dry_run_mode(self, temp_project):
        """Test dry run mode doesn't modify files."""
        updater = ImprovedClaudeMdUpdater(temp_project)
        
        original_content = updater.claude_md.read_text()
        
        with patch.object(updater, '_format_recent_analysis', return_value="New content"):
            updater.update_all_sections(dry_run=True)
        
        # File should not be modified
        assert updater.claude_md.read_text() == original_content
    
    def test_error_handling(self, temp_project):
        """Test error handling in updater."""
        updater = ImprovedClaudeMdUpdater(temp_project)
        
        # Test with missing CLAUDE.md
        updater.claude_md = temp_project / "nonexistent.md"
        result = updater.update_all_sections()
        assert not result
        
        # Test with git command failure
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            commits = updater._parse_commits_safely()
            assert commits == []
    
    def test_categorize_dependencies(self, temp_project):
        """Test dependency categorization."""
        updater = ImprovedClaudeMdUpdater(temp_project)
        
        deps = ['typer>=0.9', 'pytest>=7.0', 'black>=23.0', 'pydantic>=2.0', 'requests']
        categorized = updater._categorize_deps(deps)
        
        assert 'typer>=0.9' in categorized['CLI Framework']
        assert 'pytest>=7.0' in categorized['Testing']
        assert 'black>=23.0' in categorized['Code Quality']
        assert 'pydantic>=2.0' in categorized['Data Validation']
        assert 'requests' in categorized['Other']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])