#!/usr/bin/env python3
"""Normalize SVG icons to a centered square canvas."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from lib.normalize import NormalizeOptions, normalize_svg

REPO_ROOT = SCRIPTS_DIR.parent


def process_directory(
    icons_dir: Path,
    options: NormalizeOptions,
    *,
    dry_run: bool = False,
) -> list[Path]:
    processed: list[Path] = []

    for svg_path in sorted(icons_dir.glob("*.svg")):
        original = svg_path.read_text(encoding="utf-8")
        normalized = normalize_svg(original, options)

        if dry_run:
            print(f"[dry-run] would normalize {svg_path.name}")
        else:
            svg_path.write_text(normalized, encoding="utf-8")
            print(f"normalized {svg_path.name}")

        processed.append(svg_path)

    return processed


def build_parser() -> argparse.ArgumentParser:
    default_input = REPO_ROOT / "src" / "icons"

    parser = argparse.ArgumentParser(
        description="Normalize SVG icons in place to a centered square canvas.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=default_input,
        help=f"Directory containing SVG files (default: {default_input})",
    )
    parser.add_argument(
        "--size",
        type=int,
        default=64,
        help="Output canvas size in pixels (default: 64)",
    )
    parser.add_argument(
        "--padding",
        type=int,
        default=4,
        help="Padding around the icon inside the canvas (default: 4)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without writing files",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    options = NormalizeOptions(target_size=args.size, padding=args.padding)

    if not args.input.is_dir():
        print(f"Missing icons directory: {args.input}", file=sys.stderr)
        return 1

    svg_files = sorted(args.input.glob("*.svg"))
    if not svg_files:
        print(f"No SVG files found in: {args.input}", file=sys.stderr)
        return 1

    try:
        processed = process_directory(args.input, options, dry_run=args.dry_run)
    except (ValueError, Exception) as exc:
        print(f"Failed to normalize icons: {exc}", file=sys.stderr)
        return 1

    action = "Checked" if args.dry_run else "Normalized"
    print(f"{action} {len(processed)} icon(s) in {args.input}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
