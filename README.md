# ALTR Python package

Python code snippet written by ALTR

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

## Development

### Run unit tests

```bash
uv run pytest
```

### tagging

```bash
git tag <tag_name>
git push origin <branch_name> --tags

# delete tag
git tag -d <tag_name>
```
