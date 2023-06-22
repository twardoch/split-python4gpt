# split_python4gpt

`split_python4gpt` is a Python tool designed to reorganize large Python projects into minified files based on a specified token limit. This is particularly useful for processing large Python projects with GPT models, as it allows the models to handle the data in manageable chunks.

_**Version 1.0.2** (2023-06-22)_

### NOT IMPLEMENTED YET

Warning: The code does not yet implement the splitting or token counting, only type inference and minification. Use at your own risk.

## Installation

You can install `split_python4gpt` via pip:

```bash
pip install split_python4gpt
```

## CLI Usage

### This is not yet implemented!

After installation, you can use the `pysplit4gpt` or `python3.10 -m split_python4gpt` command to split a Python file. Here's the basic syntax:

```bash
python3.10 -m split_python4gpt py_path_or_folder --model gpt-3.5-turbo --limit 4096 --separator "=== SPLIT ==="
```

This command will split the Python file or all Python files in `py_path_or_folder` into sections, each containing no more than 4096 tokens (as counted by the `gpt-3.5-turbo` model). The sections will be separated by `=== SPLIT ===`.

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

