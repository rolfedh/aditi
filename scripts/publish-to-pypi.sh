#!/bin/bash
# Script to publish Aditi to PyPI

set -e

echo "🚀 Preparing to publish Aditi to PyPI..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found. Are you in the project root?"
    exit 1
fi

# Clean up previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ src/*.egg-info

# Run tests first (optional)
if [[ "$1" != "--skip-tests" ]]; then
    echo "🧪 Running tests..."
    python -m pytest tests/ -v || {
        echo "⚠️  Some tests failed. Continue anyway? [y/N]"
        read -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "❌ Aborted due to test failures"
            exit 1
        fi
    }
else
    echo "⚠️  Skipping tests (--skip-tests flag used)"
fi

# Check code quality (optional)
echo "🔍 Running code quality checks..."
if command -v ruff &> /dev/null || python -m ruff --version &> /dev/null 2>&1; then
    python -m ruff check . || echo "⚠️  Ruff check failed, continuing..."
else
    echo "⚠️  Ruff not installed, skipping..."
fi

if command -v mypy &> /dev/null || python -m mypy --version &> /dev/null 2>&1; then
    python -m mypy src/aditi || echo "⚠️  MyPy check failed, continuing..."
else
    echo "⚠️  MyPy not installed, skipping..."
fi

# Build the package
echo "📦 Building package..."
python -m build

# Show what will be uploaded
echo "📋 Package contents:"
ls -la dist/

# Ask for confirmation
echo ""
echo "⚠️  Ready to upload to PyPI"
echo "Make sure you have:"
echo "  1. Created a PyPI account at https://pypi.org"
echo "  2. Generated an API token at https://pypi.org/manage/account/token/"
echo "  3. Created ~/.pypirc with your token (see .pypirc.template)"
echo ""
read -p "Do you want to upload to TestPyPI first? (recommended) [y/N] " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📤 Uploading to TestPyPI..."
    python -m twine upload --repository testpypi dist/*
    echo ""
    echo "✅ Uploaded to TestPyPI!"
    echo "Test installation with: pip install -i https://test.pypi.org/simple/ aditi"
    echo ""
    read -p "Continue to upload to PyPI? [y/N] " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Cancelled PyPI upload"
        exit 0
    fi
fi

echo "📤 Uploading to PyPI..."
python -m twine upload dist/*

echo ""
echo "🎉 Success! Aditi has been published to PyPI!"
echo "Install with: pip install aditi"
echo ""
echo "Don't forget to:"
echo "  1. Create a GitHub release with tag v$(python -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])')"
echo "  2. Update the version number in pyproject.toml for the next release"