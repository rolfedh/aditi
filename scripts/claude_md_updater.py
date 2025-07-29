#!/usr/bin/env python3
"""
Intelligent CLAUDE.md updater that analyzes project state
and updates specific sections automatically.

This is the core of the Hybrid Approach for CLAUDE.md automation.
"""

import os
import re
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import sys

try:
    import toml
except ImportError:
    print("Installing toml dependency...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "toml"])
    import toml


class ClaudeMdUpdater:
    """Intelligent CLAUDE.md updater with project state analysis."""
    
    def __init__(self, project_root: str = "."):
        self.root = Path(project_root).resolve()
        self.template_file = self.root / "CLAUDE.template.md"
        self.output_file = self.root / "CLAUDE.md"
        self.pyproject_file = self.root / "pyproject.toml"
        
    def update_all_sections(self, force: bool = False) -> bool:
        """Update all auto-generated sections in CLAUDE.md."""
        if not self.template_file.exists():
            print(f"❌ Template file not found: {self.template_file}")
            return False
            
        print("🔄 Updating CLAUDE.md from template...")
        
        # Read template
        template_content = self.template_file.read_text(encoding='utf-8')
        
        # Replace date placeholders
        template_content = self._replace_date_placeholders(template_content)
        
        # Update auto-generated sections
        template_content = self._update_dependencies_section(template_content)
        template_content = self._update_architecture_section(template_content)
        template_content = self._update_commands_section(template_content)
        template_content = self._update_completed_section(template_content)
        template_content = self._update_recent_section(template_content)
        
        # Check if content changed
        if self.output_file.exists() and not force:
            current_content = self.output_file.read_text(encoding='utf-8')
            if current_content == template_content:
                print("✅ CLAUDE.md is already up to date")
                return False
        
        # Write updated content
        self.output_file.write_text(template_content, encoding='utf-8')
        print("✅ CLAUDE.md updated successfully")
        return True
    
    def _replace_date_placeholders(self, content: str) -> str:
        """Replace date placeholders with current values."""
        now = datetime.now()
        content = content.replace("{{ current_month }}", now.strftime("%B"))
        content = content.replace("{{ current_year }}", str(now.year))
        return content
    
    def _update_dependencies_section(self, content: str) -> str:
        """Update dependencies based on pyproject.toml."""
        dependencies = self._extract_dependencies()
        
        dep_content = []
        for category, deps in dependencies.items():
            if deps:
                dep_content.append(f"- **{category}**: {', '.join(deps)}")
        
        if dep_content:
            new_deps = '\n'.join(dep_content)
            return self._replace_auto_generated_section(content, "DEPENDENCIES", new_deps)
        
        return content
    
    def _update_architecture_section(self, content: str) -> str:
        """Generate current architecture from file structure."""
        tree = self._generate_project_tree()
        return self._replace_auto_generated_section(content, "ARCHITECTURE", f"### Current Architecture\n```\n{tree}\n```")
    
    def _update_commands_section(self, content: str) -> str:
        """Update commands based on available scripts and tools."""
        commands = self._discover_commands()
        commands_content = self._format_commands(commands)
        return self._replace_auto_generated_section(content, "COMMANDS", commands_content)
    
    def _update_completed_section(self, content: str) -> str:
        """Update completed items based on project analysis."""
        completed_items = self._analyze_completed_features()
        completed_content = self._format_completed_items(completed_items)
        return self._replace_auto_generated_section(content, "COMPLETED", completed_content)
    
    def _update_recent_section(self, content: str) -> str:
        """Update recent development focus based on commit analysis."""
        recent_analysis = self._analyze_recent_development()
        recent_content = self._format_recent_analysis(recent_analysis)
        return self._replace_auto_generated_section(content, "RECENT", recent_content)
    
    def _extract_dependencies(self) -> Dict[str, List[str]]:
        """Extract dependencies from pyproject.toml."""
        if not self.pyproject_file.exists():
            return {}
        
        try:
            data = toml.load(self.pyproject_file)
            project = data.get('project', {})
            
            dependencies = {
                'Core Dependencies': [],
                'Development Tools': [],
                'Testing Framework': [],
                'Documentation': [],
                'CI/CD': []
            }
            
            # Main dependencies
            for dep in project.get('dependencies', []):
                if 'typer' in dep.lower():
                    dependencies['Core Dependencies'].append('Typer CLI framework')
                elif 'rich' in dep.lower():
                    dependencies['Core Dependencies'].append('Rich progress indicators')
                elif 'pydantic' in dep.lower():
                    dependencies['Core Dependencies'].append('Pydantic configuration management')
            
            # Dev dependencies
            dev_deps = project.get('optional-dependencies', {}).get('dev', [])
            for dep in dev_deps:
                if 'pytest' in dep.lower():
                    dependencies['Testing Framework'].append('pytest with PyYAML')
                elif 'ruff' in dep.lower():
                    dependencies['Development Tools'].append('Ruff linter')
                elif 'black' in dep.lower():
                    dependencies['Development Tools'].append('Black formatter')
                elif 'mypy' in dep.lower():
                    dependencies['Development Tools'].append('MyPy type checker')
            
            # Check for Jekyll/GitHub Actions
            if (self.root / 'docs' / '_config.yml').exists():
                dependencies['Documentation'].append('Jekyll with Just the Docs theme')
            
            if (self.root / '.github' / 'workflows').exists():
                dependencies['CI/CD'].append('GitHub Actions workflows')
            
            # Container support
            if (self.root / 'src' / 'aditi' / 'vale_container.py').exists():
                dependencies['Core Dependencies'].append('Vale containerization (Podman/Docker)')
            
            return {k: v for k, v in dependencies.items() if v}
            
        except Exception as e:
            print(f"⚠️  Error reading pyproject.toml: {e}")
            return {}
    
    def _generate_project_tree(self) -> str:
        """Generate ASCII tree of project structure."""
        important_paths = [
            'src/aditi',
            'tests',
            'docs',
            '.github/workflows',
            'scripts'
        ]
        
        tree_lines = []
        for path_str in important_paths:
            path = self.root / path_str
            if path.exists():
                tree_lines.extend(self._generate_tree_for_path(path, path_str))
        
        return '\n'.join(tree_lines)
    
    def _generate_tree_for_path(self, path: Path, prefix: str, max_depth: int = 3) -> List[str]:
        """Generate tree structure for a specific path."""
        lines = [f"{prefix}/"]
        
        if path.is_dir() and max_depth > 0:
            items = []
            try:
                for item in sorted(path.iterdir()):
                    if item.name.startswith('.') and item.name not in ['.github']:
                        continue
                    if item.name in ['__pycache__', '.pytest_cache', 'node_modules']:
                        continue
                    items.append(item)
            except PermissionError:
                return lines
            
            for i, item in enumerate(items):
                is_last = i == len(items) - 1
                connector = "└── " if is_last else "├── "
                
                if item.is_dir():
                    lines.append(f"{'│   ' * (prefix.count('/') - 1)}{'    ' if is_last else '│   '}{connector}{item.name}/")
                    if max_depth > 1:
                        sub_lines = self._generate_tree_for_path(
                            item, 
                            f"{prefix}/{item.name}", 
                            max_depth - 1
                        )[1:]  # Skip the first line
                        lines.extend(sub_lines)
                else:
                    comment = self._get_file_comment(item)
                    file_line = f"{'│   ' * (prefix.count('/') - 1)}{'    ' if is_last else '│   '}{connector}{item.name}"
                    if comment:
                        file_line += f"  # {comment}"
                    lines.append(file_line)
        
        return lines
    
    def _get_file_comment(self, file_path: Path) -> str:
        """Get descriptive comment for a file based on its content or purpose."""
        name = file_path.name
        
        # Common file patterns
        comments = {
            '__init__.py': 'Package initialization',
            'cli.py': 'Main CLI interface',
            'config.py': 'Configuration management',
            'conftest.py': 'Shared test fixtures',
            'pyproject.toml': 'Project configuration',
            '_config.yml': 'Jekyll configuration',
            'post-template.md': 'Blog post template',
            'README.md': 'Documentation'
        }
        
        if name in comments:
            return comments[name]
        
        # Pattern-based comments
        if name.endswith('_test.py') or name.startswith('test_'):
            return 'Test module'
        elif name.endswith('.yml') and 'workflow' in str(file_path):
            return 'GitHub Actions workflow'
        elif name.endswith('.md') and 'docs' in str(file_path):
            return 'Documentation'
        
        return ""
    
    def _discover_commands(self) -> Dict[str, List[str]]:
        """Discover available commands and tools in the project."""
        commands = {
            'Container Setup & Testing': [],
            'Blog Post Management': [],
            'GitHub Pages Development': [],
            'Python Development': []
        }
        
        # Check for test scripts
        if (self.root / 'test_vale_integration.py').exists():
            commands['Container Setup & Testing'].append('Test Vale integration: `python test_vale_integration.py`')
        if (self.root / 'test_asciidocdita_rules.py').exists():
            commands['Container Setup & Testing'].append('Test AsciiDocDITA rules: `python test_asciidocdita_rules.py`')
        
        # Blog post validation
        if (self.root / 'tests' / 'test_blog_post_validation.py').exists():
            commands['Blog Post Management'].extend([
                '**Validate blog posts**: `python tests/test_blog_post_validation.py`',
                '**Run specific validation tests**: `python -m pytest tests/test_blog_post_validation.py -v`'
            ])
        
        # Jekyll development
        if (self.root / 'docs' / '_config.yml').exists():
            commands['GitHub Pages Development'].extend([
                '**Local development**: `cd docs && bundle exec jekyll serve`',
                '**Validation URL**: `http://localhost:4000/aditi/`'
            ])
        
        # Python development
        if self.pyproject_file.exists():
            commands['Python Development'].extend([
                '**Install dependencies**: `pip install -e ".[dev]"`',
                '**Run tests**: `pytest`',
                '**Type checking**: `mypy src/`',
                '**Code formatting**: `black src/ tests/`',
                '**Linting**: `ruff check src/ tests/`'
            ])
        
        return {k: v for k, v in commands.items() if v}
    
    def _format_commands(self, commands: Dict[str, List[str]]) -> str:
        """Format commands section."""
        sections = []
        for category, cmd_list in commands.items():
            sections.append(f"### {category}")
            for cmd in cmd_list:
                sections.append(f"- {cmd}")
            sections.append("")
        
        return "## Common Commands\n\n" + '\n'.join(sections).rstrip()
    
    def _analyze_completed_features(self) -> Dict[str, List[str]]:
        """Analyze project to determine completed features."""
        completed = {
            'Phase 0': [],
            'Phase 1': [],
            'Phase 2': [],
            'Documentation & Quality Assurance': []
        }
        
        # Check for Phase 0 completions
        if (self.root / 'src' / 'aditi' / 'vale_container.py').exists():
            completed['Phase 0'].append('✅ Vale container integration with Podman/Docker support')
        if (self.root / 'src' / 'aditi' / 'commands' / 'init.py').exists():
            completed['Phase 0'].append('✅ Init command with Rich progress indicators')
        
        # Check for Phase 1 completions
        if self.pyproject_file.exists():
            completed['Phase 1'].append('✅ Modern Python packaging with pyproject.toml')
        if (self.root / 'src' / 'aditi' / 'cli.py').exists():
            completed['Phase 1'].append('✅ Complete CLI structure with Typer framework')
        if (self.root / 'src' / 'aditi' / 'config.py').exists():
            completed['Phase 1'].append('✅ Configuration management with Pydantic models')
        if (self.root / 'tests').exists():
            completed['Phase 1'].append('✅ Comprehensive test suite (unit and integration)')
        
        # Check for Phase 2 completions (Rule Engine Implementation)
        rules_dir = self.root / 'src' / 'aditi' / 'rules'
        if rules_dir.exists():
            # Count implemented rules (exclude __init__.py, base.py, registry.py)
            rule_files = [f for f in rules_dir.glob('*.py') 
                         if f.name not in ['__init__.py', 'base.py', 'registry.py']]
            rule_count = len(rule_files)
            
            if rule_count >= 25:  # Significant rule implementation threshold
                completed['Phase 2'].extend([
                    f'✅ Complete AsciiDocDITA rule engine with {rule_count} implemented rules',
                    '✅ Non-deterministic pattern implementation for consistent rule structure',
                    '✅ Rule registry system for dynamic rule discovery and execution'
                ])
            
            # Check for specific core rules
            if (rules_dir / 'content_type.py').exists():
                completed['Phase 2'].append('✅ ContentType rule (prerequisite for content-dependent rules)')
            if (rules_dir / 'entity_reference.py').exists():
                completed['Phase 2'].append('✅ EntityReference rule with deterministic fixes')
                
        # Check for vale parser and processor
        if (self.root / 'src' / 'aditi' / 'vale_parser.py').exists():
            completed['Phase 2'].append('✅ Vale output parsing and violation processing')
        if (self.root / 'src' / 'aditi' / 'processor.py').exists():
            completed['Phase 2'].append('✅ Document processing pipeline with rule application')
        if (self.root / 'src' / 'aditi' / 'scanner.py').exists():
            completed['Phase 2'].append('✅ File scanning and AsciiDoc document discovery')
        
        # Check for Documentation & QA completions
        if (self.root / 'tests' / 'test_blog_post_validation.py').exists():
            completed['Documentation & Quality Assurance'].extend([
                '✅ Blog post validation test suite with regression prevention',
                '✅ Jekyll front matter standardization across all blog posts'
            ])
        if (self.root / '.github' / 'workflows' / 'validate-blog-posts.yml').exists():
            completed['Documentation & Quality Assurance'].append('✅ GitHub Actions workflow for automated blog post validation')
        
        return {k: v for k, v in completed.items() if v}
    
    def _format_completed_items(self, completed: Dict[str, List[str]]) -> str:
        """Format completed items section."""
        sections = []
        for phase, items in completed.items():
            sections.append(f"### Completed ({phase})")
            sections.extend(items)
            sections.append("")
        
        return '\n'.join(sections).rstrip()
    
    def _analyze_recent_development(self) -> Dict[str, any]:
        """Analyze recent commits to understand development focus."""
        try:
            # Get commits from last 30 days
            since_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            cmd = ['git', 'log', f'--since={since_date}', '--oneline', '--no-merges']
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.root)
            
            if result.returncode != 0:
                return {'achievements': [], 'focus_areas': [], 'lessons': []}
            
            commits = result.stdout.strip().split('\n')
            if not commits or commits == ['']:
                return {'achievements': [], 'focus_areas': [], 'lessons': []}
            
            # Analyze commit themes
            themes = self._extract_commit_themes(commits)
            achievements = self._extract_achievements(commits)
            lessons = self._extract_lessons(commits)
            
            return {
                'achievements': achievements[:5],  # Top 5
                'focus_areas': themes[:3],         # Top 3 themes
                'lessons': lessons[:3]             # Top 3 lessons
            }
            
        except Exception as e:
            print(f"⚠️  Error analyzing recent development: {e}")
            return {'achievements': [], 'focus_areas': [], 'lessons': []}
    
    def _extract_commit_themes(self, commits: List[str]) -> List[str]:
        """Extract development themes from commit messages."""
        themes = {}
        
        for commit in commits:
            if not commit.strip():
                continue
            
            message = commit.split(' ', 1)[1] if ' ' in commit else commit
            
            # Categorize by commit prefixes and keywords
            if any(word in message.lower() for word in ['test', 'validation', 'pytest']):
                themes['Testing & Validation'] = themes.get('Testing & Validation', 0) + 1
            elif any(word in message.lower() for word in ['jekyll', 'blog', 'front matter']):
                themes['Documentation Infrastructure'] = themes.get('Documentation Infrastructure', 0) + 1
            elif any(word in message.lower() for word in ['workflow', 'github actions', 'ci']):
                themes['CI/CD Automation'] = themes.get('CI/CD Automation', 0) + 1
            elif any(word in message.lower() for word in ['fix', 'bug', 'error']):
                themes['Bug Fixes'] = themes.get('Bug Fixes', 0) + 1
            elif any(word in message.lower() for word in ['feat', 'add', 'implement']):
                themes['Feature Development'] = themes.get('Feature Development', 0) + 1
        
        # Sort by frequency
        return sorted(themes.keys(), key=lambda x: themes[x], reverse=True)
    
    def _extract_achievements(self, commits: List[str]) -> List[str]:
        """Extract key achievements from commit messages."""
        achievements = []
        
        for commit in commits:
            if not commit.strip():
                continue
                
            message = commit.split(' ', 1)[1] if ' ' in commit else commit
            
            # Look for achievement indicators
            if 'feat:' in message.lower():
                feature = message.split('feat:', 1)[1].strip()
                achievements.append(f"✅ {feature.split('.')[0].capitalize()}")
            elif 'implement' in message.lower():
                impl = message.lower().split('implement', 1)[1].strip()
                achievements.append(f"✅ Implemented {impl.split('.')[0]}")
            elif 'add' in message.lower() and any(word in message.lower() for word in ['test', 'validation', 'workflow']):
                achievements.append(f"✅ {message.split('add', 1)[1].strip().split('.')[0].capitalize()}")
        
        return list(set(achievements))  # Remove duplicates
    
    def _extract_lessons(self, commits: List[str]) -> List[str]:
        """Extract lessons learned from commit messages."""
        lessons = []
        
        for commit in commits:
            if not commit.strip():
                continue
                
            message = commit.split(' ', 1)[1] if ' ' in commit else commit
            
            # Look for fix patterns that indicate lessons
            if 'fix:' in message.lower():
                if 'jekyll' in message.lower() or 'front matter' in message.lower():
                    lessons.append("Jekyll requires strict date formatting - template files need exclusion")
                elif 'validation' in message.lower():
                    lessons.append("Comprehensive validation prevents deployment failures")
                elif 'workflow' in message.lower():
                    lessons.append("CI/CD workflows need careful dependency management")
        
        return list(set(lessons))  # Remove duplicates
    
    def _format_recent_analysis(self, analysis: Dict[str, any]) -> str:
        """Format recent development analysis."""
        now = datetime.now()
        content = [f"## Recent Development Focus ({now.strftime('%B %Y')})"]
        
        if analysis['achievements']:
            content.append("\n### Latest Achievements")
            content.extend([f"- {achievement}" for achievement in analysis['achievements']])
        
        if analysis['focus_areas']:
            content.append("\n### Current Focus Areas")
            content.extend([f"- **{area}**: Active development and improvements" for area in analysis['focus_areas']])
        
        if analysis['lessons']:
            content.append("\n### Key Lessons Learned")
            content.extend([f"- {lesson}" for lesson in analysis['lessons']])
        
        return '\n'.join(content)
    
    def _replace_auto_generated_section(self, content: str, section_name: str, new_content: str) -> str:
        """Replace an auto-generated section in the content."""
        start_marker = f"<!-- AUTO-GENERATED:{section_name} -->"
        end_marker = f"<!-- /AUTO-GENERATED:{section_name} -->"
        
        pattern = f"{re.escape(start_marker)}.*?{re.escape(end_marker)}"
        replacement = f"{start_marker}\n{new_content}\n{end_marker}"
        
        return re.sub(pattern, replacement, content, flags=re.DOTALL)


def main():
    """Main entry point for the CLAUDE.md updater."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Update CLAUDE.md from template with current project state")
    parser.add_argument('--force', action='store_true', help='Force update even if no changes detected')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be updated without making changes')
    parser.add_argument('--section', choices=['deps', 'arch', 'commands', 'completed', 'recent'], 
                       help='Update only a specific section')
    
    args = parser.parse_args()
    
    updater = ClaudeMdUpdater()
    
    if args.dry_run:
        print("🔍 Dry run mode - showing what would be updated:")
        # Implementation for dry run
        return
    
    try:
        updated = updater.update_all_sections(force=args.force)
        if updated:
            print("📝 CLAUDE.md has been updated with current project state")
        else:
            print("✨ CLAUDE.md is already current")
            
    except Exception as e:
        print(f"❌ Error updating CLAUDE.md: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())