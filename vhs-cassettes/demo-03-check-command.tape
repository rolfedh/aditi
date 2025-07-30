Output demo-03-check-command.gif

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
Type "echo 'Check Command - Analyze DITA Compatibility Issues'"
Enter
Sleep 2s

# Navigate to test repository
Type "cd test-repo"
Enter
Sleep 1s

# Run check command
Type "# Analyze all AsciiDoc files for DITA compatibility"
Enter
Type "aditi check"
Enter
Sleep 5s

# Show summary and violations
Sleep 3s

Type "# Check command identifies violations by rule and provides fix guidance"
Enter
Sleep 2s