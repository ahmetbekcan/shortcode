"""MCP server that exposes shortcode as tools for AI coding agents.

Supported clients: Claude Code, Cursor, Windsurf, and any MCP-compatible agent.

Usage
-----
Start the server (stdio transport, used by most MCP clients):

    shortcode-mcp

Then register it in your agent's MCP config, e.g. Claude Code (~/.claude.json):

    {
      "mcpServers": {
        "shortcode": {
          "command": "shortcode-mcp"
        }
      }
    }

Tools exposed
-------------
- scan_folder  : scan a directory and return structural maps for all source files
- brief_file   : return the structural map of a single source file
"""

from __future__ import annotations

from pathlib import Path

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:
    raise ImportError(
        "The MCP server requires the 'mcp' extra.\n"
        "Install it with: pip install shortcode[mcp]"
    ) from exc

from shortcode.formatter import format_metadata
from shortcode.languages import EXT_TO_CONFIG
from shortcode.parser import parse_file

mcp = FastMCP(
    "shortcode",
    instructions=(
        "Use shortcode tools to understand a codebase's structure before reading files. "
        "Call scan_folder first to get a token-efficient map showing every class, method, "
        "and function with its line range. Then read only the specific lines you need."
    ),
)


@mcp.tool()
def scan_folder(
    path: str,
    extensions: list[str] | None = None,
    recursive: bool = True,
) -> str:
    """Scan a source folder and return compact structural maps for all supported files.

    Returns one block per file showing language, imports, classes (with methods),
    and top-level functions — all with line numbers. Read this before opening any
    source file to avoid wasting tokens on code you don't need.

    Args:
        path: Absolute or relative path to the folder to scan.
        extensions: Optional list of file extensions to include, e.g. ["py", "ts"].
                    Scans all supported languages when omitted.
        recursive: Whether to recurse into subdirectories (default True).
    """
    root = Path(path).resolve()
    if not root.is_dir():
        return f"Error: '{path}' is not a directory."

    allowed = (
        {e if e.startswith(".") else f".{e}" for e in extensions}
        if extensions
        else None
    )
    pattern = "**/*" if recursive else "*"

    results: list[str] = []
    for file_path in sorted(p for p in root.glob(pattern) if p.is_file()):
        ext = file_path.suffix.lower()
        if allowed and ext not in allowed:
            continue
        if ext not in EXT_TO_CONFIG:
            continue
        meta = parse_file(file_path)
        if meta:
            results.append(format_metadata(meta))

    if not results:
        return "No supported source files found."
    return "\n\n".join(results)


@mcp.tool()
def brief_file(path: str) -> str:
    """Return the compact structural map of a single source file.

    Shows language, imports, classes (with methods), and top-level functions,
    all with line numbers. Use this to understand a file's structure before
    deciding which lines to read.

    Args:
        path: Absolute or relative path to the source file.
    """
    file_path = Path(path).resolve()
    meta = parse_file(file_path)
    if meta is None:
        suffix = file_path.suffix.lower()
        if suffix not in EXT_TO_CONFIG:
            return f"Error: '{suffix}' is not a supported file type."
        return f"Error: Could not read '{path}'."
    return format_metadata(meta)


def serve() -> None:
    """Entry point: start the shortcode MCP server over stdio."""
    mcp.run()
