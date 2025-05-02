# ALTR Python package

Python code snippet written by ALTR

## Run unit tests

```bash
uv run pytest
```

## Installation

```bash
uv add "altr @ git+https://github.com/chuan-khuna/altr" --tag 0.1.0
```

`pyproject.toml` will look like this:

```toml
[project]
dependencies = [
    "altr"
]

[tool.uv.sources]
altr = { git = "https://github.com/chuan-khuna/altr", tag = "0.1.0" }
```
