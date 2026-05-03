from dataclasses import dataclass, field


@dataclass
class MethodInfo:
    name: str
    line_start: int
    line_end: int


@dataclass
class ClassInfo:
    name: str
    line_start: int
    line_end: int
    bases: list[str] = field(default_factory=list)
    methods: list[MethodInfo] = field(default_factory=list)


@dataclass
class FileMetadata:
    file_path: str
    language: str
    classes: list[ClassInfo] = field(default_factory=list)
    functions: list[MethodInfo] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
