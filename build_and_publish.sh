#!/bin/bash
# Build and publish script for PySide6 MVVM Framework using uv

set -e

echo "=== PySide6 MVVM Framework - Build & Publish Script ==="
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed."
    echo "Please install it with: pip install uv"
    echo "Or: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✓ uv found: $(uv --version)"
echo ""

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info mvvm_framework/*.egg-info
echo "✓ Clean complete"
echo ""

# Install build dependencies
echo "Installing build dependencies..."
uv pip install --system hatchling >/dev/null 2>&1 || uv pip install hatchling
echo "✓ Build dependencies installed"
echo ""

# Build the package
echo "Building package..."
uv build
echo "✓ Build complete"
echo ""

# Show built files
echo "Built files:"
ls -lh dist/
echo ""

# Ask user if they want to publish
if [ "$1" == "--publish" ] || [ "$1" == "-p" ]; then
    echo "Publishing to PyPI..."
    
    # Check if TWINE_USERNAME or PYPI_TOKEN is set
    if [ -z "$PYPI_TOKEN" ] && [ -z "$TWINE_USERNAME" ]; then
        echo "Warning: PYPI_TOKEN or TWINE_USERNAME not set."
        echo "Please set one of these environment variables to publish."
        echo ""
        echo "For PyPI:"
        echo "  export PYPI_TOKEN='your-pypi-token'"
        echo ""
        echo "For TestPyPI:"
        echo "  export PYPI_TOKEN='your-testpypi-token'"
        echo "  Then run with --test-pypi flag"
        exit 1
    fi
    
    if [ "$2" == "--test-pypi" ] || [ "$2" == "-t" ]; then
        echo "Publishing to TestPyPI..."
        uv publish --repository testpypi
        echo "✓ Published to TestPyPI"
    else
        echo "Publishing to PyPI..."
        uv publish
        echo "✓ Published to PyPI"
    fi
else
    echo "Build complete! To publish, run:"
    echo "  ./build_and_publish.sh --publish"
    echo ""
    echo "To publish to TestPyPI first:"
    echo "  ./build_and_publish.sh --publish --test-pypi"
    echo ""
    echo "Make sure to set PYPI_TOKEN environment variable before publishing."
fi
