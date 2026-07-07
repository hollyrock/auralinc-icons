"""Convert stroked SVG artwork to filled path outlines for icon fonts."""

from __future__ import annotations

from picosvg.svg import SVG


def strokes_to_paths(svg_text: str) -> str:
    """Outline strokes as vector paths suitable for font generation."""
    svg = SVG.fromstring(svg_text)
    return svg.topicosvg().tostring()
