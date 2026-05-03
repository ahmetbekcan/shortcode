import argparse
import sys
from pathlib import Path

from .formatter import write_metadata
from .languages import EXT_TO_CONFIG
from .parser import parse_file


def main() -> None:
    interactive = len(sys.argv) == 1

    if interactive:
        print("=== shortcode ===\n")
        folder_input = input("Folder to scan: ").strip().strip('"')
        if not folder_input:
            input("\nNo folder entered. Press Enter to exit.")
            return
        output_input = input(
            "Output folder (leave blank to write next to source files): "
        ).strip().strip('"')
        sys.argv += [folder_input]
        if output_input:
            sys.argv += ["--output-dir", output_input]

    ap = argparse.ArgumentParser(
        prog="shortcode",
        description="Extract compact structural maps from source code to save LLM tokens.",
    )
    ap.add_argument("folder", help="Root folder to scan")
    ap.add_argument("--output-dir", "-o", help="Write all .meta files here")
    ap.add_argument("--ext", nargs="+", metavar="EXT", help="Only process these extensions (e.g. py ts)")
    ap.add_argument(
        "--no-recursive",
        dest="recursive",
        action="store_false",
        default=True,
        help="Do not recurse into subdirectories",
    )
    args = ap.parse_args()

    root = Path(args.folder).resolve()
    if not root.is_dir():
        msg = f"Not a directory: {root}"
        if interactive:
            input(f"\nError: {msg}\nPress Enter to exit.")
            return
        raise SystemExit(msg)

    output_dir = Path(args.output_dir).resolve() if args.output_dir else None
    allowed = (
        {e if e.startswith(".") else f".{e}" for e in args.ext} if args.ext else None
    )
    pattern = "**/*" if args.recursive else "*"

    if interactive:
        print()

    processed = skipped = 0
    for path in sorted(p for p in root.glob(pattern) if p.is_file()):
        ext = path.suffix.lower()
        if allowed and ext not in allowed:
            continue
        if ext not in EXT_TO_CONFIG:
            skipped += 1
            continue
        meta = parse_file(path)
        if meta is None:
            skipped += 1
            continue
        out = write_metadata(meta, output_dir)
        rel = path.relative_to(root)
        nc = len(meta.classes)
        nm = sum(len(c.methods) for c in meta.classes)
        nf = len(meta.functions)
        print(f"  {rel} -> {out.name}  [{nc} classes, {nm} methods, {nf} fns]")
        processed += 1

    print(f"\nDone. {processed} processed, {skipped} skipped.")

    if interactive:
        input("\nPress Enter to exit.")


if __name__ == "__main__":
    main()
