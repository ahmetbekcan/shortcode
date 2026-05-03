from pathlib import Path

from shortcode import parse_file

FIXTURES = Path(__file__).parent / "fixtures"


# ── Python ────────────────────────────────────────────────────────────────────

def test_python_classes():
    meta = parse_file(FIXTURES / "sample.py")
    assert meta is not None
    names = [c.name for c in meta.classes]
    assert "Animal" in names
    assert "Dog" in names


def test_python_bases():
    meta = parse_file(FIXTURES / "sample.py")
    assert meta is not None
    dog = next(c for c in meta.classes if c.name == "Dog")
    assert "Animal" in dog.bases


def test_python_methods():
    meta = parse_file(FIXTURES / "sample.py")
    assert meta is not None
    dog = next(c for c in meta.classes if c.name == "Dog")
    method_names = [m.name for m in dog.methods]
    assert "speak" in method_names
    assert "fetch" in method_names


def test_python_functions():
    meta = parse_file(FIXTURES / "sample.py")
    assert meta is not None
    fn_names = [f.name for f in meta.functions]
    assert "greet" in fn_names
    assert "add" in fn_names


def test_python_imports():
    meta = parse_file(FIXTURES / "sample.py")
    assert meta is not None
    assert "os" in meta.imports


def test_python_line_numbers():
    meta = parse_file(FIXTURES / "sample.py")
    assert meta is not None
    animal = next(c for c in meta.classes if c.name == "Animal")
    assert animal.line_start > 0
    assert animal.line_end >= animal.line_start


# ── JavaScript ────────────────────────────────────────────────────────────────

def test_javascript_classes():
    meta = parse_file(FIXTURES / "sample.js")
    assert meta is not None
    names = [c.name for c in meta.classes]
    assert "Animal" in names
    assert "Dog" in names


def test_javascript_methods():
    meta = parse_file(FIXTURES / "sample.js")
    assert meta is not None
    animal = next(c for c in meta.classes if c.name == "Animal")
    method_names = [m.name for m in animal.methods]
    assert "speak" in method_names


def test_javascript_imports():
    meta = parse_file(FIXTURES / "sample.js")
    assert meta is not None
    assert "fs" in meta.imports


# ── Java ──────────────────────────────────────────────────────────────────────

def test_java_classes():
    meta = parse_file(FIXTURES / "sample.java")
    assert meta is not None
    names = [c.name for c in meta.classes]
    assert "Animal" in names
    assert "Dog" in names


def test_java_methods():
    meta = parse_file(FIXTURES / "sample.java")
    assert meta is not None
    animal = next(c for c in meta.classes if c.name == "Animal")
    method_names = [m.name for m in animal.methods]
    assert "speak" in method_names
    assert "getName" in method_names


def test_java_imports():
    meta = parse_file(FIXTURES / "sample.java")
    assert meta is not None
    assert any("List" in imp for imp in meta.imports)


# ── C++ ───────────────────────────────────────────────────────────────────────

def test_cpp_regular_class():
    meta = parse_file(FIXTURES / "sample.cpp")
    assert meta is not None
    names = [c.name for c in meta.classes]
    assert "Animal" in names


def test_cpp_macro_class_name():
    meta = parse_file(FIXTURES / "sample.cpp")
    assert meta is not None
    names = [c.name for c in meta.classes]
    # The DLL-export macro must NOT be the class name
    assert "MY_API" not in names
    assert "Log" in names


def test_cpp_macro_class_methods():
    meta = parse_file(FIXTURES / "sample.cpp")
    assert meta is not None
    log = next(c for c in meta.classes if c.name == "Log")
    method_names = [m.name for m in log.methods]
    assert "Init" in method_names
    assert "Shutdown" in method_names
    assert "GetInstance" in method_names
    assert "Write" in method_names


# ── Go ────────────────────────────────────────────────────────────────────────

def test_go_structs():
    meta = parse_file(FIXTURES / "sample.go")
    assert meta is not None
    names = [c.name for c in meta.classes]
    assert "Animal" in names
    assert "Dog" in names


def test_go_functions():
    meta = parse_file(FIXTURES / "sample.go")
    assert meta is not None
    fn_names = [f.name for f in meta.functions]
    assert "Greet" in fn_names


def test_go_imports():
    meta = parse_file(FIXTURES / "sample.go")
    assert meta is not None
    assert "fmt" in meta.imports


# ── Edge cases ────────────────────────────────────────────────────────────────

def test_unsupported_extension_returns_none():
    meta = parse_file(Path("file.xyz"))
    assert meta is None


def test_nonexistent_file_returns_none():
    meta = parse_file(Path("nonexistent.py"))
    assert meta is None
