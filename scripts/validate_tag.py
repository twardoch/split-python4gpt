#!/usr/bin/env python3
"""
Tag validation script for split-python4gpt.
Validates that a git tag follows semantic versioning format.
"""

import re
import sys
import subprocess
from pathlib import Path


def validate_semver(version):
    """Validate that a version string follows semantic versioning."""
    # Basic semver regex
    semver_pattern = r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*|[0-9a-zA-Z-]*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*|[0-9a-zA-Z-]*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
    
    return re.match(semver_pattern, version) is not None


def get_git_tags():
    """Get all git tags."""
    try:
        result = subprocess.run(['git', 'tag', '-l'], capture_output=True, text=True)
        if result.returncode == 0:
            return [tag.strip() for tag in result.stdout.split('\n') if tag.strip()]
        return []
    except Exception:
        return []


def tag_exists(tag):
    """Check if a tag already exists."""
    tags = get_git_tags()
    return tag in tags


def main():
    if len(sys.argv) != 2:
        print("Usage: validate_tag.py <version>")
        print("Example: validate_tag.py 1.2.3")
        sys.exit(1)
    
    version = sys.argv[1]
    
    # Remove 'v' prefix if present
    if version.startswith('v'):
        version = version[1:]
    
    # Validate semver format
    if not validate_semver(version):
        print(f"❌ Invalid version format: {version}")
        print("Version must follow semantic versioning (e.g., 1.2.3)")
        sys.exit(1)
    
    print(f"✅ Valid semver format: {version}")
    
    # Check if tag already exists
    tag_with_v = f"v{version}"
    if tag_exists(tag_with_v):
        print(f"❌ Tag {tag_with_v} already exists!")
        sys.exit(1)
    
    print(f"✅ Tag {tag_with_v} does not exist yet")
    
    # Parse version components
    parts = version.split('.')
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
    
    # Get current tags and suggest next version
    tags = get_git_tags()
    version_tags = []
    
    for tag in tags:
        if tag.startswith('v'):
            tag_version = tag[1:]
            if validate_semver(tag_version):
                tag_parts = tag_version.split('.')
                if len(tag_parts) >= 3:
                    try:
                        v_major, v_minor, v_patch = int(tag_parts[0]), int(tag_parts[1]), int(tag_parts[2])
                        version_tags.append((v_major, v_minor, v_patch, tag))
                    except ValueError:
                        continue
    
    if version_tags:
        version_tags.sort(reverse=True)
        latest_version = version_tags[0]
        latest_tag = latest_version[3]
        
        print(f"📍 Latest existing tag: {latest_tag}")
        
        # Check if new version is greater than latest
        if (major, minor, patch) <= (latest_version[0], latest_version[1], latest_version[2]):
            print(f"⚠️  Warning: New version {version} is not greater than latest {latest_tag[1:]}")
            print("Consider using a higher version number")
    
    print(f"✅ Version {version} is valid for tagging")


if __name__ == "__main__":
    main()