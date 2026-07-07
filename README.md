# auralinc-icons

SVG icon set and icon font for the AuraLinc project.

Icons are drawn manually as vector strokes in `src/workspace/`, then built automatically into normalized SVGs and a web font on commit.

## Directory layout

```
src/
  workspace/     Manual source SVGs (gitignored, any size)
  icons/         Generated 64×64 SVGs (committed)
  icons.svg      Combined sprite sheet (optional)
dist/            Generated icon font files (committed)
scripts/
  build_icons.py         Full build: workspace → icons → font
  build-icon-font.mjs    Stroke-to-path + fantasticon
  normalize_icons.py     Re-normalize existing icons in place
  install-git-hooks.sh   Install pre-commit hook
  lib/normalize.py       Shared SVG normalization logic
.githooks/
  pre-commit             Runs build and stages src/icons + dist
```

## Workflow

1. **Draw icons** — Save stroked line-art SVGs to `src/workspace/` using the icon name as the filename (e.g. `apple.svg`, `chili-pepper.svg`). Size can vary.
2. **Commit** — The pre-commit hook builds icons and stages the output.
3. **Result** — `src/icons/` and `dist/` are updated and included in the commit. `src/workspace/` stays local and is not committed.

### One-time setup

```bash
pip install -r requirements.txt
npm install
bash scripts/install-git-hooks.sh
```

### Manual build

```bash
npm run build
# or
python3 scripts/build_icons.py
```

## Build pipeline

| Step | What happens |
|------|----------------|
| 1. Copy | Read each `src/workspace/*.svg` |
| 2. Normalize | Resize to 64×64, center with 4 px padding |
| 3. Outline | Convert strokes to filled path outlines with [picosvg](https://github.com/googlefonts/picosvg) |
| 4. Font | Generate icon font in `dist/` via [fantasticon](https://github.com/tancredi/fantasticon) |

### Icon font output (`dist/`)

| File | Purpose |
|------|---------|
| `auralinc-icons.woff2` | Primary web font |
| `auralinc-icons.woff` | Fallback web font |
| `auralinc-icons.ttf` | TrueType font |
| `auralinc-icons.css` | CSS classes (`.icon-{name}`) |
| `auralinc-icons.json` | Glyph name → codepoint map |
| `auralinc-icons.html` | Preview page |

Glyph IDs match SVG filenames without the extension (e.g. `apple.svg` → `icon-apple`, codepoint in JSON).

### Usage in HTML

```html
<link rel="stylesheet" href="dist/auralinc-icons.css">
<i class="icon-apple"></i>
<i class="icon-tomato"></i>
```

## Scripts

### `scripts/build_icons.py`

Main build entry point.

```bash
python3 scripts/build_icons.py                  # full build
python3 scripts/build_icons.py --dry-run        # preview
python3 scripts/build_icons.py --skip-font      # normalize only
python3 scripts/build_icons.py --size 64 --padding 4
```

| Flag | Default | Description |
|------|---------|-------------|
| `--workspace` | `src/workspace` | Source SVG directory |
| `--icons` | `src/icons` | Output SVG directory |
| `--dist` | `dist` | Output font directory |
| `--size` | `64` | Canvas size (px) |
| `--padding` | `4` | Inner padding (px) |
| `--skip-font` | — | Skip stroke-to-path and font generation |
| `--dry-run` | — | Preview without writing |

### `scripts/normalize_icons.py`

Re-normalize SVGs already in `src/icons/` (utility only).

```bash
python3 scripts/normalize_icons.py --input src/icons
```

## Git hook

The pre-commit hook (`.githooks/pre-commit`) runs when `src/workspace/*.svg` exists:

1. Runs `python3 scripts/build_icons.py`
2. Stages `src/icons/` and `dist/`

Install with:

```bash
bash scripts/install-git-hooks.sh
```

## Requirements

- Python 3.9+
- Node.js 18+ and npm

```bash
pip install -r requirements.txt   # picosvg for stroke-to-path
npm install                         # fantasticon for font generation
```

## What gets committed

| Path | Committed |
|------|-----------|
| `src/workspace/` | No (gitignored) |
| `src/icons/` | Yes |
| `dist/` | Yes |
| `node_modules/` | No (gitignored) |

## License

MIT — see [LICENSE](LICENSE).
