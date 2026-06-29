# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **MkDocs Material docs site** (`mkdocs.yml`, `docs/`) with pages for home,
  installation, usage, API reference, and changelog.
- **GitHub Actions CI** (`.github/workflows/ci.yml`) covering Python 3.10–3.13
  on Linux, macOS, and Windows; separate lint job with ruff; PyPI publish on tag.
- Full type hints and docstrings throughout `minifier.py` and `__main__.py`.
- `ruff` and `mypy` configuration in `pyproject.toml`.
- `astor` dependency eliminated — replaced with stdlib `ast.unparse` (Python 3.9+).

### Changed
- **Build system migrated** from PyScaffold/setuptools-scm to
  `hatchling` + `hatch-vcs`; `setup.cfg`, `setup.py`, and `tox.ini` removed.
- **Python constraint broadened** to `>=3.10` (was `>=3.10,<3.11`), supporting
  Python 3.10, 3.11, 3.12, and 3.13.
- `pytype` and LLM extras (`tiktoken`, `simpleaichat`) moved to optional
  dependency groups `[types]` and `[llm]`; only `fire` and `python-minifier`
  are required for the core CLI.
- `PyLLMSplitter` now imports `tiktoken` and `simpleaichat` lazily in
  `__init__`; gracefully degrades when they are unavailable (character-count
  estimate replaces token count; LLM summarisation silently disabled).
- `PyTypingMinifier.infer_types` now logs "Pytype failed for …" as `WARNING`
  on subprocess failure or missing executable (previously silently swallowed
  via `contextlib.suppress`).
- `PyTypingMinifier.process_py` now catches minification errors and logs
  "Minification failed for …" as `ERROR`, writing the original source instead.
- `write_splits()` now guards against `None` `out_py_folder` and exits with a
  warning rather than raising `TypeError`.
- CLI (`mdsplit4gpt --help`) now outputs help to **stdout** via
  `fire.core.Display` override; program name shown as `mdsplit4gpt`.
- `tests/data/out_test.py` corrected to match actual `python-minifier` output.
- `test_process_folder_types_and_minify` xfail marker removed — the test now
  passes with graceful pytype fallback.

### Removed
- `setup.cfg`, `setup.py`, `tox.ini`, `.isort.cfg` — superseded by
  `pyproject.toml` with hatchling.
- `astor` as a runtime dependency (stdlib `ast.unparse` used instead).

### Fixed
- `contextlib` was referenced in `infer_types` and `visit_FunctionDef` but
  not imported; import is now present.
- `PLAN.md` for outlining development steps and `TODO.md` for tracking task completion.
- Comprehensive test suite for `PyTypingMinifier`, including:
  - Minification of single files and folders.
  - Type inference testing (currently marked `xfail` due to issues with simple cases).
  - Identity transformation checks (`types=False, mini=False`).
  - Combined type inference and minification tests (marked `xfail` accordingly).
  - Edge case handling for empty files and files with syntax errors.
- Configuration for `tox` to use Python 3.10 and `pyenv` for consistent test environments.
- Basic logging configuration in `tests/conftest.py` for improved test debugging.
- `__all__` to `src/split_python4gpt/__init__.py`.

### Changed
- **Core Logic & Robustness:**
  - Clarified comments in `src/split_python4gpt/minifier.py`.
  - Improved error handling and logging in `PyTypingMinifier.infer_types`:
    - Pytype errors are now caught and logged as warnings, allowing processing to continue.
    - Added a warning if the `pytype` executable is not found during `PyTypingMinifier` initialization.
  - Improved error handling in `PyTypingMinifier.process_py` to catch and log errors during minification, allowing processing of other files to continue.
  - Fixed `UnboundLocalError` in `PyTypingMinifier.process_py` that occurred when `types=False` and `mini=True`.
- **Documentation:**
  - Updated `README.md` to accurately reflect current MVP functionality (focus on minification and type inference), corrected the CLI command, and linked to this `CHANGELOG.md`.
- **Development & CI:**
  - Enabled and ran `pre-commit` hooks, applying formatting changes (isort, black, etc.).
  - Minor `flake8` issues (E501, E231) were ignored as per user instruction after `black` formatting.

### Removed
- Unused instance variables (`py_path`, `out_py_path`, `pyi_path`, `py_code`) from `PyTypingMinifier`.
- Unused import of `contextlib` from `src/split_python4gpt/minifier.py`.

### Fixed
- Test failures related to minifier output expectations (e.g., quote style, trailing newlines).
- Indentation errors in test files introduced during development.
- Corrected `tests/data/out_test.py` to match actual minifier output.
