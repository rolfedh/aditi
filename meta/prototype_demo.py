#!/usr/bin/env python3
"""Standalone Aditi CLI prototype - no dependencies required"""

import sys
import argparse
from datetime import datetime

# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'

def print_header():
    """Print the styled header for help"""
    print(f"\n{Colors.BOLD}{Colors.YELLOW}IMPORTANT:{Colors.RESET}")
    print("- cd to the root directory of your repository before running aditi commands.")
    print("- Create a working branch with the latest changes in it.\n")
    print(f" Usage: aditi [OPTION]|| [COMMAND]\n")
    print(f" AsciiDoc DITA Integration - Prepare AsciiDoc files for migration to DITA\n")

def print_options():
    """Print options table"""
    print("╭─ Options ────────────────────────────────────────────────────────────────────╮")
    print("│ --version             -V        Show version and exit                        │")
    print("│ --help                          Show this message and exit.                  │")
    print("╰──────────────────────────────────────────────────────────────────────────────╯")

def print_commands():
    """Print commands table"""
    print("╭─ Commands ───────────────────────────────────────────────────────────────────╮")
    print("│ init      Initialize Vale configuration for AsciiDocDITA rules.              │")
    print("│ journey   Start an interactive journey to migrate AsciiDoc files to DITA.    │")
    print("│ check     Check AsciiDoc files for DITA compatibility issues.                │")
    print("│ fix       Fix deterministic DITA compatibility issues in AsciiDoc files.     │")
    print("╰──────────────────────────────────────────────────────────────────────────────╯")

def cmd_init():
    """Initialize Vale configuration"""
    print(f"\n{Colors.BOLD}{Colors.GREEN}Initializing Vale configuration...{Colors.RESET}\n")
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    print(f"[17:21:26] INFO     Existing .vale.ini backed up to .vale.ini.backup.{timestamp}")
    print("           INFO     Created Vale configuration at .vale.ini")
    print("           INFO     Downloading AsciiDocDITA styles...")
    print("[17:21:27] INFO     Successfully downloaded AsciiDocDITA v0.2.0")
    print("           INFO     Vale configuration initialized successfully\n")
    
    print(f"{Colors.GREEN}✓{Colors.RESET} Vale initialized with AsciiDocDITA rules")
    print("\nNext steps:")
    print(f"  • Run {Colors.BOLD}aditi journey{Colors.RESET} to start an interactive migration journey")
    print(f"  • Run {Colors.BOLD}aditi check{Colors.RESET} to check files for DITA compatibility issues")

def cmd_journey():
    """Start interactive journey"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}Welcome to the Aditi Migration Journey!{Colors.RESET}\n")
    
    print("Checking Vale configuration... ", end="", flush=True)
    print(f"{Colors.GREEN}✓ Found{Colors.RESET}\n")
    
    print("📁 Repository: /home/sarah/docs/product-docs")
    print("🌿 Current branch: feature/dita-migration")
    print("📄 AsciiDoc files found: 52\n")
    
    print(f"{Colors.BOLD}Ready to start?{Colors.RESET} This journey will:")
    print("  1. Run prerequisite checks (ContentType)")
    print("  2. Check and fix Error-level issues")
    print("  3. Check and fix Warning-level issues")
    print("  4. Check and fix Suggestion-level issues")
    print("  5. Create a pull request with all changes\n")
    
    print(f"{Colors.DIM}Press Enter to continue or Ctrl+C to exit{Colors.RESET}")

def cmd_check(args):
    """Check for issues"""
    path = args.path if hasattr(args, 'path') and args.path else "."
    
    print(f"\n{Colors.BOLD}Checking AsciiDoc files in:{Colors.RESET} {path}")
    
    if hasattr(args, 'rule') and args.rule:
        print(f"{Colors.BOLD}Rule:{Colors.RESET} {args.rule}\n")
    else:
        print(f"{Colors.BOLD}Rules:{Colors.RESET} All AsciiDocDITA rules\n")
    
    print("Running Vale with AsciiDocDITA rules...")
    print(f"\n{Colors.YELLOW}⚠{Colors.RESET}  assemblies/assembly_configuring.adoc")
    print(f"   16:1  {Colors.RED}error{Colors.RESET}    Missing content type attribute    AsciiDocDITA.ContentType")
    print(f"\n{Colors.YELLOW}⚠{Colors.RESET}  modules/proc_installing.adoc")
    print(f"   1:1   {Colors.RED}error{Colors.RESET}    Missing content type attribute    AsciiDocDITA.ContentType")
    print(f"\n{Colors.GREEN}✓{Colors.RESET}  modules/con_prerequisites.adoc")
    print(f"\n{Colors.BOLD}Summary:{Colors.RESET} 2 errors, 0 warnings in 3 files")

def cmd_fix(args):
    """Fix issues"""
    path = args.path if hasattr(args, 'path') and args.path else "."
    
    print(f"\n{Colors.BOLD}Fixing deterministic issues in:{Colors.RESET} {path}")
    
    if hasattr(args, 'rule') and args.rule:
        print(f"{Colors.BOLD}Rule:{Colors.RESET} {args.rule}")
    else:
        print(f"{Colors.BOLD}Rules:{Colors.RESET} All deterministic AsciiDocDITA rules")
    
    if hasattr(args, 'dry_run') and args.dry_run:
        print(f"{Colors.YELLOW}Mode: DRY RUN (no changes will be made){Colors.RESET}\n")
    else:
        print("\n")
    
    print("Scanning for deterministic fixes...")
    print(f"\n{Colors.BOLD}EntityReference{Colors.RESET} (Fully deterministic)")
    print(f"  {Colors.GREEN}✓{Colors.RESET} modules/ref_api.adoc: Replaced &rarr; with →")
    print(f"  {Colors.GREEN}✓{Colors.RESET} modules/ref_api.adoc: Replaced &nbsp; with &#160;")
    print(f"\n{Colors.BOLD}ContentType{Colors.RESET} (Partially deterministic)")
    print(f"  {Colors.YELLOW}!{Colors.RESET} assemblies/assembly_configuring.adoc: Added placeholder")
    print(f"     {Colors.DIM}// TODO: Review and set content type to one of:{Colors.RESET}")
    print(f"     {Colors.DIM}// ASSEMBLY, CONCEPT, PROCEDURE, REFERENCE, SNIPPET{Colors.RESET}")
    print(f"     {Colors.DIM}:_mod-docs-content-type: <PLACEHOLDER>{Colors.RESET}")
    
    if not (hasattr(args, 'dry_run') and args.dry_run):
        print(f"\n{Colors.BOLD}{Colors.GREEN}✓{Colors.RESET} Fixed 3 issues in 2 files")
        print(f"\nRun {Colors.BOLD}git diff{Colors.RESET} to review changes")

def main():
    if len(sys.argv) == 1:
        print_header()
        print_options()
        print_commands()
        return
    
    # Handle version
    if '--version' in sys.argv or '-V' in sys.argv:
        print("aditi version 0.1.0")
        return
    
    # Handle help
    if '--help' in sys.argv or '-h' in sys.argv:
        print_header()
        print_options()
        print_commands()
        return
    
    # Handle commands
    command = sys.argv[1]
    
    if command == 'init':
        cmd_init()
    elif command == 'journey':
        cmd_journey()
    elif command == 'check':
        # Simple argument parsing for check
        class Args:
            path = sys.argv[2] if len(sys.argv) > 2 else None
            rule = None
        cmd_check(Args())
    elif command == 'fix':
        # Simple argument parsing for fix
        class Args:
            path = sys.argv[2] if len(sys.argv) > 2 else None
            rule = None
            dry_run = '--dry-run' in sys.argv
        cmd_fix(Args())
    else:
        print(f"Error: Unknown command '{command}'")
        print_header()
        print_options()
        print_commands()

if __name__ == "__main__":
    main()