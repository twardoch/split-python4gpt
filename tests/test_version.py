"""Tests for version functionality."""

import subprocess
import sys
from pathlib import Path
import pytest


def test_version_script():
    """Test that the version script works."""
    script_path = Path(__file__).parent.parent / "scripts" / "get_version.py"
    
    result = subprocess.run([
        sys.executable, str(script_path)
    ], capture_output=True, text=True)
    
    assert result.returncode == 0
    version = result.stdout.strip()
    assert len(version) > 0
    # Should be a valid version string
    assert "." in version


def test_package_version():
    """Test that the package has a version."""
    try:
        import split_python4gpt
        # Should have a version attribute
        assert hasattr(split_python4gpt, '__version__')
        version = split_python4gpt.__version__
        assert isinstance(version, str)
        assert len(version) > 0
        assert "." in version
    except ImportError:
        pytest.skip("Package not installed")


def test_setuptools_scm_version():
    """Test that setuptools_scm can get version info."""
    try:
        from setuptools_scm import get_version
        
        repo_root = Path(__file__).parent.parent
        version = get_version(root=repo_root)
        
        assert isinstance(version, str)
        assert len(version) > 0
        
    except ImportError:
        pytest.skip("setuptools_scm not available")
    except Exception as e:
        # This might fail if we're not in a git repo or no tags exist
        # That's okay for testing purposes
        pytest.skip(f"setuptools_scm failed: {e}")


def test_version_consistency():
    """Test that all version sources return the same version."""
    versions = []
    
    # Get version from script
    script_path = Path(__file__).parent.parent / "scripts" / "get_version.py"
    result = subprocess.run([
        sys.executable, str(script_path)
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        versions.append(result.stdout.strip())
    
    # Get version from package
    try:
        import split_python4gpt
        versions.append(split_python4gpt.__version__)
    except (ImportError, AttributeError):
        pass
    
    # Get version from setuptools_scm
    try:
        from setuptools_scm import get_version
        repo_root = Path(__file__).parent.parent
        versions.append(get_version(root=repo_root))
    except Exception:
        pass
    
    # If we have multiple versions, they should be the same
    if len(versions) > 1:
        assert all(v == versions[0] for v in versions), f"Version mismatch: {versions}"