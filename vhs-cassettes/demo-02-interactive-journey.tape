Output demo-02-interactive-journey.gif

Set FontSize 18
Set Width 1200
Set Height 800
Set Theme "Catppuccin Frappe"

# Welcome screen
Type "clear"
Enter
Sleep 1s

Type "echo 'Aditi (AsciiDoc DITA Toolkit)'"
Enter
Type "echo 'Interactive Journey - Guided DITA Migration Workflow'"
Enter
Sleep 2s

# Navigate to test repository
Type "cd test-repo"
Enter
Sleep 1s

# Start interactive journey
Type "aditi journey"
Enter
Sleep 3s

# Accept repository root (default)
Sleep 5s
Enter
Sleep 3s

# Accept subdirectory permissions (default: allow all)
Sleep 5s
Enter
Sleep 3s

# Accept branch name (default: feature/dita-migration)
Sleep 5s
Enter
Sleep 3s

# Wait for rule processing and ExampleBlock fixes
Sleep 8s

# Decline to continue after ExampleBlock changes
Sleep 5s
Type "n"
Enter
Sleep 2s

Type "# Journey paused - you can resume anytime with 'aditi journey --resume'"
Enter
Sleep 2s