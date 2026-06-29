# this_file: src/split_python4gpt/__init__.py
"""split-python4gpt — minify and split Python projects for LLM consumption."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from .minifier import PyTypingMinifier

__all__ = ["PyTypingMinifier", "__version__"]

try:
    __version__: str = version("split-python4gpt")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"
