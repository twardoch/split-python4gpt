# split-python4gpt

[![PyPI version](https://img.shields.io/pypi/v/split-python4gpt.svg)](https://pypi.org/project/split-python4gpt/)
[![License](https://img.shields.io/pypi/l/split-python4gpt.svg)](https://github.com/twardoch/split-python4gpt/blob/main/LICENSE.txt)
[![Docs](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://twardoch.github.io/split-python4gpt/)
[![CI](https://github.com/twardoch/split-python4gpt/actions/workflows/ci.yml/badge.svg)](https://github.com/twardoch/split-python4gpt/actions/workflows/ci.yml)

`split-python4gpt` is a Python tool designed to process and reorganize large Python projects into minified, type-annotated, and token-limited files. This is particularly useful for preparing Python codebases for analysis or processing by Large Language Models (LLMs) like OpenAI's GPT series, allowing them to handle the data in manageable chunks.

## Overview

**What is `split-python4gpt`?**

It's a command-line and programmatic tool that takes a Python file or an entire project directory as input and performs several operations:
1.  **Type Inference:** Optionally integrates with `pytype` to infer type hints and add them to your code.
2.  **Minification:** Optionally minifies the Python code using `python-minifier`, with granular control over various minification aspects (removing docstrings, comments, annotations, renaming variables, etc.).
3.  **Code Summarization:** For functions or classes exceeding a certain token threshold, their bodies can be replaced with `...` and a concise, AI-generated summary (requires an OpenAI API key).
4.  **Splitting for LLMs:** The processed code (potentially from multiple files) is then split into smaller text files, each respecting a specified token limit, making it suitable for LLMs with context window constraints.

**Who is it for?**

*   **Developers** working with LLMs who need to feed large Python codebases into models for analysis, understanding, refactoring, or documentation generation.
*   **Researchers** in software engineering or natural language processing who need to preprocess Python code for large-scale studies involving LLMs.
*   Anyone needing to reduce the size of Python code while preserving or enhancing its structure with type information, before passing it to token-sensitive systems.

**Why is it useful?**

*   **Manages LLM Context Limits:** LLMs have a finite context window. `split-python4gpt` breaks down large codebases into chunks that fit these limits.
*   **Reduces Token Count:** Minification and summarization significantly reduce the number of tokens, leading to faster processing and potentially lower API costs when using paid LLM services.
*   **Improves Code Clarity (for LLMs):** Adding type hints can make code easier for LLMs to understand and analyze. Summaries provide high-level context for complex code blocks.
*   **Automates Preprocessing:** Automates a tedious and error-prone part of the MLOps pipeline for code-based LLM tasks.

## Features

*   **Process Single Files or Entire Directories:** Handles individual Python scripts or recursively processes all `.py` files in a project.
*   **Optional Type Inference:** Uses `pytype` to add type annotations.
*   **Comprehensive Minification:** Leverages `python-minifier` with numerous configurable options:
    *   Remove docstrings and other literal statements (`mini_docs`).
    *   Rename global/local variable names (`mini_globs`, `mini_locs`).
    *   Hoist literal statements (`mini_lits`).
    *   Remove type annotations (`mini_annotations`).
    *   Remove `assert` and debugging statements (`mini_asserts`, `mini_debug`).
    *   Combine imports (`mini_imports`).
    *   Remove `object` base from classes (`mini_obj`).
    *   Remove `pass` statements (`mini_pass`).
    *   Convert positional to keyword arguments (`mini_posargs`).
    *   Remove explicit `return None` (`mini_retnone`).
    *   Remove shebang (`mini_shebang`).
*   **AI-Powered Code Summarization:** For functions/classes too large for LLM processing even after minification, their bodies can be replaced by an ellipsis (`...`) and a short summary generated via an OpenAI model (e.g., `gpt-3.5-turbo`).
*   **Token-Based Splitting:** Uses `tiktoken` to count tokens (compatible with OpenAI models) and splits the combined, processed code from all input files into multiple output files, ensuring each part is below a specified token limit.
*   **Configurable Output:** Specify output directories for processed files and type stubs (`.pyi` files).
*   **Preserves Relative Paths:** Maintains the original project structure in the output directory.

## Installation

**Prerequisites:**

*   Python 3.10 (it will not work with Python < 3.10 or >= 3.11).
*   An OpenAI API Key (if you intend to use the code summarization feature). Set it as an environment variable: `export OPENAI_API_KEY="your_api_key_here"`.
*   `pytype` is used for type inference. While listed as a dependency, ensure it's correctly installed and accessible in your environment, especially if using virtual environments or specific Python versions. `split-python4gpt` looks for a Python executable matching the version it's configured for (default 3.10, e.g., `python3.10`).

**Installation Steps:**

1.  It is recommended to install the tool in a virtual environment:
    ```bash
    python3.10 -m venv .venv
    source .venv/bin/activate
    ```
2.  Install `split-python4gpt` using pip:
    ```bash
    pip install split-python4gpt
    ```
    This will also install its dependencies: `fire`, `tiktoken`, `python-minifier`, `pytype`, and `simpleaichat`.

## Usage

`split-python4gpt` can be used both as a command-line tool and programmatically in your Python scripts.

### Command-Line Interface (CLI)

The primary command is `mdsplit4gpt`.

```bash
mdsplit4gpt [PATH_OR_FOLDER] [OPTIONS]
```

**Key Arguments & Options:**

*   `path_or_folder` (str | Path): Path to the input Python file or folder.
*   `--out` (str | Path | None): Output folder for processed files. Defaults to the input folder (modifies files in place if not set).
*   `--pyis` (str | Path | None): Directory for storing generated `.pyi` files (type stubs from `pytype`). Defaults to the output folder.
*   `--types` (bool, default: True): Infer types using PyType. Set to `--types=False` to disable.
*   `--mini` (bool, default: True): Minify the Python scripts. Set to `--mini=False` to disable.
*   Minification Options (all default to True if `--mini` is True, unless specified):
    *   `--mini_docs` (bool): Remove docstrings.
    *   `--mini_globs` (bool, default: False): Rename global names.
    *   `--mini_locs` (bool, default: False): Rename local names.
    *   `--mini_lits` (bool): Hoist literal statements. (Note: `python-minifier` default for this is `False`, but `split-python4gpt` defaults it to `True` via its main function argument default, though the class `PyTypingMinifier` itself has `hoist_literals=False` as its internal default for `minify` calls if not overridden).
    *   `--mini_annotations` (bool): Remove annotations.
    *   `--mini_asserts` (bool): Remove asserts.
    *   `--mini_debug` (bool): Remove debugging statements.
    *   `--mini_imports` (bool): Combine imports.
    *   `--mini_obj` (bool): Remove object base.
    *   `--mini_pass` (bool): Remove pass statements.
    *   `--mini_posargs` (bool): Convert positional to keyword args.
    *   `--mini_retnone` (bool): Remove explicit return None statements.
    *   `--mini_shebang` (bool): Remove shebang. (Set `--mini_shebang=False` to preserve shebang).
*   LLM Splitting Options (via `PyLLMSplitter` class, implicitly used by `mdsplit4gpt`):
    *   The CLI doesn't directly expose `gptok_model`, `gptok_limit`, `gptok_threshold` yet. These are currently hardcoded or have defaults in `PyLLMSplitter`. For custom LLM splitting parameters, programmatic usage is recommended.

**Example Usage:**

1.  **Process a single file, minify and infer types, output to `output_dir`:**
    ```bash
    mdsplit4gpt my_script.py --out output_dir
    ```
    This will create `output_dir/my_script.py` (processed) and `output_dir/split4gpt/split1.py` (and potentially more splits).

2.  **Process an entire project in `my_project/`, disable type inference, keep docstrings, output to `processed_project/`:**
    ```bash
    mdsplit4gpt my_project/ --out processed_project/ --types=False --mini_docs=False
    ```
    This will create `processed_project/my_project/...` (processed files) and `processed_project/my_project/split4gpt/split1.py`, etc.

### Programmatic Usage

You can use the core classes `PyTypingMinifier` and `PyLLMSplitter` directly in your Python code for more control.

```python
from pathlib import Path
from split_python4gpt import PyLLMSplitter # Or PyTypingMinifier for just types/minification

# Ensure OPENAI_API_KEY is set as an environment variable if using summarization features
# import os
# os.environ["OPENAI_API_KEY"] = "your_api_key"

# Initialize the splitter
# You can specify gptok_model, gptok_limit, gptok_threshold here
splitter = PyLLMSplitter(
    gptok_model="gpt-3.5-turbo",
    gptok_limit=4000,
    gptok_threshold=200 # Code sections over this token count might be summarized
)

input_path = "path/to/your/python_project_or_file"
output_dir = "path/to/output_directory"
pyi_dir = "path/to/pyi_files_directory" # Can be the same as output_dir

# Process the Python code
# minify_options can be passed as kwargs, e.g., remove_literal_statements=False
processed_file_paths = splitter.process_py(
    py_path_or_folder=input_path,
    out_py_folder=output_dir,
    pyi_folder=pyi_dir,
    types=True,  # Enable type inference
    mini=True,   # Enable minification
    # Minifier options:
    remove_literal_statements=True, # Equivalent to mini_docs=True
    rename_globals=False,
    # ... other minifier options from python-minifier ...
)

# Write the split files for LLM consumption
splitter.write_splits() # This will create a 'split4gpt' subdirectory in output_dir

print(f"Processed files: {processed_file_paths}")
print(f"LLM splits written to: {Path(output_dir) / 'split4gpt'}")
```

## Technical Deep Dive

### How it Works

The tool operates in several stages:

1.  **File Discovery:**
    *   If a single file path is provided, it's processed.
    *   If a folder path is provided, it recursively finds all `*.py` files within that folder.

2.  **Initialization (`PyTypingMinifier.init_folders`, `PyTypingMinifier.init_code_data`):**
    *   Input, output, and `.pyi` (type stub) directories are resolved and created if they don't exist.
    *   Original files are copied to the output directory if `out` is different from the input path.
    *   Data structures are prepared to hold code content and paths.

3.  **Processing per file (`PyTypingMinifier.process_py` which calls `infer_types` and `minify`):**
    *   **Type Inference (optional):**
        *   If `types=True`, `pytype` is invoked as a subprocess for the current file.
        *   `pytype` generates a `.pyi` stub file.
        *   The content of this `.pyi` file is then merged back into the Python source code using `pytype.tools.merge_pyi`.
        *   Errors during `pytype` execution are caught, and a warning is logged; processing continues.
    *   **Minification (optional):**
        *   If `mini=True`, the (potentially type-annotated) code is passed to `python-minifier`.
        *   Various minification options (passed from the CLI or programmatic call) control the minifier's behavior (e.g., removing docstrings, renaming variables).

4.  **Code Summarization and Sectioning for LLMs (`PyLLMSplitter.process_py_code`):**
    *   This step occurs after the initial type inference and minification if `PyLLMSplitter` is used (which is the case for the `mdsplit4gpt` CLI tool).
    *   The code of each file is parsed into an Abstract Syntax Tree (AST).
    *   Top-level nodes (imports, variable assignments, functions, classes) are processed.
    *   For each function (`FunctionDef`) or class (`ClassDef`):
        *   Its source code is minified (again, with docstrings preserved temporarily for summarization context).
        *   Its token count is calculated using `tiktoken`.
        *   If the token count exceeds `gptok_threshold` (default 128):
            *   The `PyBodySummarizer` (an `ast.NodeTransformer`) is invoked.
            *   `PyBodySummarizer` attempts to generate a concise summary of the function/class body using `simpleaichat` (which calls an OpenAI GPT model).
            *   The original body of the function/class is replaced in the AST with this summary (as a docstring) and an ellipsis (`...`).
            *   The modified AST node (with summarized body) is then converted back to minified source code.
    *   The file is thus broken down into a list of "sections," each being a string of minified Python code (e.g., an import block, a variable assignment, a function definition, a summarized function definition). Each section has its token count.

5.  **Splitting for LLMs (`PyLLMSplitter.write_splits`):**
    *   All processed sections from all input files are collected.
    *   The tool iterates through these sections, prepending a `# File: <original_filepath>` comment before the sections of each new file.
    *   It accumulates sections into a "portion" of text, keeping track of the current token size.
    *   If adding the next section (plus its file header if it's from a new file) would exceed `gptok_limit` (default based on `gptok_model`, e.g., 4096 for `gpt-3.5-turbo`):
        *   The current portion is written to a new file: `splitN.py` (e.g., `split1.py`, `split2.py`) in a `split4gpt` subdirectory within the main output folder.
        *   A new portion is started.
    *   Any remaining portion is written to a final split file.

**Output Structure:**

*   **Processed Python Files:** If an `out` directory is specified, minified/type-annotated versions of your original Python files are placed there, maintaining the original directory structure. If `out` is not specified, original files are modified in place (use with caution!).
*   **`.pyi` files:** If `pyis` directory is specified (defaults to `out` directory), `pytype` will generate `.pyi` stub files there (typically within a `.pytype/pyi/` subfolder structure).
*   **`split4gpt` directory:** Inside the `out` directory (or input directory if `out` is not set), a `split4gpt` subdirectory is created. This contains the `splitN.py` files, which are the final chunks intended for LLMs.

### Core Components

*   **`PyTypingMinifier`:**
    *   Manages file/folder paths for input, output, and `.pyi` stubs.
    *   Orchestrates `pytype` for type inference and `python-minifier` for code minification.
    *   Handles reading Python files and applying these transformations.
*   **`PyBodySummarizer(ast.NodeTransformer)`:**
    *   Used by `PyLLMSplitter`.
    *   Visits `FunctionDef` and `ClassDef` nodes in an AST.
    *   If a node's code is too long (token-wise), it replaces its body with `...` and an AI-generated docstring summary.
*   **`PyLLMSplitter(PyTypingMinifier)`:**
    *   Inherits type inference and minification capabilities.
    *   Adds LLM-specific processing:
        *   Uses `tiktoken` to count tokens accurately for OpenAI models.
        *   Employs `PyBodySummarizer` to condense oversized code elements.
        *   Chunks the processed code from all input files into multiple smaller files (`splitN.py`) based on `gptok_limit`.
        *   Uses `simpleaichat` to interact with an OpenAI API for the summarization feature.

## Contributing

Contributions are welcome! Please follow these guidelines:

1.  **Fork the repository** on GitHub.
2.  **Create a new branch** for your feature or bug fix: `git checkout -b feature/your-feature-name` or `git checkout -b fix/your-bug-fix`.
3.  **Set up the development environment:**
    *   It's recommended to use a virtual environment with Python 3.10.
    *   Install dependencies, including testing tools:
        ```bash
        pip install -e .[testing]
        ```
    *   This project uses `pre-commit` for code quality checks. Install and set up the hooks:
        ```bash
        pip install pre-commit
        pre-commit install
        ```
        Before committing, `pre-commit` will run tools like `black`, `isort`, and `flake8`.
4.  **Make your changes.**
5.  **Adhere to coding standards:**
    *   Code is formatted with `black`.
    *   Imports are sorted with `isort`.
    *   Follow PEP 8 guidelines.
    *   `flake8` is used for linting with the following configurations (see `setup.cfg`):
        *   `max_line_length = 88`
        *   `extend_ignore = E203, W503` (E203: whitespace before ':', often conflicts with black; W503: line break before binary operator, also a black preference).
6.  **Add tests** for your changes in the `tests/` directory.
7.  **Run tests** using `tox` (which also checks coverage) or `pytest`:
    ```bash
    tox
    # OR
    pytest
    ```
    Ensure all tests pass.
8.  **Commit your changes** with a clear and descriptive commit message.
9.  **Push your branch** to your fork: `git push origin feature/your-feature-name`.
10. **Create a Pull Request (PR)** against the `main` branch of the original repository.

## License

This project is licensed under the **Apache License 2.0**. See the [LICENSE.txt](LICENSE.txt) file for details.

## Authors

*   Adam Twardoch ([@twardoch](https://github.com/twardoch))

This project was scaffolded using [PyScaffold](https://pyscaffold.org/).
