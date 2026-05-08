# Build using uv (alternative to shell script)
# Usage: uv run build.py [--publish] [--test-pypi]

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_uv():
    """Check if uv is installed."""
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True, check=True)
        print(f"✓ uv found: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: uv is not installed.")
        print("Please install it with: pip install uv")
        print("Or: curl -LsSf https://astral.sh/uv/install.sh | sh")
        return False


def clean_builds():
    """Clean previous builds."""
    print("Cleaning previous builds...")
    dirs_to_clean = ["dist", "build"]
    patterns_to_clean = ["*.egg-info", "mvvm_framework/*.egg-info"]
    
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.rmtree(dir_path)
    
    for pattern in patterns_to_clean:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
    
    print("✓ Clean complete")


def install_build_deps():
    """Install build dependencies."""
    print("Installing build dependencies...")
    subprocess.run([sys.executable, "-m", "uv", "pip", "install", "hatchling"], check=True, capture_output=True)
    print("✓ Build dependencies installed")


def build_package():
    """Build the package."""
    print("Building package...")
    subprocess.run([sys.executable, "-m", "uv", "build"], check=True)
    print("✓ Build complete")
    
    # Show built files
    print("\nBuilt files:")
    dist_path = Path("dist")
    if dist_path.exists():
        for file in sorted(dist_path.iterdir()):
            size_mb = file.stat().st_size / (1024 * 1024)
            print(f"  {file.name} ({size_mb:.2f} MB)")


def publish_package(test_pypi=False):
    """Publish the package."""
    if test_pypi:
        print("Publishing to TestPyPI...")
        subprocess.run([sys.executable, "-m", "uv", "publish", "--repository", "testpypi"], check=True)
        print("✓ Published to TestPyPI")
    else:
        print("Publishing to PyPI...")
        subprocess.run([sys.executable, "-m", "uv", "publish"], check=True)
        print("✓ Published to PyPI")


def main():
    print("=== PySide6 MVVM Framework - Build & Publish ===\n")
    
    if not check_uv():
        sys.exit(1)
    
    print()
    clean_builds()
    print()
    install_build_deps()
    print()
    build_package()
    print()
    
    # Check for publish flag
    if "--publish" in sys.argv or "-p" in sys.argv:
        # Check for environment variables
        if not os.environ.get("PYPI_TOKEN") and not os.environ.get("TWINE_USERNAME"):
            print("Warning: PYPI_TOKEN or TWINE_USERNAME not set.")
            print("Please set one of these environment variables to publish.\n")
            print("For PyPI:")
            print("  export PYPI_TOKEN='your-pypi-token'\n")
            print("For TestPyPI:")
            print("  export PYPI_TOKEN='your-testpypi-token'")
            print("  Then run with --test-pypi flag\n")
            sys.exit(1)
        
        test_pypi = "--test-pypi" in sys.argv or "-t" in sys.argv
        publish_package(test_pypi=test_pypi)
    else:
        print("Build complete! To publish, run:")
        print("  python build.py --publish\n")
        print("To publish to TestPyPI first:")
        print("  python build.py --publish --test-pypi\n")
        print("Make sure to set PYPI_TOKEN environment variable before publishing.")


if __name__ == "__main__":
    main()
