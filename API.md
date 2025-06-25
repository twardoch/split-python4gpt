<a id="split_python4gpt"></a>

# split\_python4gpt

<a id="split_python4gpt.__main__"></a>

# split\_python4gpt.\_\_main\_\_

<a id="split_python4gpt.__main__.split_python4gpt"></a>

#### split\_python4gpt

```python
def split_python4gpt(path_or_folder: str | Path,
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
                     mini_shebang: bool = True)
```

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

<a id="split_python4gpt.minifier"></a>

# split\_python4gpt.minifier
