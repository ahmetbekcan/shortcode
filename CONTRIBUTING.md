# Contributing to codebrief

Thank you for helping make codebrief better!

## Development setup

```bash
git clone https://github.com/ahmetbekcan/codebrief.git
cd codebrief
uv sync --dev
```

## Running tests

```bash
uv run pytest tests/ -v
```

## Linting

```bash
uv run ruff check codebrief tests
uv run ruff format codebrief tests
```

## Adding a new language

All language configurations live in `codebrief/languages.py`. Adding a new language takes about 10 lines:

**1. Install the tree-sitter binding:**
```bash
uv add tree-sitter-<lang>
```

**2. Add a `LangConfig` entry inside `_make_configs()`:**
```python
import tree_sitter_mylang as ts_ml

LangConfig(
    ts_module=ts_ml,
    extensions=[".ml"],
    class_types=["class_definition"],        # node types for classes
    function_types=["function_definition"],  # node types for methods/functions
    import_query="(import_statement ...) @name",
),
```

To find the correct node type names for a language, use the [tree-sitter playground](https://tree-sitter.github.io/tree-sitter/playground) or run:
```python
import tree_sitter_mylang as ts_ml
from tree_sitter import Language, Parser
parser = Parser(Language(ts_ml.language()))
tree = parser.parse(b"your source code here")
print(tree.root_node.sexp())
```

**3. Add a fixture and test:**
- Add a small sample file to `tests/fixtures/sample.ml`
- Add test cases to `tests/test_parser.py`
- Update the language table in `README.md`

## Pull request checklist

- [ ] `uv run pytest tests/ -v` passes
- [ ] `uv run ruff check codebrief tests` passes
- [ ] New language? Add fixture, tests, and update `README.md`
- [ ] New feature? Update docstrings and `README.md` if user-facing
