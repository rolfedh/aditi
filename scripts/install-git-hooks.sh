#!/bin/bash
# Install git hooks for CLAUDE.md automation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HOOKS_DIR="$PROJECT_ROOT/.git/hooks"

echo "🔧 Installing git hooks for CLAUDE.md automation..."

# Check if we're in a git repository
if [ ! -d "$PROJECT_ROOT/.git" ]; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Create hooks directory if it doesn't exist
mkdir -p "$HOOKS_DIR"

# Install post-commit hook
cat > "$HOOKS_DIR/post-commit" << 'EOF'
#!/bin/bash
# Auto-update CLAUDE.md on significant commits

PROJECT_ROOT="$(git rev-parse --show-toplevel)"
UPDATER_SCRIPT="$PROJECT_ROOT/scripts/claude_md_updater.py"

# Check if the updater script exists
if [ ! -f "$UPDATER_SCRIPT" ]; then
    echo "⚠️  CLAUDE.md updater script not found, skipping auto-update"
    exit 0
fi

# Check if this commit affects files that should trigger CLAUDE.md update
CHANGED_FILES=$(git diff HEAD~1 --name-only 2>/dev/null || echo "")

if echo "$CHANGED_FILES" | grep -E "(src/|tests/|pyproject\.toml|\.github/workflows/)" > /dev/null; then
    echo "🔄 Detected changes affecting CLAUDE.md, running updater..."
    
    # Run the updater
    cd "$PROJECT_ROOT"
    if python "$UPDATER_SCRIPT" 2>/dev/null; then
        # Check if CLAUDE.md was actually modified
        if ! git diff --quiet CLAUDE.md; then
            echo "📝 CLAUDE.md updated based on recent changes"
            git add CLAUDE.md
            
            # Amend the commit to include CLAUDE.md changes
            git commit --amend --no-edit --no-verify
            echo "✅ CLAUDE.md changes included in commit"
        else
            echo "✅ CLAUDE.md already current"
        fi
    else
        echo "⚠️  CLAUDE.md updater failed, continuing without update"
    fi
else
    echo "ℹ️  No significant changes detected, skipping CLAUDE.md update"
fi
EOF

# Make the hook executable
chmod +x "$HOOKS_DIR/post-commit"

# Install pre-push hook for validation
cat > "$HOOKS_DIR/pre-push" << 'EOF'
#!/bin/bash
# Validate CLAUDE.md before pushing

PROJECT_ROOT="$(git rev-parse --show-toplevel)"
UPDATER_SCRIPT="$PROJECT_ROOT/scripts/claude_md_updater.py"

# Check if CLAUDE.md is in sync with project state
if [ -f "$UPDATER_SCRIPT" ]; then
    echo "🔍 Validating CLAUDE.md sync status..."
    
    cd "$PROJECT_ROOT"
    
    # Run updater in dry-run mode (if it supported it)
    # For now, just run it and check if changes are needed
    cp CLAUDE.md CLAUDE.md.backup 2>/dev/null || true
    
    if python "$UPDATER_SCRIPT" 2>/dev/null; then
        if ! git diff --quiet CLAUDE.md; then
            echo "⚠️  CLAUDE.md is out of sync with project state"
            echo "📝 Auto-updating CLAUDE.md before push..."
            
            git add CLAUDE.md
            git commit -m "docs: Sync CLAUDE.md with project state before push

🤖 Auto-generated update via pre-push hook

Co-Authored-By: Git Hook <noreply@github.com>"
            echo "✅ CLAUDE.md synchronized and committed"
        else
            echo "✅ CLAUDE.md is current"
        fi
    else
        echo "⚠️  Could not validate CLAUDE.md sync status"
        # Restore backup if update failed
        if [ -f CLAUDE.md.backup ]; then
            mv CLAUDE.md.backup CLAUDE.md
        fi
    fi
    
    # Clean up backup
    rm -f CLAUDE.md.backup
fi
EOF

# Make the hook executable
chmod +x "$HOOKS_DIR/pre-push"

# Create a convenience script for manual hook management
cat > "$SCRIPT_DIR/manage-git-hooks.sh" << 'EOF'
#!/bin/bash
# Manage git hooks for CLAUDE.md automation

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HOOKS_DIR="$PROJECT_ROOT/.git/hooks"

case "${1:-help}" in
    install)
        echo "🔧 (Re)installing git hooks..."
        "$SCRIPT_DIR/install-git-hooks.sh"
        ;;
    
    remove)
        echo "🗑️  Removing CLAUDE.md git hooks..."
        rm -f "$HOOKS_DIR/post-commit"
        rm -f "$HOOKS_DIR/pre-push"
        echo "✅ Git hooks removed"
        ;;
    
    status)
        echo "📊 Git hooks status:"
        if [ -f "$HOOKS_DIR/post-commit" ]; then
            echo "  ✅ post-commit hook installed"
        else
            echo "  ❌ post-commit hook not found"
        fi
        
        if [ -f "$HOOKS_DIR/pre-push" ]; then
            echo "  ✅ pre-push hook installed"
        else
            echo "  ❌ pre-push hook not found"
        fi
        ;;
    
    test)
        echo "🧪 Testing CLAUDE.md updater..."
        python "$PROJECT_ROOT/scripts/claude_md_updater.py" --dry-run || echo "⚠️  Dry-run not supported yet"
        ;;
    
    help|*)
        echo "Usage: $0 {install|remove|status|test}"
        echo ""
        echo "Commands:"
        echo "  install  - Install or reinstall git hooks"
        echo "  remove   - Remove all CLAUDE.md git hooks"  
        echo "  status   - Show current hook installation status"
        echo "  test     - Test the CLAUDE.md updater script"
        ;;
esac
EOF

chmod +x "$SCRIPT_DIR/manage-git-hooks.sh"

echo "✅ Git hooks installed successfully!"
echo ""
echo "Installed hooks:"
echo "  📝 post-commit: Auto-updates CLAUDE.md after significant commits"
echo "  🔍 pre-push: Validates CLAUDE.md sync before pushing"
echo ""
echo "Hook management:"
echo "  ./scripts/manage-git-hooks.sh status   - Check hook status"
echo "  ./scripts/manage-git-hooks.sh remove   - Remove hooks"
echo "  ./scripts/manage-git-hooks.sh install  - Reinstall hooks"
echo ""
echo "Note: Hooks only trigger on commits affecting src/, tests/, pyproject.toml, or .github/workflows/"