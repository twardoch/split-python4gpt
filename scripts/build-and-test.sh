#!/bin/bash
# Comprehensive build and test script for split-python4gpt

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo_info "Starting build and test process..."
echo_info "Project root: $PROJECT_ROOT"

cd "$PROJECT_ROOT"

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo_error "Not in a git repository!"
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1-2)
if [[ "$python_version" != "3.10" ]]; then
    echo_warn "Python 3.10 is required, but found Python $python_version"
    echo_warn "Continuing anyway, but tests may fail"
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo_info "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo_info "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo_info "Upgrading pip..."
pip install --upgrade pip

# Install build dependencies
echo_info "Installing build dependencies..."
pip install -e ".[testing]"
pip install build twine setuptools_scm

# Get current version
echo_info "Getting current version..."
if [ -f "scripts/get_version.py" ]; then
    current_version=$(python scripts/get_version.py)
    echo_info "Current version: $current_version"
else
    echo_warn "Version script not found, using setuptools_scm directly"
    current_version=$(python -c "from setuptools_scm import get_version; print(get_version())")
    echo_info "Current version: $current_version"
fi

# Run linting if pre-commit is available
if command -v pre-commit &> /dev/null; then
    echo_info "Running pre-commit hooks..."
    pre-commit run --all-files || {
        echo_warn "Pre-commit checks failed, but continuing with tests"
    }
else
    echo_warn "pre-commit not available, skipping linting"
fi

# Run tests
echo_info "Running tests..."
pytest -v --tb=short

# Run performance tests if requested
if [[ "$1" == "--with-performance" ]]; then
    echo_info "Running performance tests..."
    pytest -v --tb=short -m performance
fi

# Run tests with coverage if requested
if [[ "$1" == "--with-coverage" ]]; then
    echo_info "Running tests with coverage..."
    pytest -v --tb=short --cov=split_python4gpt --cov-report=term-missing --cov-report=html
fi

# Build package
echo_info "Building package..."
python -m build

# Check the built package
echo_info "Checking built package..."
twine check dist/*

# List built files
echo_info "Built files:"
ls -la dist/

echo_info "Build and test completed successfully!"
echo_info "Package version: $current_version"
echo_info "Built files are in dist/"

# Optional: Install the built package in a new environment to test
if [[ "$1" == "--test-install" ]]; then
    echo_info "Testing installation of built package..."
    
    # Create a temporary environment
    temp_env=$(mktemp -d)
    python3 -m venv "$temp_env"
    source "$temp_env/bin/activate"
    
    # Install the built wheel
    pip install dist/*.whl
    
    # Test that it works
    python -c "import split_python4gpt; print('Import successful')"
    python -c "from split_python4gpt import __version__; print(f'Version: {__version__}')"
    
    # Test CLI
    mdsplit4gpt --help > /dev/null && echo_info "CLI test passed"
    
    # Cleanup
    deactivate
    rm -rf "$temp_env"
    
    echo_info "Installation test completed successfully!"
fi

echo_info "All checks passed! 🎉"