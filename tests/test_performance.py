"""Performance tests for split-python4gpt."""

import time
from pathlib import Path
import tempfile
import pytest

from split_python4gpt.minifier import PyTypingMinifier


def create_large_python_file(path: Path, num_functions: int = 100):
    """Create a large Python file with many functions."""
    content = []
    
    for i in range(num_functions):
        function_code = f'''
def function_{i}(arg1, arg2=None):
    """
    This is function number {i}.
    
    Args:
        arg1: First argument
        arg2: Optional second argument
    
    Returns:
        The result of the function
    """
    if arg2 is None:
        arg2 = "default"
    
    result = f"Function {{i}} called with {{arg1}} and {{arg2}}"
    
    # Some complex logic
    data = []
    for j in range(10):
        data.append({{
            "index": j,
            "value": arg1 + str(j),
            "computed": j * i if i > 0 else j
        }})
    
    # More processing
    filtered_data = [item for item in data if item["computed"] % 2 == 0]
    
    return {{
        "result": result,
        "data": filtered_data,
        "function_id": {i}
    }}
'''
        content.append(function_code)
    
    # Add some module-level code
    content.append(f'''
# Module level code
CONSTANT_VALUE = {num_functions}

def main():
    """Main function to test all generated functions."""
    results = []
    for i in range(CONSTANT_VALUE):
        func_name = f"function_{{i}}"
        if func_name in globals():
            result = globals()[func_name](f"test_{{i}}", f"arg_{{i}}")
            results.append(result)
    return results

if __name__ == "__main__":
    main()
''')
    
    path.write_text('\n'.join(content))


@pytest.mark.performance
def test_large_file_processing():
    """Test processing of a large Python file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Create a large file
        large_file = tmp_path / "large_file.py"
        create_large_python_file(large_file, num_functions=50)
        
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        minifier = PyTypingMinifier()
        
        # Measure processing time
        start_time = time.time()
        
        processed_files = minifier.process_py(
            py_path_or_folder=large_file,
            out_py_folder=output_dir,
            pyi_folder=output_dir / "pyi",
            types=False,  # Disable types for performance test
            mini=True
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should complete in reasonable time (less than 30 seconds)
        assert processing_time < 30.0, f"Processing took too long: {processing_time:.2f}s"
        
        # Should produce output
        assert len(processed_files) == 1
        output_file = processed_files[0]
        assert output_file.exists()
        
        # Output should be smaller than input (due to minification)
        original_size = large_file.stat().st_size
        output_size = output_file.stat().st_size
        assert output_size < original_size, "Minification should reduce file size"


@pytest.mark.performance
def test_multiple_files_processing():
    """Test processing of multiple files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Create multiple files
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        
        num_files = 10
        for i in range(num_files):
            file_path = input_dir / f"file_{i}.py"
            create_large_python_file(file_path, num_functions=20)
        
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        minifier = PyTypingMinifier()
        
        # Measure processing time
        start_time = time.time()
        
        processed_files = minifier.process_py(
            py_path_or_folder=input_dir,
            out_py_folder=output_dir,
            pyi_folder=output_dir / "pyi",
            types=False,  # Disable types for performance test
            mini=True
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should complete in reasonable time
        assert processing_time < 60.0, f"Processing took too long: {processing_time:.2f}s"
        
        # Should process all files
        assert len(processed_files) == num_files
        
        # All output files should exist
        for pf in processed_files:
            assert pf.exists()


@pytest.mark.performance
def test_memory_usage():
    """Test that memory usage doesn't grow excessively."""
    import psutil
    import os
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Create a moderately large file
        large_file = tmp_path / "memory_test.py"
        create_large_python_file(large_file, num_functions=100)
        
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        minifier = PyTypingMinifier()
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Process the file
        processed_files = minifier.process_py(
            py_path_or_folder=large_file,
            out_py_folder=output_dir,
            pyi_folder=output_dir / "pyi",
            types=False,
            mini=True
        )
        
        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100.0, f"Memory usage increased too much: {memory_increase:.2f}MB"
        
        # Should still produce output
        assert len(processed_files) == 1
        assert processed_files[0].exists()