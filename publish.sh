#!/usr/bin/env bash
# publish.sh: Build, install, version, and publish split-python4gpt to PyPI
# split_python4gpt: Split Python source files into chunks for GPT context windows

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Build ==="
bash "$SCRIPT_DIR/build.sh"

echo "=== Install ==="
bash "$SCRIPT_DIR/install.sh"

echo "=== Version bump ==="
uvx gitnextver@latest

echo "=== Final build & publish ==="
uvx hatch build
uv publish

echo "=== Publish complete ==="
