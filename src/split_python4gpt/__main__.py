#!/usr/bin/env python3
from pathlib import Path

import fire
from .minifier import PyTypingMinifier


def split_python4gpt(
    path_or_folder: str | Path,
    out: str | Path | None = None,
    pyis: str | Path | None = None,
    types: bool = True,
    mini: bool = True,
    mini_docs: bool = True,
    mini_globs: bool = False,
    mini_locs: bool = False,
    mini_lits: bool = True,
    mini_annotations: bool = True,
    mini_asserts: bool = True,
    mini_debug: bool = True,
    mini_imports: bool = True,
    mini_obj: bool = True,
    mini_pass: bool = True,
    mini_posargs: bool = True,
    mini_retnone: bool = True,
    mini_shebang: bool = True,
):
    """
    Minify Python scripts or projects and/or infer types in them.

    Args:
        path_or_folder (str | Path): Path to the input Python file or folder.
        out (str | Path | None, optional): Output folder for the processed files. Defaults to input folder.
        pyis (str | Path | None, optional): Directory for storing generated .pyi files. Defaults to the output folder.
        types (bool, optional): Infer types using PyType? Defaults to True.
        mini (bool, optional): Minify the Python scripts? Defaults to True.
        mini_docs (bool, optional): Remove docstrings? Defaults to True.
        mini_globs (bool, optional): Rename global names? Defaults to False.
        mini_locs (bool, optional): Rename local names? Defaults to False.
        mini_lits (bool, optional): Hoist literal statements? Defaults to True.
        mini_annotations (bool, optional): Remove annotations? Defaults to True.
        mini_asserts (bool, optional): Remove asserts? Defaults to True.
        mini_debug (bool, optional): Remove debugging statements? Defaults to True.
        mini_imports (bool, optional): Combine imports? Defaults to True.
        mini_obj (bool, optional): Remove object base? Defaults to True.
        mini_pass (bool, optional): Remove pass statements? Defaults to True.
        mini_posargs (bool, optional): Convert positional to keyword args? Defaults to True.
        mini_retnone (bool, optional): Remove explicit return None statements? Defaults to True.
        mini_shebang (bool, optional): Remove shebang? Defaults to True.

    Returns:
        list[Path]: List of output Python files.
    """
    return PyTypingMinifier().process_py(
        py_path_or_folder=path_or_folder,
        out_py_folder=out,
        pyi_folder=pyis,
        types=types,
        mini=mini,
        combine_imports=mini_imports,
        convert_posargs_to_args=mini_posargs,
        hoist_literals=mini_lits,
        preserve_shebang=not mini_shebang,
        remove_annotations=mini_annotations,
        remove_asserts=mini_asserts,
        remove_debug=mini_debug,
        remove_explicit_return_none=mini_retnone,
        remove_literal_statements=mini_docs,
        remove_object_base=mini_obj,
        remove_pass=mini_pass,
        rename_globals=mini_globs,
        rename_locals=mini_locs,
    )


def cli():
    fire.core.Display = lambda lines, out: print(*lines, file=out)
    fire.Fire(split_python4gpt)


if __name__ == "__main__":
    cli()
