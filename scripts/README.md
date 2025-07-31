# Aditi Scripts

Utility scripts for the Aditi project.

## Release Management

### 🚀 release.py
**Complete release automation script** - Handles the entire release process in one command.

```bash
# Bump patch version and release (0.1.7 → 0.1.8)
python scripts/release.py patch

# Bump minor version and release (0.1.7 → 0.2.0)
python scripts/release.py minor

# Bump major version and release (0.1.7 → 1.0.0)
python scripts/release.py major

# Dry run to see what would happen
python scripts/release.py patch --dry-run

# Skip tests during release
python scripts/release.py patch --skip-tests

# Only do git operations (no PyPI upload)
python scripts/release.py patch --skip-pypi
```

**What it does:**
1. Bumps version in `pyproject.toml` (single source of truth!)
2. Runs tests
3. Builds the package
4. Uploads to PyPI
5. Creates git commit and tag
6. Pushes to GitHub
7. Creates GitHub release

### 📝 bump-version.py
**Simple version bump script** - Only updates the version number.

```bash
# Show current version
python scripts/bump-version.py

# Bump patch version (0.1.7 → 0.1.8)
python scripts/bump-version.py patch

# Bump minor version (0.1.7 → 0.2.0)
python scripts/bump-version.py minor

# Set specific version
python scripts/bump-version.py --set 1.2.3
```

### 📦 publish-to-pypi.sh (Legacy)
**Note:** This script is being replaced by `release.py`. It still works but requires manual version updates in multiple files.

## Blog Post Creation

### `new-blog-post.sh`

Creates a new blog post with correct filename and timestamp formatting.

**Usage:**
```bash
./scripts/new-blog-post.sh "Your Blog Post Title"
```

**What it does:**
- Generates filename: `YYYY-MM-DD-HHMM-post-title.md`
- Creates proper timestamp in front matter with current timezone
- Uses the blog post template as a starting point
- Provides next steps for editing and publishing

**Example:**
```bash
./scripts/new-blog-post.sh "Implementing New Feature"
# Creates: 2025-07-27-1423-implementing-new-feature.md
# With timestamp: 2025-07-27 14:23:45 -0400
```

**Benefits:**
- Ensures chronological sorting in Jekyll
- Prevents filename/timestamp mismatches
- Consistent formatting across all blog posts
- Reduces manual errors in date/time formatting

## Future Scripts

Additional utility scripts will be added here as the project grows.