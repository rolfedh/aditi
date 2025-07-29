# CLAUDE.md Automation System

This document describes the **Hybrid Approach** for automating CLAUDE.md updates, ensuring it stays synchronized with the project's current state.

## Overview

The automation system uses multiple layers to keep CLAUDE.md current:

1. **Template-based foundation** for structure and consistency
2. **Smart scripts** for dynamic content generation
3. **GitHub Actions** for scheduled and event-driven updates
4. **Git hooks** for immediate updates on significant changes

## Architecture

```
CLAUDE.md Automation System
├── CLAUDE.template.md           # Template with auto-generated sections
├── scripts/
│   ├── claude_md_updater.py     # Core updater script
│   ├── install-git-hooks.sh     # Git hooks installer
│   └── manage-git-hooks.sh      # Hook management utility
├── .github/workflows/
│   └── update-claude-md.yml     # Automated updates via GitHub Actions
└── .git/hooks/                  # Local git hooks (installed)
    ├── post-commit              # Auto-update after commits
    └── pre-push                 # Validate before pushing
```

## Components

### 1. Template System (`CLAUDE.template.md`)

The template contains static content plus auto-generated sections marked with:

```markdown
<!-- AUTO-GENERATED:SECTION_NAME -->
Content gets replaced here automatically
<!-- /AUTO-GENERATED:SECTION_NAME -->
```

**Auto-generated sections:**
- `DEPENDENCIES` - Dependencies from pyproject.toml
- `ARCHITECTURE` - Current project file structure
- `COMMANDS` - Available commands and tools
- `COMPLETED` - Implementation status based on project analysis
- `RECENT` - Recent development focus from commit analysis

### 2. Smart Updater Script (`scripts/claude_md_updater.py`)

**Features:**
- Analyzes project structure to generate architecture diagrams
- Extracts dependencies from `pyproject.toml`
- Discovers available commands and tools
- Analyzes recent commits for development themes
- Updates only changed sections to minimize noise

**Usage:**
```bash
# Update all sections
python scripts/claude_md_updater.py

# Force update even if no changes detected
python scripts/claude_md_updater.py --force

# Update specific section only
python scripts/claude_md_updater.py --section deps
```

### 3. GitHub Actions Workflow (`.github/workflows/update-claude-md.yml`)

**Triggers:**
- Push to main branch affecting key files (`src/`, `tests/`, `pyproject.toml`, etc.)
- Weekly schedule (Sundays at 6 AM UTC)
- Manual workflow dispatch

**Process:**
1. Checks out repository with full history
2. Runs the updater script
3. Commits and pushes changes if CLAUDE.md was updated
4. Creates detailed summary of changes

### 4. Git Hooks

**post-commit hook:**
- Triggers after commits affecting significant files
- Auto-updates CLAUDE.md and amends the commit
- Provides immediate feedback on changes

**pre-push hook:**
- Validates CLAUDE.md sync before pushing
- Auto-commits updates if needed
- Ensures remote repository always has current CLAUDE.md

## Setup

### Initial Setup

1. **Install the system:**
   ```bash
   # Install git hooks
   ./scripts/install-git-hooks.sh
   
   # Test the updater
   python scripts/claude_md_updater.py
   ```

2. **Dependencies:**
   ```bash
   pip install toml  # For pyproject.toml parsing
   ```

### Hook Management

```bash
# Check hook status
./scripts/manage-git-hooks.sh status

# Remove hooks
./scripts/manage-git-hooks.sh remove

# Reinstall hooks
./scripts/manage-git-hooks.sh install

# Test updater
./scripts/manage-git-hooks.sh test
```

## How It Works

### Automatic Updates

1. **On commit** (if changes affect `src/`, `tests/`, `pyproject.toml`, or workflows):
   ```
   git commit -m "feat: add new feature"
   → post-commit hook triggers
   → CLAUDE.md updated automatically
   → commit amended to include changes
   ```

2. **On push** (validation):
   ```
   git push
   → pre-push hook validates CLAUDE.md sync
   → auto-commits updates if needed
   → push continues with current CLAUDE.md
   ```

3. **Via GitHub Actions** (weekly or on significant changes):
   ```
   Weekly schedule or push to main
   → workflow runs updater script
   → commits and pushes changes
   → creates summary of updates
   ```

### Manual Updates

```bash
# Update all sections
python scripts/claude_md_updater.py

# Force update (ignore change detection)
python scripts/claude_md_updater.py --force

# Update specific section
python scripts/claude_md_updater.py --section arch
```

## What Gets Updated Automatically

### Dependencies Section
- Extracts from `pyproject.toml`
- Categorizes by purpose (Core, Development, Testing, etc.)
- Detects Jekyll, GitHub Actions, and container support

### Architecture Section  
- Generates ASCII tree of project structure
- Includes file comments for important files
- Focuses on key directories (`src/`, `tests/`, `docs/`, etc.)
- Excludes noise (caches, temporary files)

### Commands Section
- Discovers available scripts and tools
- Categorizes by purpose (Testing, Development, etc.)
- Includes common development workflows

### Implementation Status
- Analyzes project to detect completed features
- Checks for key files to determine phase completion
- Updates automatically as project evolves

### Recent Development Focus
- Analyzes commits from last 30 days
- Extracts development themes and achievements
- Identifies lessons learned from commit messages
- Updates monthly with current focus areas

## Customization

### Adding New Auto-Generated Sections

1. **In template** (`CLAUDE.template.md`):
   ```markdown
   <!-- AUTO-GENERATED:NEWSECTION -->
   Default content here
   <!-- /AUTO-GENERATED:NEWSECTION -->
   ```

2. **In updater script** (`scripts/claude_md_updater.py`):
   ```python
   def _update_newsection_section(self, content: str) -> str:
       new_content = self._generate_new_section_content()
       return self._replace_auto_generated_section(content, "NEWSECTION", new_content)
   ```

3. **Add to update pipeline:**
   ```python
   def update_all_sections(self):
       # ... existing updates
       template_content = self._update_newsection_section(template_content)
   ```

### Modifying Update Triggers

**Git hooks** (local development):
Edit the file patterns in `.git/hooks/post-commit`:
```bash
if echo "$CHANGED_FILES" | grep -E "(src/|tests/|your-pattern)" > /dev/null; then
```

**GitHub Actions** (CI/CD):
Edit `.github/workflows/update-claude-md.yml`:
```yaml
paths:
  - 'src/**'
  - 'tests/**'  
  - 'your-new-pattern/**'
```

## Troubleshooting

### Common Issues

**1. Updater script fails:**
```bash
# Check dependencies
pip install toml

# Run with error output
python scripts/claude_md_updater.py --force
```

**2. Git hooks not triggering:**
```bash
# Check hook installation
./scripts/manage-git-hooks.sh status

# Reinstall hooks
./scripts/manage-git-hooks.sh install
```

**3. Duplicates in dependencies:**
- Edit `_extract_dependencies()` method to deduplicate
- Common cause: multiple similar dependency entries

**4. GitHub Actions workflow fails:**
```bash
# Check workflow logs in GitHub Actions tab
# Common cause: Missing toml dependency or permission issues
```

### Debug Mode

```bash
# Add debug output to updater script
python scripts/claude_md_updater.py --force 2>&1 | tee debug.log

# Check git hook execution
echo "Debug output" >> .git/hooks/post-commit
```

## Benefits

✅ **Always current**: CLAUDE.md stays synchronized with project state  
✅ **Multiple triggers**: Immediate (hooks), scheduled (Actions), and manual updates  
✅ **Low maintenance**: Template-based approach reduces manual editing  
✅ **Smart updates**: Only updates sections that actually changed  
✅ **Comprehensive**: Covers dependencies, architecture, commands, and status  
✅ **Transparent**: Clear commit messages and summaries of changes

## Maintenance

### Weekly Tasks
- Review GitHub Actions summary for update patterns
- Check for any failed automated updates

### Monthly Tasks  
- Review and update template content for static sections
- Verify automation is capturing new project developments
- Update hook triggers if project structure changes significantly

### As Needed
- Add new auto-generated sections for evolving project needs
- Customize commit analysis patterns for better theme detection
- Adjust update frequency based on development velocity

---

*This automation system ensures CLAUDE.md remains an accurate, up-to-date guide for Claude Code while minimizing manual maintenance overhead.*