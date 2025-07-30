Output demo-01-getting-started.gif

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
Type "echo 'Getting Started - Essential First Steps'"
Enter
Sleep 2s

# Navigate to test repository
Type "# Always start by navigating to your repository root"
Enter
Type "cd test-repo"
Enter
Sleep 1s

# Show version
Type "# Check the installed version"
Enter
Type "aditi --version"
Enter
Sleep 2s

# Show help
Type "# View available commands and options"
Enter
Type "aditi --help"
Enter
Sleep 3s

# Initialize Vale configuration
Type "# REQUIRED: Initialize Vale configuration (run this once per repo)"
Enter
Type "# Note: Any existing .vale.ini files will be backed up"
Enter
Type "aditi init"
Enter
Sleep 5s

Type "# Setup complete! You're ready to use Aditi."
Enter
Sleep 2s