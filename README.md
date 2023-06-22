# split_python4gpt

`split_python4gpt` is a Python tool designed to reorganize large Python projects into minified files based on a specified token limit. This is particularly useful for processing large Python projects with GPT models, as it allows the models to handle the data in manageable chunks.

_**Version 1.0.3** (2023-06-22)_

### NOT IMPLEMENTED YET

Warning: The code does not yet implement the splitting or token counting, only type inference and minification. Use at your own risk.

## Installation

You can install `split_python4gpt` via pip:

```bash
pip install split_python4gpt
```

## CLI Usage

After installation, you can use the `pysplit4gpt` or `python3.10 -m split_python4gpt` command: 

```
python3.10 -m split_python4gpt PATH_OR_FOLDER [FLAGS]

POSITIONAL ARGUMENTS
    PATH_OR_FOLDER
        Type: str | pathlib.Path
        Path to the input Python file or folder.

FLAGS
    -o, --out=OUT
        Type: Optional[str | pathlib...
        Default: None
        Output folder for the processed files. Defaults to input folder.
    -p, --pyis=PYIS
        Type: Optional[str | pathlib...
        Default: None
        Directory for storing generated .pyi files. Defaults to the output folder.
    -t, --types=TYPES
        Type: bool
        Default: True
        Infer types using PyType? Defaults to True.
    --mini=MINI
        Type: bool
        Default: True
        Minify the Python scripts? Defaults to True.
    --mini_docs=MINI_DOCS
        Type: bool
        Default: True
        Remove docstrings? Defaults to True.
    --mini_globs=MINI_GLOBS
        Type: bool
        Default: False
        Rename global names? Defaults to False.
    --mini_locs=MINI_LOCS
        Type: bool
        Default: False
        Rename local names? Defaults to False.
    --mini_lits=MINI_LITS
        Type: bool
        Default: True
        Hoist literal statements? Defaults to True.
    --mini_annotations=MINI_ANNOTATIONS
        Type: bool
        Default: True
        Remove annotations? Defaults to True.
    --mini_asserts=MINI_ASSERTS
        Type: bool
        Default: True
        Remove asserts? Defaults to True.
    --mini_debug=MINI_DEBUG
        Type: bool
        Default: True
        Remove debugging statements? Defaults to True.
    --mini_imports=MINI_IMPORTS
        Type: bool
        Default: True
        Combine imports? Defaults to True.
    --mini_obj=MINI_OBJ
        Type: bool
        Default: True
        Remove object base? Defaults to True.
    --mini_pass=MINI_PASS
        Type: bool
        Default: True
        Remove pass statements? Defaults to True.
    --mini_posargs=MINI_POSARGS
        Type: bool
        Default: True
        Convert positional to keyword args? Defaults to True.
    --mini_retnone=MINI_RETNONE
        Type: bool
        Default: True
        Remove explicit return None statements? Defaults to True.
    --mini_shebang=MINI_SHEBANG
        Type: bool
        Default: True
        Remove shebang? Defaults to True.
```

## Python usage

- **[See the API documentation](https://twardoch.github.io/split-python4gpt/API.html)** for more advanced usage

## Changelog

- v1.0.0: Initial release

## Contributing

Contributions to `split_python4gpt` are welcome! Please open an issue or submit a pull request on the [GitHub repository](https://github.com/twardoch/split-python4gpt).

## License

- Copyright (c) 2023 [Adam Twardoch](./AUTHORS.md)
- Written with assistance from ChatGPT
- Licensed under the [Apache License 2.0](./LICENSE.txt)<a id="split_python4gpt"></a>

