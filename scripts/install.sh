#!/bin/bash
# Installation script for split-python4gpt
# This script provides easy installation options for end users

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

echo_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Default values
INSTALL_METHOD="auto"
INSTALL_DIR="$HOME/.local/bin"
GITHUB_REPO="twardoch/split-python4gpt"

show_help() {
    echo "Split-Python4GPT Installation Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo "  -m, --method METHOD Installation method (auto|pip|binary)"
    echo "  -d, --dir DIR       Installation directory for binary (default: ~/.local/bin)"
    echo "  -v, --version VER   Specific version to install (default: latest)"
    echo ""
    echo "Installation methods:"
    echo "  auto    - Automatically choose the best method"
    echo "  pip     - Install using pip from PyPI"
    echo "  binary  - Download and install binary from GitHub releases"
    echo ""
    echo "Examples:"
    echo "  $0                           # Auto-detect best installation method"
    echo "  $0 -m pip                    # Force pip installation"
    echo "  $0 -m binary -d ~/bin        # Install binary to ~/bin"
    echo "  $0 -v 1.2.3                 # Install specific version"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -m|--method)
            INSTALL_METHOD="$2"
            shift 2
            ;;
        -d|--dir)
            INSTALL_DIR="$2"
            shift 2
            ;;
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        *)
            echo_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect OS
detect_os() {
    case "$(uname -s)" in
        Linux*)     echo "linux";;
        Darwin*)    echo "macos";;
        CYGWIN*|MINGW*|MSYS*) echo "windows";;
        *)          echo "unknown";;
    esac
}

# Function to get latest version from GitHub
get_latest_version() {
    if command_exists curl; then
        curl -s "https://api.github.com/repos/$GITHUB_REPO/releases/latest" | \
            grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/' | sed 's/^v//'
    elif command_exists wget; then
        wget -qO- "https://api.github.com/repos/$GITHUB_REPO/releases/latest" | \
            grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/' | sed 's/^v//'
    else
        echo_error "curl or wget is required to fetch latest version"
        exit 1
    fi
}

# Function to install via pip
install_via_pip() {
    local version_spec=""
    if [[ -n "$VERSION" ]]; then
        version_spec="==$VERSION"
    fi
    
    echo_step "Installing split-python4gpt via pip..."
    
    if command_exists pip; then
        pip install "split-python4gpt$version_spec"
    elif command_exists pip3; then
        pip3 install "split-python4gpt$version_spec"
    else
        echo_error "pip is not available. Please install Python and pip first."
        exit 1
    fi
    
    echo_info "Testing installation..."
    if command_exists mdsplit4gpt; then
        mdsplit4gpt --help > /dev/null
        echo_info "✅ Installation successful!"
        echo_info "You can now use: mdsplit4gpt --help"
    else
        echo_warn "Installation completed but mdsplit4gpt is not in PATH"
        echo_warn "You may need to add ~/.local/bin to your PATH"
    fi
}

# Function to install binary
install_binary() {
    local os=$(detect_os)
    local arch="x86_64"
    
    if [[ "$os" == "unknown" ]]; then
        echo_error "Unsupported operating system"
        exit 1
    fi
    
    # Get version
    local install_version="$VERSION"
    if [[ -z "$install_version" ]]; then
        echo_step "Fetching latest version..."
        install_version=$(get_latest_version)
    fi
    
    if [[ -z "$install_version" ]]; then
        echo_error "Could not determine version to install"
        exit 1
    fi
    
    echo_step "Installing split-python4gpt v$install_version binary for $os-$arch..."
    
    # Determine binary name
    local binary_name="mdsplit4gpt-$os-$arch"
    if [[ "$os" == "windows" ]]; then
        binary_name="mdsplit4gpt-$os-$arch.exe"
    fi
    
    # Download URL
    local download_url="https://github.com/$GITHUB_REPO/releases/download/v$install_version/$binary_name"
    
    echo_step "Downloading from: $download_url"
    
    # Create installation directory
    mkdir -p "$INSTALL_DIR"
    
    # Download binary
    local temp_file=$(mktemp)
    if command_exists curl; then
        curl -L -o "$temp_file" "$download_url"
    elif command_exists wget; then
        wget -O "$temp_file" "$download_url"
    else
        echo_error "curl or wget is required to download binary"
        exit 1
    fi
    
    # Install binary
    local target_name="mdsplit4gpt"
    if [[ "$os" == "windows" ]]; then
        target_name="mdsplit4gpt.exe"
    fi
    
    local target_path="$INSTALL_DIR/$target_name"
    mv "$temp_file" "$target_path"
    chmod +x "$target_path"
    
    echo_info "Binary installed to: $target_path"
    
    # Test installation
    echo_step "Testing installation..."
    if "$target_path" --help > /dev/null 2>&1; then
        echo_info "✅ Installation successful!"
        echo_info "You can now use: $target_path --help"
        
        # Check if it's in PATH
        if command_exists "$target_name"; then
            echo_info "✅ Binary is available in PATH as: $target_name"
        else
            echo_warn "Binary is not in PATH. Add $INSTALL_DIR to your PATH to use '$target_name' directly."
            echo_warn "Or use the full path: $target_path"
        fi
    else
        echo_error "Installation failed - binary test failed"
        exit 1
    fi
}

# Function to auto-detect best installation method
auto_detect_method() {
    if command_exists python3 && (command_exists pip || command_exists pip3); then
        echo_info "Python and pip detected - using pip installation"
        install_via_pip
    else
        echo_info "Python/pip not available - using binary installation"
        install_binary
    fi
}

# Main installation logic
echo_info "Split-Python4GPT Installation Script"
echo_info "======================================"

case "$INSTALL_METHOD" in
    auto)
        auto_detect_method
        ;;
    pip)
        install_via_pip
        ;;
    binary)
        install_binary
        ;;
    *)
        echo_error "Invalid installation method: $INSTALL_METHOD"
        echo_error "Valid methods: auto, pip, binary"
        exit 1
        ;;
esac

echo_info ""
echo_info "Installation completed! 🎉"
echo_info ""
echo_info "Next steps:"
echo_info "1. Run 'mdsplit4gpt --help' to see usage information"
echo_info "2. Try: mdsplit4gpt your_script.py --out output_dir"
echo_info "3. Visit https://github.com/$GITHUB_REPO for documentation"