# split-python4gpt

**split-python4gpt** processes and reorganises large Python projects into
minified, type-annotated, token-bounded files ready for analysis by Large
Language Models (LLMs) such as OpenAI GPT-4.

## What it does

Given a Python file or directory tree, the tool:

1. **Minifies** each `.py` file — removes docstrings, `pass`, annotations,
   debug statements and more via
   [`python-minifier`](https://github.com/dflook/python-minifier).
2. **Infers types** (optional) — runs `pytype` on each file and merges the
   generated `.pyi` stubs back into the source.
3. **Splits for LLMs** — counts tokens with `tiktoken` and writes
   `split4gpt/split1.py`, `split2.py` … so that each file fits within the
   chosen model's context window.
4. **Summarises large blocks** (optional) — replaces functions/classes that
   exceed the token threshold with `...` stubs and an AI-generated one-liner
   (requires an OpenAI API key).

## Quick start

```bash
pip install split-python4gpt
mdsplit4gpt path/to/myproject --out path/to/output --types=False
```

The `split4gpt/` sub-folder inside the output directory will contain numbered
Python files sized to fit the target model.

## Features at a glance

| Feature | Flag | Default |
|---|---|---|
| Type inference via pytype | `--types` | `True` |
| Minification | `--mini` | `True` |
| Remove docstrings | `--mini_docs` | `True` |
| Remove type annotations | `--mini_annotations` | `True` |
| Remove asserts | `--mini_asserts` | `True` |
| Rename globals | `--mini_globs` | `False` |
| Rename locals | `--mini_locs` | `False` |

See [Usage](usage.md) for the full flag reference.
