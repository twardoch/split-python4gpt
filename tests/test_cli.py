"""Integration tests for the CLI functionality."""

import subprocess
import sys
import tempfile
from pathlib import Path
import pytest


def test_cli_help():
    """Test that the CLI help command works."""
    result = subprocess.run([
        sys.executable, "-m", "split_python4gpt", "--help"
    ], capture_output=True, text=True)
    
    assert result.returncode == 0
    assert "mdsplit4gpt" in result.stdout or "split_python4gpt" in result.stdout


def test_cli_version():
    """Test that we can get version information."""
    # This will test both the CLI and the version system
    result = subprocess.run([
        sys.executable, "-c", 
        "from split_python4gpt import __version__; print(__version__)"
    ], capture_output=True, text=True)
    
    # Should not error even if version is 0.0.0
    assert result.returncode == 0
    version = result.stdout.strip()
    assert len(version) > 0
    # Basic semver pattern check
    assert "." in version


def test_cli_basic_processing():
    """Test basic CLI processing functionality."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Create a simple test file
        test_file = tmp_path / "test_input.py"
        test_file.write_text('''
def hello_world():
    """A simple function."""
    print("Hello, World!")
    return "Hello"

x = hello_world()
''')
        
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        # Run the CLI tool
        result = subprocess.run([
            sys.executable, "-m", "split_python4gpt",
            str(test_file),
            "--out", str(output_dir),
            "--types=False",  # Disable types to avoid pytype dependency issues
            "--mini=True"
        ], capture_output=True, text=True)
        
        # Should not crash
        assert result.returncode == 0
        
        # Check that output file exists
        output_file = output_dir / "test_input.py"
        assert output_file.exists()
        
        # Check that minification occurred (no docstrings)
        content = output_file.read_text()
        assert '"""A simple function."""' not in content
        assert "def hello_world():" in content


def test_cli_folder_processing():
    """Test CLI processing of a folder."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Create a folder structure
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        
        # Create test files
        (input_dir / "file1.py").write_text('''
def func1():
    """Function 1."""
    return 1
''')
        
        subdir = input_dir / "subdir"
        subdir.mkdir()
        (subdir / "file2.py").write_text('''
def func2():
    """Function 2."""
    return 2
''')
        
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        # Run the CLI tool on the folder
        result = subprocess.run([
            sys.executable, "-m", "split_python4gpt",
            str(input_dir),
            "--out", str(output_dir),
            "--types=False",  # Disable types to avoid pytype dependency issues
            "--mini=True"
        ], capture_output=True, text=True)
        
        # Should not crash
        assert result.returncode == 0
        
        # Check that output structure is maintained
        assert (output_dir / "file1.py").exists()
        assert (output_dir / "subdir" / "file2.py").exists()
        
        # Check that split files are created
        split_dir = output_dir / "split4gpt"
        assert split_dir.exists()
        split_files = list(split_dir.glob("split*.py"))
        assert len(split_files) > 0