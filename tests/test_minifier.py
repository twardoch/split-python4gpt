import pytest
from split_python4gpt.minifier import PyTypingMinifier
from pathlib import Path


@pytest.fixture
def minifier():
    return PyTypingMinifier()


def test_minify_code(minifier):
    # Test if the minify method returns the expected result
    in_code = Path(Path(__file__).parent / "data" / "in_test.py").read_text()
    out_code = Path(Path(__file__).parent / "data" / "out_test.py").read_text()

    minified_code = minifier.minify(in_code)

    assert minified_code == out_code
