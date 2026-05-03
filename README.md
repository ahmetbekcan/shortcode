# shortcode

> Extract compact structural maps from source code — designed to reduce LLM context usage.

[![CI](https://github.com/ahmetbekcan/shortcode/actions/workflows/ci.yml/badge.svg)](https://github.com/ahmetbekcan/shortcode/actions)
[![PyPI](https://img.shields.io/pypi/v/shortcode)](https://pypi.org/project/shortcode/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/shortcode)](https://pypi.org/project/shortcode/)

When working with an LLM on a large codebase, dumping entire source files into the context is expensive and slow. **shortcode** generates a `.meta` file for each source file — a one-line-per-symbol summary that tells the LLM *where* everything lives without wasting tokens on implementation details.

**Workflow:**
1. Run `shortcode ./src` once to generate `.meta` files
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

`shortcode` produces `auth.py.meta`:

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
pip install shortcode
# or
uv add shortcode
```

**No Python?** Download the pre-built Windows executable from [Releases](https://github.com/ahmetbekcan/shortcode/releases).

---

## CLI usage

```bash
# Scan a folder — writes .meta next to each source file
shortcode ./src

# Write all .meta files to a separate directory
shortcode ./src --output-dir ./meta

# Only process specific extensions
shortcode ./src --ext py ts java

# Top-level only (no subdirectories)
shortcode ./src --no-recursive
```

Double-clicking the `.exe` opens an interactive prompt asking for the folder path.

---

## Python API

```python
from shortcode import parse_file
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

shortcode ships an MCP server so Claude Code (and any MCP-compatible agent) can call it as a tool directly — no manual `.meta` file management needed.

### Install with MCP support

```bash
pip install "shortcode[mcp]"
# or
uv add "shortcode[mcp]"
```

### Register in Claude Code

Edit your Claude Code config file:

- **macOS/Linux:** `~/.claude.json`
- **Windows:** `C:\Users\<YourName>\.claude.json`

Add the `mcpServers` block:

```json
{
  "mcpServers": {
    "shortcode": {
      "command": "shortcode-mcp"
    }
  }
}
```

Or with `uvx` — no separate install needed, just requires [uv](https://docs.astral.sh/uv/getting-started/installation/):

```json
{
  "mcpServers": {
    "shortcode": {
      "command": "uvx",
      "args": ["--from", "shortcode[mcp]", "shortcode-mcp"]
    }
  }
}
```

**Restart Claude Code** after editing the config. Run `/mcp` to confirm the server is connected.

### Make Claude use it consistently (recommended)

Add a `CLAUDE.md` file to your project root:

```markdown
## Code navigation
A shortcode MCP server is available. Before reading any source file, call
`brief_file(path)` to get its structure and line ranges. Then read only
the specific lines you need using offset + limit.
```

This instructs Claude to use shortcode at the start of every session instead of reading full files.

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

> **Other MCP clients:** The same `shortcode-mcp` server works with Cursor, Windsurf, and any agent that supports the Model Context Protocol.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Adding support for a new language takes about 10 lines.

---

## License

MIT © [Ahmet Bekcan](https://github.com/ahmetbekcan)
