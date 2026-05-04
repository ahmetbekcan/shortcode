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

_COMPACT_THRESHOLD = 0.3  # return full file if compact saves less than 30%

mcp = FastMCP(
    "shortcode",
    instructions=(
        "Before reading any source file, call compact_file(path). "
        "It returns either a compact structural map with line ranges (read only the lines you need) "
        "or the full file content when the file is too small to benefit from compaction."
    ),
)


@mcp.tool()
def compact_file(path: str) -> str:
    """Return a token-efficient view of a source file.

    If the file is large enough to benefit from compaction, returns a structural
    map (imports, classes, methods, functions with line ranges) so you can read
    only the specific lines you need. Otherwise returns the full file content
    to avoid a wasted round trip.

    The response is prefixed with [COMPACT] or [FULL] so you know which was returned.

    Args:
        path: Absolute or relative path to the source file.
    """
    file_path = Path(path).resolve()

    try:
        original = file_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return f"Error: Could not read '{path}'."

    meta = parse_file(file_path)
    if meta is None:
        suffix = file_path.suffix.lower()
        if suffix not in EXT_TO_CONFIG:
            return f"Error: '{suffix}' is not a supported file type."
        return f"[FULL]\n{original}"

    compact = format_metadata(meta)
    savings = len(original) - len(compact)

    if savings < len(original) * _COMPACT_THRESHOLD:
        return f"[FULL]\n{original}"
    return f"[COMPACT]\n{compact}"


def serve() -> None:
    mcp.run()
