from pathlib import Path

from .models import FileMetadata


def _lr(start: int, end: int) -> str:
    return f"{start}-{end}" if end != start else str(start)


def format_metadata(meta: FileMetadata) -> str:
    """Render FileMetadata as a compact, token-efficient text representation."""
    lines = [f"[{meta.language}] {meta.file_path}"]
    if meta.imports:
        lines.append("IMPORT " + ",".join(meta.imports))
    for cls in meta.classes:
        bases = f"({','.join(cls.bases)})" if cls.bases else ""
        lines.append(f"CLASS {cls.name}{bases}:{_lr(cls.line_start, cls.line_end)}")
        for m in cls.methods:
            lines.append(f"  {m.name}:{_lr(m.line_start, m.line_end)}")
    for fn in meta.functions:
        lines.append(f"FN {fn.name}:{_lr(fn.line_start, fn.line_end)}")
    return "\n".join(lines)


def write_metadata(meta: FileMetadata, output_dir: Path | None) -> Path:
    """Write the metadata for a file to a .meta file and return its path."""
    source_path = Path(meta.file_path)
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        out_path = output_dir / (source_path.name + ".meta")
    else:
        out_path = source_path.with_suffix(source_path.suffix + ".meta")
    out_path.write_text(format_metadata(meta), encoding="utf-8")
    return out_path
