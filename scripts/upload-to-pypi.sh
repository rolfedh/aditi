#!/bin/bash
# Simple script to upload to PyPI

set -e

echo "📦 Uploading Aditi to PyPI..."

# Check for dist files
if [ ! -d "dist" ] || [ -z "$(ls -A dist)" ]; then
    echo "❌ No dist files found. Run 'python -m build' first."
    exit 1
fi

echo "📋 Files to upload:"
ls -la dist/

# Install twine if not available
if ! command -v twine &> /dev/null && ! python -m twine --version &> /dev/null 2>&1; then
    echo "📥 Installing twine..."
    # Try pipx first
    if command -v pipx &> /dev/null; then
        pipx install twine
    else
        echo "⚠️  Twine not found. Please install it with one of:"
        echo "    pipx install twine"
        echo "    python -m pip install --user twine"
        echo "    apt install twine"
        exit 1
    fi
fi

# Upload to PyPI
echo ""
echo "⚠️  About to upload to PyPI"
echo "Make sure you have ~/.pypirc configured with your API token"
echo ""
read -p "Upload to TestPyPI first? (recommended) [y/N] " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📤 Uploading to TestPyPI..."
    if command -v twine &> /dev/null; then
        twine upload --repository testpypi dist/*
    else
        python -m twine upload --repository testpypi dist/*
    fi
    echo "✅ Uploaded to TestPyPI!"
    echo "Test with: pip install -i https://test.pypi.org/simple/ aditi"
    echo ""
    read -p "Continue to PyPI? [y/N] " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

echo "📤 Uploading to PyPI..."
if command -v twine &> /dev/null; then
    twine upload dist/*
else
    python -m twine upload dist/*
fi

echo "🎉 Successfully uploaded to PyPI!"
echo "Upgrade with: pip install --upgrade aditi"