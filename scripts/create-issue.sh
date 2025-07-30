#!/bin/bash

# Script to create GitHub issues using gh CLI
# Usage: ./create-issue.sh [--file FILE]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}INFO:${NC} $1"
}

print_success() {
    echo -e "${GREEN}SUCCESS:${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}WARNING:${NC} $1"
}

print_error() {
    echo -e "${RED}ERROR:${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [--file FILE]"
    echo ""
    echo "Create a GitHub issue for this repository."
    echo ""
    echo "Options:"
    echo "  --file FILE    Read title and body from a file"
    echo "  -h, --help     Show this help message"
    echo ""
    echo "File format (if using --file):"
    echo "  First line: Issue title"
    echo "  Blank line"
    echo "  Remaining content: Issue body"
    echo ""
    echo "Examples:"
    echo "  $0                    # Interactive mode"
    echo "  $0 --file issue.txt   # Read from file"
}

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    print_error "GitHub CLI (gh) is not installed or not in PATH"
    print_info "Install with: https://cli.github.com/"
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "Not in a git repository"
    exit 1
fi

# Check if gh is authenticated
if ! gh auth status &> /dev/null; then
    print_error "GitHub CLI is not authenticated"
    print_info "Run: gh auth login"
    exit 1
fi

# Parse command line arguments
FILE=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --file)
            FILE="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Function to read from file
read_from_file() {
    local file="$1"
    
    if [[ ! -f "$file" ]]; then
        print_error "File not found: $file"
        exit 1
    fi
    
    # Read first line as title
    TITLE=$(head -n 1 "$file")
    
    # Read everything after the first blank line as body
    BODY=$(tail -n +3 "$file")
    
    if [[ -z "$TITLE" ]]; then
        print_error "File must contain a title on the first line"
        exit 1
    fi
    
    print_info "Title: $TITLE"
    print_info "Body preview: $(echo "$BODY" | head -c 100)..."
}

# Function to read interactively
read_interactive() {
    print_info "Creating a new GitHub issue"
    echo ""
    
    # Get title
    while true; do
        read -p "Enter issue title: " TITLE
        if [[ -n "$TITLE" ]]; then
            break
        fi
        print_warning "Title cannot be empty"
    done
    
    echo ""
    print_info "Enter issue body (press Ctrl+D when finished):"
    print_info "You can use Markdown formatting"
    echo ""
    
    # Read multiline body
    BODY=$(cat)
    
    echo ""
    print_info "Title: $TITLE"
    print_info "Body preview: $(echo "$BODY" | head -c 100)..."
}

# Main logic
if [[ -n "$FILE" ]]; then
    read_from_file "$FILE"
else
    read_interactive
fi

# Confirm creation
echo ""
read -p "Create this issue? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Issue creation cancelled"
    exit 0
fi

# Create the issue
print_info "Creating issue..."

if [[ -n "$BODY" ]]; then
    ISSUE_URL=$(gh issue create --title "$TITLE" --body "$BODY")
else
    ISSUE_URL=$(gh issue create --title "$TITLE")
fi

if [[ $? -eq 0 ]]; then
    print_success "Issue created successfully!"
    print_info "URL: $ISSUE_URL"
else
    print_error "Failed to create issue"
    exit 1
fi