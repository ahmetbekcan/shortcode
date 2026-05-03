"""
shortcode — Extract compact structural maps from source code to save LLM tokens.

Quick start:
    from shortcode import parse_file
    from pathlib import Path

    meta = parse_file(Path("src/auth.py"))
    print(meta.classes)    # list of ClassInfo
    print(meta.functions)  # list of MethodInfo
"""

from .models import ClassInfo, FileMetadata, MethodInfo
from .parser import parse_file

__all__ = ["parse_file", "FileMetadata", "ClassInfo", "MethodInfo"]
__version__ = "0.1.0"
