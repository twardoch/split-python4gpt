#!/bin/bash
# Development environment setup script for split-python4gpt

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

echo_info "Setting up development environment for split-python4gpt..."
echo_info "Project root: $PROJECT_ROOT"

cd "$PROJECT_ROOT"

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1-2)
if [[ "$python_version" != "3.10" ]]; then
    echo_warn "Python 3.10 is required, but found Python $python_version"
    echo_warn "Please install Python 3.10 and try again"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo_info "Creating virtual environment..."
    python3 -m venv .venv
else
    echo_info "Virtual environment already exists"
fi

# Activate virtual environment
echo_info "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo_info "Upgrading pip..."
pip install --upgrade pip

# Install the package in development mode
echo_info "Installing package in development mode..."
pip install -e ".[testing]"

# Install additional development tools
echo_info "Installing development tools..."
pip install \
    pre-commit \
    black \
    isort \
    flake8 \
    mypy \
    build \
    twine \
    setuptools_scm \
    psutil

# Install pre-commit hooks
echo_info "Installing pre-commit hooks..."
pre-commit install

echo_info "Running pre-commit on all files to ensure setup is correct..."
pre-commit run --all-files || {
    echo_warn "Pre-commit checks failed, but that's okay for initial setup"
}

# Test that the package works
echo_info "Testing package installation..."
python -c "import split_python4gpt; print('✓ Package import successful')"

# Test CLI
echo_info "Testing CLI..."
mdsplit4gpt --help > /dev/null && echo_info "✓ CLI test passed"

# Test version
echo_info "Testing version extraction..."
if [ -f "scripts/get_version.py" ]; then
    version=$(python scripts/get_version.py)
    echo_info "✓ Current version: $version"
else
    echo_warn "Version script not found"
fi

# Run a quick test
echo_info "Running quick test..."
python -m pytest tests/test_version.py -v

echo_info "Development environment setup completed successfully! 🎉"
echo_info ""
echo_info "To activate the environment in the future, run:"
echo_info "  source .venv/bin/activate"
echo_info ""
echo_info "Available development scripts:"
echo_info "  ./scripts/build-and-test.sh     - Run full build and test"
echo_info "  ./scripts/release.sh <version>  - Create a new release"
echo_info "  ./scripts/get_version.py        - Get current version"
echo_info ""
echo_info "To run tests:"
echo_info "  pytest                          - Run all tests"
echo_info "  pytest -m performance          - Run performance tests"
echo_info "  pytest --cov=split_python4gpt  - Run with coverage"
echo_info ""
echo_info "To run linting:"
echo_info "  pre-commit run --all-files      - Run all pre-commit hooks"
echo_info "  black .                         - Format code"
echo_info "  isort .                         - Sort imports"
echo_info "  flake8                          - Check code style"