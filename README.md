# split-python4gpt

[![PyPI version](https://img.shields.io/pypi/v/split-python4gpt.svg)](https://pypi.org/project/split-python4gpt/)
[![License](https://img.shields.io/pypi/l/split-python4gpt.svg)](https://github.com/twardoch/split-python4gpt/blob/main/LICENSE.txt)
[![Docs](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://twardoch.github.io/split-python4gpt/)
[![CI](https://github.com/twardoch/split-python4gpt/actions/workflows/ci.yml/badge.svg)](https://github.com/twardoch/split-python4gpt/actions/workflows/ci.yml)

`split-python4gpt` processes and reorganizes large Python projects into minified, type-annotated, and token-limited files. This prepares codebases for analysis by Large Language Models (LLMs) like OpenAI's GPT series, allowing them to handle data in manageable chunks.

## Overview

**What is `split-python4gpt`?**

A command-line and programmatic tool that takes Python files or project directories as input and performs:
1. **Type Inference:** Integrates with `pytype` to add type hints
2. **Minification:** Uses `python-minifier` with configurable options
3. **Code Summarization:** Replaces large functions/classes with `...` and AI-generated summaries (requires OpenAI API key)
4. **Splitting for LLMs:** Breaks processed code into smaller files respecting token limits

**Who is it for?**

* **Developers** working with LLMs who need to analyze large Python codebases
* **Researchers** in software engineering or NLP preprocessing Python code for studies
* Anyone reducing Python code size while preserving structure before passing to token-sensitive systems

**Why is it useful?**

* **Manages LLM Context Limits:** Breaks code into chunks that fit finite context windows
* **Reduces Token Count:** Minification and summarization significantly cut tokens, reducing processing time and API costs
* **Improves Code Clarity:** Type hints help LLMs understand code; summaries provide context for complex blocks
* **Automates Preprocessing:** Handles tedious parts of the MLOps pipeline for code-based LLM tasks

## Features

* **Process Single Files or Entire Directories:** Handles individual scripts or recursively processes all `.py` files
* **Optional Type Inference:** Uses `pytype` to add type annotations
* **Comprehensive Minification:** Leverages `python-minifier` with configurable options:
    * Remove docstrings (`mini_docs`)
    * Rename global/local variables (`mini_globs`, `mini_locs`)
    * Hoist literal statements (`mini_lits`)
    * Remove type annotations (`mini_annotations`)
    * Remove `assert` and debugging statements (`mini_asserts`, `mini_debug`)
    * Combine imports (`mini_imports`)
    * Remove `object` base from classes (`mini_obj`)
    * Remove `pass` statements (`mini_pass`)
    * Convert positional to keyword arguments (`mini_posargs`)
    * Remove explicit `return None` (`mini_retnone`)
    * Remove shebang (`mini_shebang`)
* **AI-Powered Code Summarization:** Replaces large functions/classes with `...` and summaries via OpenAI models
* **Token-Based Splitting:** Uses `tiktoken` to count tokens and split code into multiple files respecting limits
* **Configurable Output:** Specify output directories for processed files and type stubs
* **Preserves Relative Paths:** Maintains original project structure in output

## Installation

**Prerequisites:**

* Python 3.10 or later (3.11, 3.12, 3.13 are all supported)
* An OpenAI API key is required **only** for LLM summarisation (`export OPENAI_API_KEY="your_api_key_here"`)
* `pytype` is optional — install the `[types]` extra for type inference

### Installation

```bash
pip install split-python4gpt
```

Optional extras:

```bash
# Type inference via pytype
pip install "split-python4gpt[types]"

# LLM summarisation (tiktoken + simpleaichat)
pip install "split-python4gpt[llm]"
```

#### From source

1. Install in virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -e ".[dev]"
    ```

Installs dependencies: `fire`, `tiktoken`, `python-minifier`, `pytype`, and `simpleaichat`.

#### Option 2: Pre-built Binary

Download from [releases page](https://github.com/twardoch/split-python4gpt/releases):

- **Linux**: `mdsplit4gpt-linux-x86_64`
- **macOS**: `mdsplit4gpt-macos-x86_64`
- **Windows**: `mdsplit4gpt-windows-x86_64.exe`

Make executable and add to PATH:
```bash
chmod +x mdsplit4gpt-linux-x86_64
mv mdsplit4gpt-linux-x86_64 ~/.local/bin/mdsplit4gpt
```

#### Option 3: Source Installation

```bash
git clone https://github.com/twardoch/split-python4gpt.git
cd split-python4gpt
./scripts/install-dev.sh
```

## Usage

### Command-Line Interface

Primary command: `mdsplit4gpt`

```bash
mdsplit4gpt [PATH_OR_FOLDER] [OPTIONS]
```

**Key Arguments:**

* `path_or_folder`: Input Python file or folder
* `--out`: Output folder for processed files (defaults to input folder)
* `--pyis`: Directory for `.pyi` files (defaults to output folder)
* `--types`: Infer types using PyType (default: True)
* `--mini`: Minify scripts (default: True)

**Minification Options:**
* `--mini_docs`: Remove docstrings
* `--mini_globs`: Rename global names (default: False)
* `--mini_locs`: Rename local names (default: False)
* `--mini_lits`: Hoist literal statements
* `--mini_annotations`: Remove annotations
* `--mini_asserts`: Remove asserts
* `--mini_debug`: Remove debugging statements
* `--mini_imports`: Combine imports
* `--mini_obj`: Remove object base
* `--mini_pass`: Remove pass statements
* `--mini_posargs`: Convert positional to keyword args
* `--mini_retnone`: Remove explicit return None
* `--mini_shebang`: Remove shebang (set to False to preserve)

**Examples:**

1. Process single file with minification and type inference:
    ```bash
    mdsplit4gpt my_script.py --out output_dir
    ```
    Creates `output_dir/my_script.py` and `output_dir/split4gpt/split1.py`.

2. Process project without type inference, preserving docstrings:
    ```bash
    mdsplit4gpt my_project/ --out processed_project/ --types=False --mini_docs=False
    ```

### Programmatic Usage

```python
from pathlib import Path
from split_python4gpt import PyLLMSplitter

# Set OPENAI_API_KEY environment variable for summarization
# os.environ["OPENAI_API_KEY"] = "your_api_key"

splitter = PyLLMSplitter(
    gptok_model="gpt-3.5-turbo",
    gptok_limit=4000,
    gptok_threshold=200
)

input_path = "path/to/your/python_project_or_file"
output_dir = "path/to/output_directory"
pyi_dir = "path/to/pyi_files_directory"

processed_file_paths = splitter.process_py(
    py_path_or_folder=input_path,
    out_py_folder=output_dir,
    pyi_folder=pyi_dir,
    types=True,
    mini=True,
    remove_literal_statements=True,
    rename_globals=False
)

splitter.write_splits()

print(f"Processed files: {processed_file_paths}")
print(f"LLM splits: {Path(output_dir) / 'split4gpt'}")
```

## Technical Details

### Workflow

1. **File Discovery:** Processes single files or recursively finds all `*.py` files in folders

2. **Initialization:** Resolves and creates input/output directories; copies files if needed

3. **Per-file Processing:**
    * **Type Inference:** Runs `pytype` subprocess, merges generated stubs back into source
    * **Minification:** Passes code through `python-minifier` with specified options

4. **LLM Preparation:**
    * Parses code into AST
    * Processes top-level nodes (imports, assignments, functions, classes)
    * For each function/class:
        * Calculates token count with `tiktoken`
        * If count exceeds threshold, replaces body with `...` and AI summary

5. **Splitting:**
    * Collects all processed sections
    * Accumulates sections into portions respecting token limits
    * Writes `splitN.py` files in `split4gpt` subdirectory

### Output Structure

* **Processed Files:** Minified/type-annotated versions in output directory (modifies in-place if no output specified)
* **`.pyi` Files:** Type stubs in specified directory (defaults to output)
* **`split4gpt` Directory:** Contains final chunks for LLM consumption

### Core Components

* **`PyTypingMinifier`:** Handles file management, type inference, and minification
* **`PyBodySummarizer`:** AST transformer that summarizes large functions/classes
* **`PyLLMSplitter`:** Inherits from `PyTypingMinifier`, adds token counting and splitting

## Contributing

### Development Setup

1. Fork repository
2. Create branch: `git checkout -b feature/your-feature-name`
3. Set up environment:
    ```bash
    ./scripts/install-dev.sh
    ```

### Development Workflow

4. Make changes
5. Run tests:
    ```bash
    ./scripts/build-and-test.sh
    ./scripts/build-and-test.sh --with-coverage
    ./scripts/build-and-test.sh --with-performance
    ```

6. Code standards:
    * Formatted with `black`
    * Imports sorted with `isort`
    * PEP 8 compliant
    * Linted with `flake8`
    * Pre-commit hooks run automatically

7. Add tests in `tests/` directory
8. Commit with descriptive message
9. Push branch: `git push origin feature/your-feature-name`
10. Create Pull Request

### Release Process

1. **Create release:**
   ```bash
   ./scripts/release.sh 1.2.3
   ```

2. **Automated CI/CD:**
   * Tests run on push/PR for Linux, macOS, Windows
   * Git tags trigger: PyPI publication, binary builds, GitHub releases

3. **Scripts:**
   * `install-dev.sh`: Development setup
   * `build-and-test.sh`: Testing
   * `release.sh`: Create releases
   * `get_version.py`: Check current version
   * `validate_tag.py`: Validate version format

## License

Apache License 2.0. See [LICENSE.txt](LICENSE.txt).

## Authors

* Adam Twardoch ([@twardoch](https://github.com/twardoch))

Scaffolded with [PyScaffold](https://pyscaffold.org/).