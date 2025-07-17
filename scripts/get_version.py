#!/usr/bin/env python3
"""
Version extraction script for split-python4gpt.
Gets the current version from git tags using setuptools_scm.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "src"))

try:
    from setuptools_scm import get_version
    
    def get_current_version():
        """Get the current version from git tags."""
        try:
            version = get_version(root=repo_root)
            return version
        except Exception as e:
            print(f"Error getting version: {e}", file=sys.stderr)
            return "0.0.0"
    
    if __name__ == "__main__":
        print(get_current_version())
        
except ImportError:
    print("setuptools_scm not available, using fallback version", file=sys.stderr)
    print("0.0.0")