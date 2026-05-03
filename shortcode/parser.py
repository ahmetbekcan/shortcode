from pathlib import Path

from tree_sitter import Node, Query, QueryCursor

from .languages import EXT_TO_CONFIG, LangConfig
from .models import ClassInfo, FileMetadata, MethodInfo


def _text(node: Node) -> str:
    return node.text.decode("utf-8", errors="replace")


def _range(node: Node) -> tuple[int, int]:
    return node.start_point[0] + 1, node.end_point[0] + 1


def _strip_quotes(s: str) -> str:
    return s.strip("\"'<>")


# ── Tree walker ───────────────────────────────────────────────────────────────

def _walk(
    node: Node,
    config: LangConfig,
    classes: list[ClassInfo],
    functions: list[MethodInfo],
    current_class: ClassInfo | None = None,
    in_function: bool = False,
) -> None:
    if node.type in config.class_types and config.include_class(node):
        name = config.get_name(node)
        if name:
            start, end = _range(node)
            cls = ClassInfo(
                name=name,
                line_start=start,
                line_end=end,
                bases=config.get_bases(node),
            )
            classes.append(cls)
            for child in node.children:
                _walk(child, config, classes, functions, current_class=cls, in_function=False)
        return

    if node.type in config.function_types and config.include_function(node):
        if not in_function:
            name = config.get_name(node)
            if name:
                start, end = _range(node)
                m = MethodInfo(name=name, line_start=start, line_end=end)
                if current_class is not None:
                    current_class.methods.append(m)
                else:
                    functions.append(m)
        for child in node.children:
            _walk(child, config, classes, functions, current_class=current_class, in_function=True)
        return

    for child in node.children:
        _walk(child, config, classes, functions, current_class=current_class, in_function=in_function)


# ── Import extraction ─────────────────────────────────────────────────────────

def _extract_imports(tree, config: LangConfig) -> list[str]:
    if not config.import_query:
        return []
    try:
        query = Query(config.language(), config.import_query)
        captures = QueryCursor(query).captures(tree.root_node)
    except Exception:
        return []
    seen: set[str] = set()
    result: list[str] = []
    for nodes in captures.values():
        for node in nodes:
            text = _strip_quotes(_text(node).strip())
            if text and text not in seen:
                seen.add(text)
                result.append(text)
    return result


# ── Public API ────────────────────────────────────────────────────────────────

def parse_file(path: Path) -> FileMetadata | None:
    """Parse a source file and return its structural metadata, or None if unsupported."""
    config = EXT_TO_CONFIG.get(path.suffix.lower())
    if config is None:
        return None
    try:
        source = path.read_bytes()
    except OSError:
        return None

    tree = config.parser().parse(source)
    classes: list[ClassInfo] = []
    functions: list[MethodInfo] = []
    _walk(tree.root_node, config, classes, functions)
    imports = _extract_imports(tree, config)

    return FileMetadata(
        file_path=str(path),
        language=config.extensions[0].lstrip("."),
        classes=classes,
        functions=functions,
        imports=imports,
    )
