#!/bin/bash
# Release script for split-python4gpt

set -e  # Exit on any error

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

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo_error "Not in a git repository!"
    exit 1
fi

# Check if working directory is clean
if ! git diff-index --quiet HEAD --; then
    echo_error "Working directory is not clean. Please commit or stash changes."
    exit 1
fi

# Check if we're on the main branch
current_branch=$(git rev-parse --abbrev-ref HEAD)
if [[ "$current_branch" != "main" ]]; then
    echo_warn "Current branch is '$current_branch', not 'main'"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get the version to release
if [ -z "$1" ]; then
    echo_error "Usage: $0 <version>"
    echo_error "Example: $0 1.2.3"
    exit 1
fi

VERSION="$1"

# Validate version format using validation script
echo_step "Validating version format..."
if ! "$SCRIPT_DIR/validate_tag.py" "$VERSION"; then
    echo_error "Version validation failed"
    exit 1
fi

echo_step "Preparing release for version $VERSION"

# Tag validation script already checks if tag exists
echo_step "Version validation passed"

# Run build and test
echo_step "Running build and test..."
"$SCRIPT_DIR/build-and-test.sh" --with-coverage

# Update CHANGELOG.md if it exists
if [ -f "CHANGELOG.md" ]; then
    echo_step "Updating CHANGELOG.md..."
    
    # Get the date
    release_date=$(date +%Y-%m-%d)
    
    # Create a temporary changelog entry
    temp_changelog=$(mktemp)
    
    # Add the new version entry
    echo "## [$VERSION] - $release_date" > "$temp_changelog"
    echo "" >> "$temp_changelog"
    
    # Get commits since last tag
    last_tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
    if [ -n "$last_tag" ]; then
        echo "### Changes since $last_tag" >> "$temp_changelog"
        git log --oneline "$last_tag"..HEAD --pretty=format:"- %s" >> "$temp_changelog"
    else
        echo "### Initial release" >> "$temp_changelog"
        git log --oneline --pretty=format:"- %s" >> "$temp_changelog"
    fi
    
    echo "" >> "$temp_changelog"
    echo "" >> "$temp_changelog"
    
    # Prepend to existing changelog
    if [ -f "CHANGELOG.md" ]; then
        cat "CHANGELOG.md" >> "$temp_changelog"
    fi
    
    mv "$temp_changelog" "CHANGELOG.md"
    
    echo_info "CHANGELOG.md updated"
fi

# Build the package
echo_step "Building package..."
rm -rf dist/
python -m build

# Create and push the tag
echo_step "Creating git tag..."
git tag -a "v$VERSION" -m "Release version $VERSION"

echo_step "Pushing tag to origin..."
git push origin "v$VERSION"

echo_info "Release process completed!"
echo_info "Version: $VERSION"
echo_info "Tag: v$VERSION"
echo_info ""
echo_info "The GitHub Actions workflow should now automatically:"
echo_info "1. Run tests on multiple platforms"
echo_info "2. Build binary artifacts"
echo_info "3. Create a GitHub release"
echo_info "4. Publish to PyPI"
echo_info ""
echo_info "Monitor the GitHub Actions workflow at:"
echo_info "https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/actions"

# Optional: Open the GitHub Actions page
if command -v open &> /dev/null; then
    read -p "Open GitHub Actions page? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        repo_url=$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/')
        open "https://github.com/$repo_url/actions"
    fi
fi