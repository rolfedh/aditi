Output demo-04-fix-command.gif

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
Type "echo 'Fix Command - Automatically Repair Deterministic Issues'"
Enter
Sleep 2s

# Navigate to test repository
Type "cd test-repo"
Enter
Sleep 1s

# Fix specific rule
Type "# Fix deterministic violations for a specific rule"
Enter
Type "aditi fix --rule EntityReference"
Enter
Sleep 4s

# Show before/after comparison
Sleep 2s

Type "# Fix command applies automatic corrections where possible"
Enter
Type "# Non-deterministic issues require manual review"
Enter
Sleep 2s