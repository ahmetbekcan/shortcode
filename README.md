# codebrief

> Extract compact structural maps from source code — designed to reduce LLM context usage.

[![CI](https://github.com/ahmetbekcan/codebrief/actions/workflows/ci.yml/badge.svg)](https://github.com/ahmetbekcan/codebrief/actions)
[![PyPI](https://img.shields.io/pypi/v/codebrief)](https://pypi.org/project/codebrief/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/codebrief)](https://pypi.org/project/codebrief/)

When working with an LLM on a large codebase, dumping entire source files into the context is expensive and slow. **codebrief** generates a `.meta` file for each source file — a one-line-per-symbol summary that tells the LLM *where* everything lives without wasting tokens on implementation details.

**Workflow:**
1. Run `codebrief ./src` once to generate `.meta` files
2. Feed the LLM the relevant `.meta` files (tiny)
3. Ask it to read only the specific functions it needs
4. The LLM reads targeted line ranges from the originals

---

## What it looks like

Given `auth.py`:

```python
class TokenManager:
    def __init__(self, secret): ...
    def generate(self, user_id): ...
    def verify(self, token): ...
```

`codebrief` produces `auth.py.meta`:

```
[py] src/auth.py
IMPORT flask,jwt,datetime
CLASS TokenManager:4-52
  __init__:5-9
  generate:11-24
  verify:26-38
FN hash_password:54-61
FN check_password:63-70
```

~15 tokens instead of ~400. The LLM asks to see lines 11-24 when it needs `generate`.

---

## Supported languages

| Language       | Extensions                          |
|----------------|-------------------------------------|
| Python         | `.py`                               |
| JavaScript     | `.js` `.mjs` `.cjs`                 |
| TypeScript     | `.ts` `.tsx`                        |
| Java           | `.java`                             |
| C#             | `.cs`                               |
| C / C++        | `.cpp` `.cc` `.cxx` `.hpp` `.h`     |
| Go             | `.go`                               |
| Rust           | `.rs`                               |
| Ruby           | `.rb`                               |
| PHP            | `.php`                              |

Powered by [tree-sitter](https://tree-sitter.github.io) — real AST parsing, no regex heuristics.

---

## Installation

```bash
pip install codebrief
# or
uv add codebrief
```

**No Python?** Download the pre-built Windows executable from [Releases](https://github.com/ahmetbekcan/codebrief/releases).

---

## CLI usage

```bash
# Scan a folder — writes .meta next to each source file
codebrief ./src

# Write all .meta files to a separate directory
codebrief ./src --output-dir ./meta

# Only process specific extensions
codebrief ./src --ext py ts java

# Top-level only (no subdirectories)
codebrief ./src --no-recursive
```

Double-clicking the `.exe` opens an interactive prompt asking for the folder path.

---

## Python API

```python
from codebrief import parse_file
from pathlib import Path

meta = parse_file(Path("src/auth.py"))

print(meta.language)          # "py"
print(meta.imports)           # ["flask", "jwt", "datetime"]

for cls in meta.classes:
    print(cls.name, cls.line_start, cls.line_end)
    for method in cls.methods:
        print("  ", method.name, method.line_start)

for fn in meta.functions:
    print(fn.name, fn.line_start)
```

---

## Claude Code integration (MCP)

codebrief ships an MCP server so Claude Code (and any MCP-compatible agent) can call it as a tool directly — no manual `.meta` file management needed.

### Install with MCP support

```bash
pip install "codebrief[mcp]"
# or
uv add "codebrief[mcp]"
```

### Register in Claude Code

Add to your `~/.claude.json` (global) or `.claude/settings.json` (project):

```json
{
  "mcpServers": {
    "codebrief": {
      "command": "codebrief-mcp"
    }
  }
}
```

Or with `uvx` (no install needed):

```json
{
  "mcpServers": {
    "codebrief": {
      "command": "uvx",
      "args": ["--from", "codebrief[mcp]", "codebrief-mcp"]
    }
  }
}
```

### Available tools

| Tool | Description |
|---|---|
| `scan_folder(path, extensions?, recursive?)` | Scan a folder and return structural maps for all source files |
| `brief_file(path)` | Return the structural map of a single source file |

### Example session

```
You:   scan my src/ folder

Claude: [calls scan_folder("src/")]

       [py] src/auth.py
       IMPORT flask,jwt,datetime
       CLASS TokenManager:12-87
         __init__:13-18
         generate:20-35
         verify:37-52

       [py] src/models.py
       CLASS User:4-31
         ...

You:   show me the generate method

Claude: [reads src/auth.py lines 20-35]
```

> **Other MCP clients:** The same `codebrief-mcp` server works with Cursor, Windsurf, and any agent that supports the Model Context Protocol.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Adding support for a new language takes about 10 lines.

---

## License

MIT © [Ahmet Bekcan](https://github.com/ahmetbekcan)
