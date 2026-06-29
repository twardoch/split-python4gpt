# Installation

## Requirements

- Python 3.10 or later
- An OpenAI API key is **only** required for LLM summarisation (`--summarise`)

## Install from PyPI

```bash
pip install split-python4gpt
```

## Install optional extras

```bash
# Type inference via pytype (Linux/macOS, Python 3.10 recommended)
pip install "split-python4gpt[types]"

# LLM summarisation (tiktoken + simpleaichat)
pip install "split-python4gpt[llm]"

# Everything
pip install "split-python4gpt[types,llm]"
```

## Install from source

```bash
git clone https://github.com/twardoch/split-python4gpt
cd split-python4gpt
pip install -e ".[dev]"
```

## Verify

```bash
mdsplit4gpt --help
```
