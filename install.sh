#!/usr/bin/env bash
# install.sh: Install split-python4gpt in editable mode
# split_python4gpt: Split Python source files into chunks for GPT context windows

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Installing split-python4gpt (editable) ==="
uv pip install -e .
echo "=== Install complete ==="
