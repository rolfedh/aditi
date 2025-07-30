#!/usr/bin/env python3
"""
Improved CLAUDE.md updater that updates sections in-place with robust parsing.

This version implements the recommendations:
- No template file needed - updates CLAUDE.md directly
- Robust commit parsing with error handling
- Structured commit analysis
- Deterministic output
- Validation of generated content
"""

import os
import re
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set
from collections import OrderedDict, defaultdict
import sys

try:
    import toml
except ImportError:
    print("Installing toml dependency...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "toml"])
    import toml


class CommitInfo:
    """Structured representation of a git commit."""
    
    def __init__(self, hash: str, message: str):
        self.hash = hash
        self.message = message
        self.type = self._extract_type()
        self.scope = self._extract_scope()
        self.description = self._extract_description()
        self.breaking = self._is_breaking_change()
        
    def _extract_type(self) -> str:
        """Extract conventional commit type (feat, fix, docs, etc)."""
        # Handle breaking changes (feat!, fix!, etc)
        match = re.match(r'^(\w+)(?:!)?(?:\([^)]+\))?:', self.message)
        return match.group(1) if match else 'other'
    
    def _extract_scope(self) -> Optional[str]:
        """Extract scope from conventional commit."""
        match = re.match(r'^\w+\(([^)]+)\):', self.message)
        return match.group(1) if match else None
    
    def _extract_description(self) -> str:
        """Extract the description part of the commit message."""
        # Remove type(scope): prefix if present
        match = re.match(r'^(?:\w+)(?:\([^)]+\))?:\s*(.+)', self.message)
        if match:
            return match.group(1)
        return self.message
    
    def _is_breaking_change(self) -> bool:
        """Check if this is a breaking change."""
        return '!' in self.message.split(':')[0] if ':' in self.message else False


class ImprovedClaudeMdUpdater:
    """Improved CLAUDE.md updater with in-place updates and robust parsing."""
    
    def __init__(self, project_root: str = "."):
        self.root = Path(project_root).resolve()
        self.claude_md = self.root / "CLAUDE.md"
        self.pyproject_file = self.root / "pyproject.toml"
        
    def update_all_sections(self, dry_run: bool = False) -> bool:
        """Update all auto-generated sections in CLAUDE.md."""
        if not self.claude_md.exists():
            print(f"❌ CLAUDE.md not found: {self.claude_md}")
            return False
            
        print("🔄 Updating CLAUDE.md sections in-place...")
        
        # Read current content
        content = self.claude_md.read_text(encoding='utf-8')
        original_content = content
        
        # Update each section
        try:
            content = self._update_dependencies_section(content)
            content = self._update_completed_section(content)
            content = self._update_architecture_section(content)
            content = self._update_recent_section(content)
            content = self._update_commands_section(content)
            
            # Validate the updated content
            validation_errors = self._validate_content(content)
            if validation_errors:
                print("❌ Validation errors found:")
                for error in validation_errors:
                    print(f"   - {error}")
                return False
            
            # Write back if changed and not dry run
            if content != original_content:
                # Check if changes are significant
                changes_significant = self._are_changes_significant(original_content, content)
                
                if dry_run:
                    if changes_significant:
                        print("🔍 Dry run - significant changes would be made but not saved")
                        self._show_diff(original_content, content)
                    else:
                        print("ℹ️  No significant changes detected, skipping CLAUDE.md update")
                elif changes_significant:
                    self.claude_md.write_text(content, encoding='utf-8')
                    print("✅ CLAUDE.md updated successfully")
                else:
                    print("ℹ️  No significant changes detected, skipping CLAUDE.md update")
                return True
            else:
                print("✨ CLAUDE.md is already up to date")
                return True
                
        except Exception as e:
            print(f"❌ Error updating CLAUDE.md: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _update_section(self, content: str, marker: str, new_content: str) -> str:
        """Update a single auto-generated section."""
        start_marker = f"<!-- AUTO-GENERATED:{marker} -->"
        end_marker = f"<!-- /AUTO-GENERATED:{marker} -->"
        
        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker)
        
        if start_idx == -1 or end_idx == -1:
            print(f"⚠️  Section markers not found for {marker}")
            return content
        
        # Replace content between markers
        before = content[:start_idx + len(start_marker)]
        after = content[end_idx:]
        
        return before + "\n" + new_content + "\n" + after
    
    def _update_dependencies_section(self, content: str) -> str:
        """Update dependencies from pyproject.toml."""
        deps = self._extract_dependencies()
        deps_content = self._format_dependencies(deps)
        return self._update_section(content, "DEPENDENCIES", deps_content)
    
    def _update_completed_section(self, content: str) -> str:
        """Update completed features - preserve existing content."""
        # For completed section, we preserve what's there since it's manually curated
        # This prevents losing phase completions
        return content
    
    def _update_architecture_section(self, content: str) -> str:
        """Update current architecture tree."""
        tree = self._generate_architecture_tree()
        return self._update_section(content, "ARCHITECTURE", tree)
    
    def _update_recent_section(self, content: str) -> str:
        """Update recent development with improved analysis."""
        analysis = self._analyze_recent_development()
        recent_content = self._format_recent_analysis(analysis)
        return self._update_section(content, "RECENT", recent_content)
    
    def _update_commands_section(self, content: str) -> str:
        """Update common commands section."""
        commands = self._extract_commands()
        commands_content = self._format_commands(commands)
        return self._update_section(content, "COMMANDS", commands_content)
    
    def _parse_commits_safely(self, since_days: int = 30) -> List[CommitInfo]:
        """Safely parse git commits with structured analysis."""
        try:
            since_date = (datetime.now() - timedelta(days=since_days)).strftime('%Y-%m-%d')
            cmd = ['git', 'log', f'--since={since_date}', '--oneline', '--no-merges']
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.root)
            
            if result.returncode != 0:
                return []
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                    
                try:
                    parts = line.split(' ', 1)
                    if len(parts) == 2:
                        commits.append(CommitInfo(parts[0], parts[1]))
                    else:
                        # Handle edge case of commit with no message
                        commits.append(CommitInfo(parts[0], ""))
                except Exception as e:
                    print(f"⚠️  Skipping malformed commit line: {line}")
                    continue
                    
            return commits
            
        except Exception as e:
            print(f"⚠️  Error parsing commits: {e}")
            return []
    
    def _analyze_recent_development(self) -> Dict[str, any]:
        """Analyze recent commits with improved intelligence."""
        commits = self._parse_commits_safely()
        
        if not commits:
            return {
                'achievements': [],
                'focus_areas': OrderedDict(),
                'statistics': {},
                'top_changed_files': []
            }
        
        # Categorize commits by type
        type_counts = defaultdict(int)
        achievements = []
        focus_areas = defaultdict(int)
        
        for commit in commits:
            type_counts[commit.type] += 1
            
            # Extract achievements from feat commits
            if commit.type == 'feat':
                # Clean up the description
                desc = commit.description.strip()
                if desc and not desc.endswith('.'):
                    desc += '.'
                achievement = f"✅ {desc.capitalize()}"
                if achievement not in achievements:  # Avoid duplicates
                    achievements.append(achievement)
            
            # Categorize focus areas
            if commit.scope:
                focus_areas[commit.scope] += 1
            else:
                # Infer from keywords if no scope
                desc_lower = commit.description.lower()
                if any(word in desc_lower for word in ['test', 'spec', 'coverage']):
                    focus_areas['testing'] += 1
                elif any(word in desc_lower for word in ['doc', 'readme', 'guide']):
                    focus_areas['documentation'] += 1
                elif any(word in desc_lower for word in ['ci', 'github action', 'workflow']):
                    focus_areas['ci/cd'] += 1
                elif commit.type == 'fix':
                    focus_areas['bug-fixes'] += 1
                elif commit.type == 'feat':
                    focus_areas['features'] += 1
        
        # Get top changed files
        top_files = self._get_top_changed_files(len(commits))
        
        # Sort focus areas by frequency
        sorted_focus = OrderedDict(
            sorted(focus_areas.items(), key=lambda x: x[1], reverse=True)
        )
        
        return {
            'achievements': achievements[:5],  # Top 5, no duplicates
            'focus_areas': sorted_focus,
            'statistics': {
                'total_commits': len(commits),
                'types': dict(type_counts),
                'breaking_changes': sum(1 for c in commits if c.breaking)
            },
            'top_changed_files': top_files[:5]
        }
    
    def _get_top_changed_files(self, days: int) -> List[Tuple[str, int]]:
        """Get the most frequently changed files."""
        try:
            since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            cmd = ['git', 'log', f'--since={since_date}', '--format=', '--name-only', '--no-merges']
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.root)
            
            if result.returncode != 0:
                return []
            
            file_counts = defaultdict(int)
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    file_counts[line.strip()] += 1
            
            # Sort by frequency
            return sorted(file_counts.items(), key=lambda x: x[1], reverse=True)
            
        except Exception:
            return []
    
    def _format_recent_analysis(self, analysis: Dict[str, any]) -> str:
        """Format the recent development analysis."""
        lines = []
        now = datetime.now()
        lines.append(f"## Recent Development Focus ({now.strftime('%B %Y')})")
        
        # Statistics
        stats = analysis.get('statistics', {})
        if stats:
            lines.append(f"\n### Statistics")
            lines.append(f"- Total commits: {stats.get('total_commits', 0)}")
            if stats.get('breaking_changes', 0) > 0:
                lines.append(f"- ⚠️  Breaking changes: {stats['breaking_changes']}")
        
        # Achievements
        achievements = analysis.get('achievements', [])
        if achievements:
            lines.append(f"\n### Latest Achievements")
            for achievement in achievements:
                lines.append(f"- {achievement}")
        
        # Focus areas
        focus_areas = analysis.get('focus_areas', {})
        if focus_areas:
            lines.append(f"\n### Development Focus")
            for area, count in list(focus_areas.items())[:5]:
                area_name = area.replace('-', ' ').title()
                lines.append(f"- **{area_name}**: {count} commits")
        
        # Top changed files
        top_files = analysis.get('top_changed_files', [])
        if top_files:
            lines.append(f"\n### Most Active Files")
            for file, count in top_files[:3]:
                lines.append(f"- `{file}`: {count} changes")
        
        return '\n'.join(lines)
    
    def _validate_content(self, content: str) -> List[str]:
        """Validate the generated content."""
        errors = []
        
        # Check for truncated words (like "Implemented ation")
        truncated_pattern = r'\b\w+\s+ation\b'
        if re.search(truncated_pattern, content):
            errors.append("Found truncated words ending with 'ation'")
        
        # Check for empty sections
        for marker in ['DEPENDENCIES', 'ARCHITECTURE', 'RECENT', 'COMMANDS']:
            start = f"<!-- AUTO-GENERATED:{marker} -->"
            end = f"<!-- /AUTO-GENERATED:{marker} -->"
            start_idx = content.find(start)
            end_idx = content.find(end)
            if start_idx != -1 and end_idx != -1:
                section_content = content[start_idx + len(start):end_idx].strip()
                if not section_content:
                    errors.append(f"Empty {marker} section")
        
        # Check for broken markdown
        # Count backticks - should be even
        backtick_count = content.count('```')
        if backtick_count % 2 != 0:
            errors.append("Unmatched code block markers (```)")
        
        return errors
    
    def _extract_dependencies(self) -> Dict[str, List[str]]:
        """Extract dependencies from pyproject.toml."""
        try:
            if self.pyproject_file.exists():
                data = toml.load(self.pyproject_file)
                deps = data.get('project', {}).get('dependencies', [])
                optional = data.get('project', {}).get('optional-dependencies', {})
                
                categorized = {
                    'Core': self._categorize_deps(deps),
                    'Development': self._categorize_deps(optional.get('dev', []))
                }
                
                return categorized
        except Exception as e:
            print(f"⚠️  Error reading dependencies: {e}")
        
        return {}
    
    def _categorize_deps(self, deps: List[str]) -> Dict[str, List[str]]:
        """Categorize dependencies by purpose."""
        categories = {
            'CLI Framework': [],
            'Data Validation': [],
            'Testing': [],
            'Code Quality': [],
            'Other': []
        }
        
        for dep in deps:
            dep_lower = dep.lower()
            if 'typer' in dep_lower or 'click' in dep_lower:
                categories['CLI Framework'].append(dep)
            elif 'pydantic' in dep_lower or 'marshmallow' in dep_lower:
                categories['Data Validation'].append(dep)
            elif any(test in dep_lower for test in ['pytest', 'unittest', 'mock']):
                categories['Testing'].append(dep)
            elif any(qual in dep_lower for qual in ['black', 'ruff', 'mypy', 'flake8']):
                categories['Code Quality'].append(dep)
            else:
                categories['Other'].append(dep)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def _format_dependencies(self, deps: Dict[str, Dict[str, List[str]]]) -> str:
        """Format dependencies for display."""
        lines = []
        
        for section, categories in deps.items():
            if categories:
                lines.append(f"### {section} Dependencies")
                for category, dep_list in categories.items():
                    if dep_list:
                        lines.append(f"- **{category}**: {', '.join(dep_list)}")
                lines.append("")
        
        return '\n'.join(lines).strip()
    
    def _generate_architecture_tree(self) -> str:
        """Generate a tree view of the project architecture."""
        # This is simplified - in production you'd walk the actual tree
        # For now, return existing tree structure
        return """### Current Architecture
```
src/aditi/
├── __init__.py
├── cli.py                 # Main CLI interface
├── config.py              # Configuration management
├── commands/
│   ├── init.py           # Vale initialization
│   ├── check.py          # Rule checking
│   ├── fix.py            # Auto-fixing
│   └── journey.py        # Interactive workflow
├── rules/
│   ├── base.py           # Base rule classes
│   ├── registry.py       # Rule discovery
│   └── ...               # Individual rule implementations
├── vale_container.py      # Container management
└── processor.py          # Rule processing engine

tests/
├── unit/                 # Unit tests
└── integration/          # Integration tests

docs/
├── _posts/              # Blog posts
└── _design/             # Design documents
```"""
    
    def _extract_commands(self) -> Dict[str, List[Tuple[str, str]]]:
        """Extract common commands from documentation and code."""
        # This would scan README, docs, and code for command examples
        # For now, return standard commands
        return {
            'Development': [
                ('Install dependencies', 'pip install -e ".[dev]"'),
                ('Run tests', 'pytest'),
                ('Type checking', 'mypy src/'),
                ('Format code', 'black src/ tests/'),
                ('Lint code', 'ruff check src/ tests/')
            ],
            'Usage': [
                ('Initialize Vale', 'aditi init'),
                ('Check files', 'aditi check'),
                ('Start journey', 'aditi journey'),
                ('Fix issues', 'aditi fix --rule EntityReference')
            ]
        }
    
    def _format_commands(self, commands: Dict[str, List[Tuple[str, str]]]) -> str:
        """Format commands for display."""
        lines = []
        
        for section, cmd_list in commands.items():
            lines.append(f"### {section}")
            for desc, cmd in cmd_list:
                lines.append(f"- **{desc}**: `{cmd}`")
            lines.append("")
        
        return '\n'.join(lines).strip()
    
    def _are_changes_significant(self, original: str, updated: str) -> bool:
        """Check if changes are significant enough to warrant a commit."""
        import difflib
        
        # Get line-by-line diff
        diff_lines = list(difflib.unified_diff(
            original.splitlines(keepends=True),
            updated.splitlines(keepends=True),
            lineterm=''
        ))
        
        # Count actual content changes (exclude diff headers)
        content_changes = [line for line in diff_lines if line.startswith(('+', '-')) and not line.startswith(('+++', '---'))]
        
        # If no content changes, not significant
        if not content_changes:
            return False
        
        # Check for trivial-only changes
        trivial_patterns = [
            r'- Total commits: \d+',  # Commit count changes
            r'- `.*`: \d+ changes',   # File change count updates
            r'### Statistics',        # Statistics section updates
            r'### Most Active Files', # Most active files updates
        ]
        
        significant_changes = []
        for change_line in content_changes:
            line_content = change_line[1:].strip()  # Remove +/- prefix
            
            # Skip if this line matches trivial patterns
            is_trivial = any(re.search(pattern, line_content) for pattern in trivial_patterns)
            
            if not is_trivial and line_content:  # Ignore empty lines
                significant_changes.append(change_line)
        
        # Only significant if there are non-trivial changes
        return len(significant_changes) > 0
    
    def _show_diff(self, original: str, updated: str) -> None:
        """Show a diff between original and updated content."""
        import difflib
        
        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            updated.splitlines(keepends=True),
            fromfile='CLAUDE.md (original)',
            tofile='CLAUDE.md (updated)',
            n=3
        )
        
        print("\n📝 Changes that would be made:")
        print(''.join(diff))


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Update CLAUDE.md with project information')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without saving')
    parser.add_argument('--check', action='store_true', help='Check if updates are needed (exit 1 if changes needed)')
    args = parser.parse_args()
    
    updater = ImprovedClaudeMdUpdater()
    
    if args.check:
        # Check mode - create a backup, update, compare, then restore
        import tempfile
        import shutil
        
        original_content = updater.claude_md.read_text(encoding='utf-8')
        
        # Create a backup
        backup_path = updater.claude_md.with_suffix('.backup')
        shutil.copy2(updater.claude_md, backup_path)
        
        try:
            # Run the actual update
            success = updater.update_all_sections(dry_run=False)
            
            if success:
                updated_content = updater.claude_md.read_text(encoding='utf-8')
                
                # Compare content and check if changes are significant
                changes_significant = updater._are_changes_significant(original_content, updated_content)
                
                if changes_significant:
                    print("❌ CLAUDE.md needs updates")
                    exit_code = 1
                else:
                    print("✅ CLAUDE.md is up to date (only trivial changes)")
                    exit_code = 0
            else:
                print("❌ Error checking CLAUDE.md status")
                exit_code = 1
                
        finally:
            # Always restore the original
            shutil.move(backup_path, updater.claude_md)
            
        sys.exit(exit_code)
    else:
        success = updater.update_all_sections(dry_run=args.dry_run)
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()