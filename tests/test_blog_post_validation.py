#!/usr/bin/env python3
"""
Blog Post Validation Tests

Prevents regressions in Jekyll front matter and blog post conventions
based on lessons learned from GitHub Pages deployment failures.

Key areas tested:
1. Front matter format consistency
2. Date format validation  
3. Filename conventions
4. Template file exclusions
5. Required fields presence
"""

import os
import re
import yaml
import pytest
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


class BlogPostValidator:
    """Validates blog post front matter and conventions."""
    
    # Standard front matter fields that should be present
    REQUIRED_FIELDS = {'layout', 'title', 'date', 'author', 'tags', 'summary'}
    
    # Valid layouts for blog posts
    VALID_LAYOUTS = {'post'}
    
    # Date format that Jekyll expects: YYYY-MM-DD HH:MM:SS -0400
    DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [+-]\d{4}$')
    
    # Filename pattern: YYYY-MM-DD-HHMM-post-title.md
    FILENAME_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}-\d{4}-.+\.md$')
    
    # Placeholder patterns that should NOT appear in published posts
    PLACEHOLDER_PATTERNS = [
        r'YYYY-MM-DD',
        r'Your Name',
        r'Your Blog Post Title Here',
        r'A brief.*summary.*appear in listings'
    ]
    
    def __init__(self, docs_path: str = 'docs'):
        self.docs_path = Path(docs_path)
        self.posts_path = self.docs_path / '_posts'
        
    def get_blog_posts(self) -> List[Path]:
        """Get all blog post files, excluding templates."""
        if not self.posts_path.exists():
            return []
            
        posts = []
        for post_file in self.posts_path.glob('*.md'):
            # Skip template files
            if 'template' in post_file.name.lower():
                continue
            posts.append(post_file)
        return posts
    
    def extract_front_matter(self, post_path: Path) -> Optional[Dict[str, Any]]:
        """Extract YAML front matter from a blog post."""
        try:
            content = post_path.read_text(encoding='utf-8')
            
            # Blog posts should start with ---
            if not content.startswith('---\n'):
                return None
                
            # Find the closing ---
            parts = content.split('---\n', 2)
            if len(parts) < 3:
                return None
                
            front_matter_yaml = parts[1]
            return yaml.safe_load(front_matter_yaml)
            
        except Exception as e:
            print(f"Error parsing {post_path}: {e}")
            return None
    
    def validate_front_matter_structure(self, front_matter: Dict[str, Any], post_path: Path) -> List[str]:
        """Validate front matter has required fields and correct structure."""
        errors = []
        
        # Check required fields
        missing_fields = self.REQUIRED_FIELDS - set(front_matter.keys())
        if missing_fields:
            errors.append(f"Missing required fields: {missing_fields}")
        
        # Validate layout
        layout = front_matter.get('layout')
        if layout not in self.VALID_LAYOUTS:
            errors.append(f"Invalid layout '{layout}', must be one of {self.VALID_LAYOUTS}")
        
        # Validate date format
        date_str = str(front_matter.get('date', ''))
        if not self.DATE_PATTERN.match(date_str):
            errors.append(f"Invalid date format '{date_str}', must match 'YYYY-MM-DD HH:MM:SS ±HHMM'")
        
        # Validate tags is a list
        tags = front_matter.get('tags', [])
        if not isinstance(tags, list):
            errors.append(f"Tags must be a list, got {type(tags).__name__}")
        
        # Check for placeholder content
        for field, value in front_matter.items():
            value_str = str(value)
            for pattern in self.PLACEHOLDER_PATTERNS:
                if re.search(pattern, value_str, re.IGNORECASE):
                    errors.append(f"Field '{field}' contains placeholder text: '{value_str}'")
        
        return errors
    
    def validate_filename_convention(self, post_path: Path) -> List[str]:
        """Validate filename follows YYYY-MM-DD-HHMM-title.md convention."""
        errors = []
        
        filename = post_path.name
        if not self.FILENAME_PATTERN.match(filename):
            errors.append(f"Filename '{filename}' doesn't match pattern YYYY-MM-DD-HHMM-title.md")
        
        return errors
    
    def validate_date_consistency(self, front_matter: Dict[str, Any], post_path: Path) -> List[str]:
        """Validate filename date matches front matter date."""
        errors = []
        
        filename = post_path.name
        # Extract date from filename: YYYY-MM-DD-HHMM
        filename_match = re.match(r'^(\d{4})-(\d{2})-(\d{2})-(\d{2})(\d{2})', filename)
        if not filename_match:
            return errors  # Already caught by filename validation
        
        year, month, day, hour, minute = filename_match.groups()
        filename_date = f"{year}-{month}-{day}"
        filename_time = f"{hour}:{minute}"
        
        # Extract date from front matter
        date_str = str(front_matter.get('date', ''))
        frontmatter_match = re.match(r'^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):', date_str)
        if frontmatter_match:
            fm_year, fm_month, fm_day, fm_hour, fm_minute = frontmatter_match.groups()
            frontmatter_date = f"{fm_year}-{fm_month}-{fm_day}"
            frontmatter_time = f"{fm_hour}:{fm_minute}"
            
            if filename_date != frontmatter_date:
                errors.append(f"Filename date '{filename_date}' doesn't match front matter date '{frontmatter_date}'")
        
        return errors
    
    def check_jekyll_config_exclusions(self) -> List[str]:
        """Validate Jekyll config excludes template files and dangerous directories."""
        errors = []
        
        config_path = self.docs_path / '_config.yml'
        if not config_path.exists():
            errors.append("_config.yml not found")
            return errors
        
        try:
            config = yaml.safe_load(config_path.read_text())
            exclude_list = config.get('exclude', [])
            
            # Check for template exclusions
            template_patterns = ['template', 'drafts/']
            for pattern in template_patterns:
                if not any(pattern in item for item in exclude_list):
                    errors.append(f"_config.yml should exclude files/dirs matching '{pattern}'")
            
        except Exception as e:
            errors.append(f"Error reading _config.yml: {e}")
        
        return errors
    
    def find_dangerous_files(self) -> List[str]:
        """Find files that might break Jekyll builds."""
        errors = []
        
        # Search for files with placeholder dates
        for pattern in ['**/YYYY-MM-DD*', '**/yyyy-mm-dd*']:
            for dangerous_file in self.docs_path.glob(pattern):
                errors.append(f"Found file with placeholder date pattern: {dangerous_file}")
        
        # Search for files containing literal placeholder dates in content
        for md_file in self.docs_path.rglob('*.md'):
            try:
                content = md_file.read_text(encoding='utf-8')
                # Allow placeholder dates if they have comments or are in code blocks
                if ('date: YYYY-MM-DD HH:MM:SS' in content and 
                    'template' not in md_file.name.lower() and
                    '# placeholder' not in content and
                    '```yaml' not in content):
                    errors.append(f"File contains literal placeholder date: {md_file}")
            except Exception:
                pass  # Skip files that can't be read
        
        return errors


# Test implementation
@pytest.fixture
def validator():
    """Create a BlogPostValidator instance."""
    return BlogPostValidator()


def test_blog_posts_exist(validator):
    """Test that blog posts directory exists and contains posts."""
    posts = validator.get_blog_posts()
    assert len(posts) > 0, "No blog posts found in docs/_posts/"


def test_front_matter_structure(validator):
    """Test that all blog posts have valid front matter structure."""
    posts = validator.get_blog_posts()
    all_errors = []
    
    for post_path in posts:
        front_matter = validator.extract_front_matter(post_path)
        assert front_matter is not None, f"Could not parse front matter in {post_path}"
        
        errors = validator.validate_front_matter_structure(front_matter, post_path)
        if errors:
            all_errors.extend([f"{post_path.name}: {error}" for error in errors])
    
    assert not all_errors, f"Front matter validation errors:\n" + "\n".join(all_errors)


def test_filename_conventions(validator):
    """Test that all blog posts follow filename conventions."""
    posts = validator.get_blog_posts()
    all_errors = []
    
    for post_path in posts:
        errors = validator.validate_filename_convention(post_path)
        if errors:
            all_errors.extend([f"{post_path.name}: {error}" for error in errors])
    
    assert not all_errors, f"Filename convention errors:\n" + "\n".join(all_errors)


def test_date_consistency(validator):
    """Test that filename dates match front matter dates."""
    posts = validator.get_blog_posts()
    all_errors = []
    
    for post_path in posts:
        front_matter = validator.extract_front_matter(post_path)
        if front_matter:
            errors = validator.validate_date_consistency(front_matter, post_path)
            if errors:
                all_errors.extend([f"{post_path.name}: {error}" for error in errors])
    
    assert not all_errors, f"Date consistency errors:\n" + "\n".join(all_errors)


def test_jekyll_config_exclusions(validator):
    """Test that Jekyll config properly excludes dangerous files."""
    errors = validator.check_jekyll_config_exclusions()
    assert not errors, f"Jekyll config validation errors:\n" + "\n".join(errors)


def test_no_dangerous_files(validator):
    """Test that no files exist that could break Jekyll builds."""
    errors = validator.find_dangerous_files()
    assert not errors, f"Dangerous files found:\n" + "\n".join(errors)


def test_no_placeholder_content(validator):
    """Test that published posts don't contain placeholder content."""
    posts = validator.get_blog_posts()
    all_errors = []
    
    for post_path in posts:
        front_matter = validator.extract_front_matter(post_path)
        if front_matter:
            # Check for common placeholder patterns in front matter
            for field, value in front_matter.items():
                value_str = str(value)
                for pattern in validator.PLACEHOLDER_PATTERNS:
                    if re.search(pattern, value_str, re.IGNORECASE):
                        all_errors.append(f"{post_path.name}: Field '{field}' contains placeholder: '{value_str}'")
    
    assert not all_errors, f"Placeholder content found:\n" + "\n".join(all_errors)


if __name__ == '__main__':
    """Run validation checks directly."""
    validator = BlogPostValidator()
    
    print("🔍 Validating blog posts...")
    
    # Run all validations
    posts = validator.get_blog_posts()
    print(f"Found {len(posts)} blog posts")
    
    all_errors = []
    
    # Check each post
    for post_path in posts:
        print(f"\n📝 Checking {post_path.name}")
        
        front_matter = validator.extract_front_matter(post_path)
        if not front_matter:
            all_errors.append(f"{post_path.name}: Could not parse front matter")
            continue
        
        errors = []
        errors.extend(validator.validate_front_matter_structure(front_matter, post_path))
        errors.extend(validator.validate_filename_convention(post_path))
        errors.extend(validator.validate_date_consistency(front_matter, post_path))
        
        if errors:
            all_errors.extend([f"{post_path.name}: {error}" for error in errors])
        else:
            print("  ✅ Valid")
    
    # Check Jekyll config
    print(f"\n⚙️  Checking Jekyll configuration...")
    config_errors = validator.check_jekyll_config_exclusions()
    all_errors.extend(config_errors)
    
    # Check for dangerous files
    print(f"\n🚨 Checking for dangerous files...")
    dangerous_errors = validator.find_dangerous_files()
    all_errors.extend(dangerous_errors)
    
    # Summary
    if all_errors:
        print(f"\n❌ Validation failed with {len(all_errors)} errors:")
        for error in all_errors:
            print(f"  • {error}")
        exit(1)
    else:
        print(f"\n✅ All validations passed!")
        exit(0)