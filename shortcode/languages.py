
from tree_sitter import Language, Node, Parser


class LangConfig:
    def __init__(
        self,
        ts_module,
        extensions: list[str],
        class_types: list[str],
        function_types: list[str],
        import_query: str = "",
    ):
        self.ts_module = ts_module
        self.extensions = extensions
        self.class_types = frozenset(class_types)
        self.function_types = frozenset(function_types)
        self.import_query = import_query
        self._language: Language | None = None
        self._parser: Parser | None = None

    def language(self) -> Language:
        if self._language is None:
            self._language = Language(self.ts_module.language())
        return self._language

    def parser(self) -> Parser:
        if self._parser is None:
            self._parser = Parser(self.language())
        return self._parser

    def get_name(self, node: Node) -> str | None:
        child = node.child_by_field_name("name")
        return child.text.decode("utf-8", errors="replace") if child else None

    def get_bases(self, node: Node) -> list[str]:
        return []

    def include_class(self, node: Node) -> bool:
        return True

    def include_function(self, node: Node) -> bool:
        return True


# ── Per-language subclasses ───────────────────────────────────────────────────

class PythonConfig(LangConfig):
    def get_bases(self, node: Node) -> list[str]:
        args = node.child_by_field_name("superclasses")
        if args is None:
            return []
        return [
            c.text.decode("utf-8", errors="replace")
            for c in args.children
            if c.type == "identifier"
        ]


class GoConfig(LangConfig):
    def include_class(self, node: Node) -> bool:
        if node.type == "type_spec":
            t = node.child_by_field_name("type")
            return t is not None and t.type == "struct_type"
        return True


class RubyConfig(LangConfig):
    def get_name(self, node: Node) -> str | None:
        for child in node.children:
            if child.type in ("constant", "identifier", "scope_resolution"):
                return child.text.decode("utf-8", errors="replace")
        return None


# ── C++ helpers ───────────────────────────────────────────────────────────────

def _cpp_is_macro_class(node: Node) -> bool:
    """True when a function_definition is `class MACRO ClassName { }` misparsed by tree-sitter."""
    type_node = node.child_by_field_name("type")
    if type_node is None or type_node.type not in ("class_specifier", "struct_specifier"):
        return False
    decl = node.child_by_field_name("declarator")
    return decl is not None and decl.type == "identifier"


def _cpp_next_decl(node: Node) -> Node | None:
    """Step down one level in a declarator chain, falling back to first named child
    when there is no named 'declarator' field (e.g. reference_declarator)."""
    inner = node.child_by_field_name("declarator")
    if inner is None:
        inner = next((c for c in node.named_children if c.type != "&"), None)
    return inner


def _cpp_has_declarator_fn(node: Node) -> bool:
    """True if the declarator chain of node leads to a function_declarator."""
    decl = node.child_by_field_name("declarator")
    while decl and decl.type in ("pointer_declarator", "reference_declarator"):
        decl = _cpp_next_decl(decl)
    return decl is not None and decl.type == "function_declarator"


def _cpp_fn_name(node: Node) -> str | None:
    decl = node.child_by_field_name("declarator")
    while decl is not None and decl.type in (
        "pointer_declarator",
        "reference_declarator",
        "abstract_reference_declarator",
    ):
        decl = _cpp_next_decl(decl)
    if decl is None:
        return None
    if decl.type == "function_declarator":
        inner = decl.child_by_field_name("declarator")
        if inner:
            raw = inner.text.decode("utf-8", errors="replace").split("(")[0].strip()
            return raw.split("::")[-1] or None
    elif decl.type == "identifier":
        return decl.text.decode("utf-8", errors="replace")
    return None


class CppConfig(LangConfig):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.function_types = frozenset([
            "function_definition",
            "declaration",        # declarations inside macro-class compound bodies
            "field_declaration",  # declarations inside regular class field_declaration_list
        ])
        self.class_types = frozenset([
            "class_specifier",
            "struct_specifier",
            "function_definition",  # macro-class misparse: class MACRO Name { }
        ])

    def include_class(self, node: Node) -> bool:
        if node.type == "function_definition":
            return _cpp_is_macro_class(node)
        return any(c.type == "field_declaration_list" for c in node.children)

    def include_function(self, node: Node) -> bool:
        if node.type == "function_definition":
            return not _cpp_is_macro_class(node)
        if node.type in ("declaration", "field_declaration"):
            return _cpp_has_declarator_fn(node)
        return True

    def get_name(self, node: Node) -> str | None:
        if node.type in ("class_specifier", "struct_specifier"):
            child = node.child_by_field_name("name")
            return child.text.decode("utf-8", errors="replace") if child else None
        if node.type == "function_definition" and _cpp_is_macro_class(node):
            decl = node.child_by_field_name("declarator")
            return decl.text.decode("utf-8", errors="replace") if decl else None
        return _cpp_fn_name(node)


# ── Config registry ───────────────────────────────────────────────────────────

def _make_configs() -> list[LangConfig]:
    import tree_sitter_c_sharp as ts_cs
    import tree_sitter_cpp as ts_cpp
    import tree_sitter_go as ts_go
    import tree_sitter_java as ts_java
    import tree_sitter_javascript as ts_js
    import tree_sitter_php as ts_php
    import tree_sitter_python as ts_py
    import tree_sitter_ruby as ts_rb
    import tree_sitter_rust as ts_rs
    import tree_sitter_typescript as ts_ts

    return [
        PythonConfig(
            ts_module=ts_py,
            extensions=[".py"],
            class_types=["class_definition"],
            function_types=["function_definition"],
            import_query="""
                (import_statement (dotted_name) @name)
                (import_from_statement module_name: (dotted_name) @name)
            """,
        ),
        LangConfig(
            ts_module=ts_js,
            extensions=[".js", ".mjs", ".cjs"],
            class_types=["class_declaration"],
            function_types=["function_declaration", "method_definition"],
            import_query="(import_statement source: (string (string_fragment) @name))",
        ),
        LangConfig(
            ts_module=ts_ts.language_typescript(),
            extensions=[".ts"],
            class_types=["class_declaration"],
            function_types=["function_declaration", "method_definition"],
            import_query="(import_statement source: (string (string_fragment) @name))",
        ),
        LangConfig(
            ts_module=ts_ts.language_tsx(),
            extensions=[".tsx"],
            class_types=["class_declaration"],
            function_types=["function_declaration", "method_definition"],
            import_query="(import_statement source: (string (string_fragment) @name))",
        ),
        LangConfig(
            ts_module=ts_java,
            extensions=[".java"],
            class_types=["class_declaration", "interface_declaration", "enum_declaration"],
            function_types=["method_declaration", "constructor_declaration"],
            import_query="(import_declaration (scoped_identifier) @name)",
        ),
        LangConfig(
            ts_module=ts_cs,
            extensions=[".cs"],
            class_types=[
                "class_declaration",
                "interface_declaration",
                "struct_declaration",
                "record_declaration",
            ],
            function_types=["method_declaration", "constructor_declaration"],
            import_query="(using_directive (qualified_name) @name)",
        ),
        CppConfig(
            ts_module=ts_cpp,
            extensions=[".cpp", ".cc", ".cxx", ".hpp", ".h"],
            class_types=[],
            function_types=[],
            import_query="(preproc_include path: [(string_literal) (system_lib_string)] @name)",
        ),
        GoConfig(
            ts_module=ts_go,
            extensions=[".go"],
            class_types=["type_spec"],
            function_types=["function_declaration", "method_declaration"],
            import_query="(import_spec path: (interpreted_string_literal) @name)",
        ),
        LangConfig(
            ts_module=ts_rs,
            extensions=[".rs"],
            class_types=["struct_item", "enum_item", "trait_item", "impl_item"],
            function_types=["function_item"],
            import_query="(use_declaration argument: (_) @name)",
        ),
        RubyConfig(
            ts_module=ts_rb,
            extensions=[".rb"],
            class_types=["class", "module"],
            function_types=["method", "singleton_method"],
            import_query="",
        ),
        LangConfig(
            ts_module=ts_php,
            extensions=[".php"],
            class_types=["class_declaration", "interface_declaration", "trait_declaration"],
            function_types=["method_declaration", "function_definition"],
            import_query="",
        ),
    ]


def _build_ext_map() -> dict[str, LangConfig]:
    configs = _make_configs()
    # TypeScript passes a Language capsule rather than a module object — initialise directly.
    for cfg in configs:
        if cfg.extensions[0] in (".ts", ".tsx"):
            capsule = cfg.ts_module
            cfg.ts_module = None
            cfg._language = Language(capsule)
            cfg._parser = Parser(cfg._language)
    ext_map: dict[str, LangConfig] = {}
    for cfg in configs:
        for ext in cfg.extensions:
            ext_map[ext] = cfg
    return ext_map


EXT_TO_CONFIG: dict[str, LangConfig] = _build_ext_map()
