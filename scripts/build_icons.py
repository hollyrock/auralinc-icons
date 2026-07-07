#!/usr/bin/env python3
"""Build icon set and icon font from src/workspace SVG sources."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from lib.normalize import NormalizeOptions, normalize_svg
DEFAULT_WORKSPACE = REPO_ROOT / "src" / "workspace"
DEFAULT_ICONS = REPO_ROOT / "src" / "icons"
DEFAULT_DIST = REPO_ROOT / "dist"
BUILD_FONT_SCRIPT = REPO_ROOT / "scripts" / "build-icon-font.mjs"


def sync_workspace_to_icons(
    workspace_dir: Path,
    icons_dir: Path,
    options: NormalizeOptions,
    *,
    dry_run: bool = False,
) -> list[str]:
    if not workspace_dir.is_dir():
        raise FileNotFoundError(f"Workspace directory not found: {workspace_dir}")

    workspace_files = sorted(workspace_dir.glob("*.svg"))
    if not workspace_files:
        raise FileNotFoundError(f"No SVG files found in: {workspace_dir}")

    if not dry_run:
        icons_dir.mkdir(parents=True, exist_ok=True)

    icon_names = {path.stem for path in workspace_files}

    if icons_dir.exists() and not dry_run:
        for stale in icons_dir.glob("*.svg"):
            if stale.stem not in icon_names:
                stale.unlink()
                print(f"removed stale icon {stale.name}")

    processed: list[str] = []
    for source in workspace_files:
        normalized = normalize_svg(source.read_text(encoding="utf-8"), options)
        target = icons_dir / source.name

        if dry_run:
            print(f"[dry-run] would write {target.name}", flush=True)
        else:
            target.write_text(normalized, encoding="utf-8")
            print(f"normalized {target.name}", flush=True)

        processed.append(source.stem)

    return processed


def run_font_build(*, dry_run: bool = False) -> None:
    if dry_run:
        print("[dry-run] would run node scripts/build-icon-font.mjs")
        return

    if not BUILD_FONT_SCRIPT.exists():
        raise FileNotFoundError(f"Missing font build script: {BUILD_FONT_SCRIPT}")

    node_modules = REPO_ROOT / "node_modules"
    if not node_modules.exists():
        raise RuntimeError(
            "Missing node_modules. Run `npm install` in the repo root first."
        )

    subprocess.run(
        ["node", str(BUILD_FONT_SCRIPT)],
        cwd=REPO_ROOT,
        check=True,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build normalized SVG icons and icon font from src/workspace.",
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=DEFAULT_WORKSPACE,
        help=f"Source SVG directory (default: {DEFAULT_WORKSPACE})",
    )
    parser.add_argument(
        "--icons",
        type=Path,
        default=DEFAULT_ICONS,
        help=f"Output SVG directory (default: {DEFAULT_ICONS})",
    )
    parser.add_argument(
        "--dist",
        type=Path,
        default=DEFAULT_DIST,
        help=f"Output font directory (default: {DEFAULT_DIST})",
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
        "--skip-font",
        action="store_true",
        help="Only normalize SVGs; skip stroke-to-path and font generation",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show planned actions without writing files",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    options = NormalizeOptions(target_size=args.size, padding=args.padding)

    try:
        icon_names = sync_workspace_to_icons(
            args.workspace,
            args.icons,
            options,
            dry_run=args.dry_run,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"Build failed: {exc}", file=sys.stderr)
        return 1

    if args.skip_font:
        action = "Checked" if args.dry_run else "Built"
        print(f"{action} {len(icon_names)} icon(s)")
        return 0

    try:
        run_font_build(dry_run=args.dry_run)
    except (FileNotFoundError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"Font build failed: {exc}", file=sys.stderr)
        return 1

    action = "Checked" if args.dry_run else "Built"
    print(f"{action} {len(icon_names)} icon(s) -> {args.icons}")
    if not args.dry_run:
        print(f"Icon font written to {args.dist}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
