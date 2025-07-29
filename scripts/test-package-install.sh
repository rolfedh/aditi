#!/bin/bash
# Test installing the package locally

set -e

echo "🧪 Testing local package installation..."

# Create a temporary virtual environment
TEMP_DIR=$(mktemp -d)
echo "📁 Creating temporary environment in $TEMP_DIR"

# Create venv
python3 -m venv "$TEMP_DIR/venv"

# Activate venv and install
source "$TEMP_DIR/venv/bin/activate"

echo "📦 Installing aditi from dist/"
pip install dist/aditi-0.1.0-py3-none-any.whl

echo "✅ Testing installation..."
aditi --version
aditi --help

echo "🧹 Cleaning up..."
deactivate
rm -rf "$TEMP_DIR"

echo "✅ Package installation test successful!"