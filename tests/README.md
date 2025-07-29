# Aditi Test Suite

This directory contains tests for the Aditi project, including regression prevention tests for Jekyll blog post management.

## Test Categories

### Unit Tests
- `test_*.py` - Standard unit tests for core functionality
- Located in `unit/` subdirectory

### Integration Tests  
- `test_cli_integration.py` - CLI command integration tests
- Located in `integration/` subdirectory

### Blog Post Validation Tests
- `test_blog_post_validation.py` - **Regression prevention for Jekyll front matter issues**

## Blog Post Validation

The `test_blog_post_validation.py` file implements comprehensive validation to prevent the Jekyll front matter issues that broke GitHub Pages deployment.

### What It Checks

#### 1. Front Matter Structure
- ✅ Required fields: `layout`, `title`, `date`, `author`, `tags`, `summary`
- ✅ Valid layout values (`post`)
- ✅ Proper date format: `YYYY-MM-DD HH:MM:SS ±HHMM`
- ✅ Tags as arrays (not strings)
- ❌ Placeholder content in published posts

#### 2. Filename Conventions
- ✅ Pattern: `YYYY-MM-DD-HHMM-post-title.md`
- ✅ Date consistency between filename and front matter

#### 3. Jekyll Configuration Safety
- ✅ Template files excluded from processing
- ✅ Drafts directory excluded
- ❌ Dangerous placeholder files

#### 4. Content Safety
- ❌ Files with `YYYY-MM-DD` pattern names
- ❌ Literal placeholder dates in content (except in code blocks)

### Running the Tests

#### Standalone Validation
```bash
# Quick validation check
python tests/test_blog_post_validation.py

# With pytest framework
python -m pytest tests/test_blog_post_validation.py -v
```

#### GitHub Actions Integration
The validation runs automatically on:
- Pushes that modify blog posts
- Pull requests affecting blog content
- Changes to Jekyll configuration
- Manual workflow triggers

### Validation Output Example

```
🔍 Validating blog posts...
Found 10 blog posts

📝 Checking 2025-07-29-0607-fixing-jekyll-front-matter-standardization.md
  ✅ Valid

⚙️  Checking Jekyll configuration...
🚨 Checking for dangerous files...

✅ All validations passed!
```

### Error Examples

The validator catches common issues:

```
❌ Validation failed with 3 errors:
  • 2025-07-29-1234-example-post.md: Missing required fields: {'layout', 'summary'}
  • 2025-07-29-1234-example-post.md: Invalid date format '2025-07-29', must match 'YYYY-MM-DD HH:MM:SS ±HHMM'
  • Found file with placeholder date pattern: docs/_posts/YYYY-MM-DD-template.md
```

## Adding New Tests

### For New Blog Post Rules
Add validation methods to the `BlogPostValidator` class:

```python
def validate_custom_rule(self, front_matter: Dict[str, Any], post_path: Path) -> List[str]:
    errors = []
    # Your validation logic here
    return errors
```

### For New Content Types
Extend the validator to handle other Jekyll content types:

```python
def validate_design_docs(self) -> List[str]:
    # Validate _design/ collection
    pass
```

## Lessons Learned Integration

This test suite directly addresses the root causes identified during the GitHub Pages deployment failure investigation:

1. **Template Management**: Ensures template files are properly excluded
2. **Front Matter Consistency**: Enforces standardized structure across all posts  
3. **Date Format Validation**: Prevents invalid date parsing errors
4. **Placeholder Detection**: Catches template content in published posts
5. **Configuration Safety**: Validates Jekyll exclusion rules

## Maintenance

- Update `REQUIRED_FIELDS` when adding new front matter requirements
- Extend `PLACEHOLDER_PATTERNS` for new template placeholders
- Add new validation methods for additional content rules
- Keep GitHub Actions workflow in sync with test requirements

## Dependencies

- `pytest` - Test framework
- `pyyaml` - YAML parsing for front matter
- `pathlib` - File system operations
- Standard library modules (`re`, `datetime`, etc.)

Install test dependencies:
```bash
pip install -e ".[dev]"
```