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
