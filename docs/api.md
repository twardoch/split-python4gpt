# API Reference

## `split_python4gpt.minifier`

### `PyTypingMinifier`

Core class.  Reads Python files, optionally infers types with `pytype`, and
minifies them with `python-minifier`.

```python
class PyTypingMinifier(py_ver="3.10")
```

**Constructor parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `py_ver` | `str` | `"3.10"` | Python version string passed to pytype |

**Key methods**

| Method | Returns | Description |
|---|---|---|
| `process_py(path, out_py_folder, pyi_folder, types, mini, **opts)` | `list[Path]` | Main entry point — process one file or a whole directory |
| `minify(py_code, **opts)` | `str` | Minify a source string |
| `infer_types(py_path, pyi_path, py_code)` | `str` | Run pytype and merge stubs |

---

### `PyLLMSplitter`

Extends `PyTypingMinifier` with token counting and LLM-based summarisation.
Requires the `llm` extras (`tiktoken`, `simpleaichat`).

```python
class PyLLMSplitter(
    *args,
    gptok_model="gpt-3.5-turbo",
    gptok_limit=None,
    gptok_threshold=128,
    **kwargs,
)
```

**Constructor parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `gptok_model` | `str` | `"gpt-3.5-turbo"` | OpenAI model for token counting |
| `gptok_limit` | `int \| None` | model context window | Max tokens per split file |
| `gptok_threshold` | `int` | `128` | Token size above which a block gets stubbed |

**Key methods**

| Method | Returns | Description |
|---|---|---|
| `write_splits()` | `None` | Write `split4gpt/split*.py` to the output folder |
| `gptok_size(text)` | `int` | Count tokens (or estimate if tiktoken unavailable) |
| `process_py_code(py_code)` | `list[dict]` | Split source into token-bounded sections |

---

### `PyBodySummarizer`

Internal AST `NodeTransformer` used by `PyLLMSplitter`.  Replaces oversized
function/class bodies with `...` stubs and (optionally) an AI summary string.
Not intended for direct use.
