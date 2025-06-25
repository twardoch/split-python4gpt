"""
Dummy conftest.py for split_python4gpt.

If you don't know what this is for, just leave it empty.
Read more about conftest.py under:
- https://docs.pytest.org/en/stable/fixture.html
- https://docs.pytest.org/en/stable/writing_plugins.html
"""

import logging

# import pytest

# Configure basic logging for all tests to see output from the library
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(name)s:%(module)s:%(funcName)s:%(lineno)d: %(message)s",
)
