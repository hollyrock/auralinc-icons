"""Normalize SVG icons to a centered square canvas."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from copy import deepcopy
from dataclasses import dataclass

SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
ET.register_namespace("", SVG_NS)
ET.register_namespace("xlink", XLINK_NS)
ET.register_namespace("svg", SVG_NS)

SKIP_TAGS = {"defs", "metadata", "sodipodi:namedview", "title", "desc"}


@dataclass
class NormalizeOptions:
    target_size: int = 64
    padding: int = 4


def parse_viewbox(value: str) -> tuple[float, float, float, float]:
    parts = [float(part) for part in re.split(r"[\s,]+", value.strip()) if part]
    if len(parts) != 4:
        raise ValueError(f"Invalid viewBox: {value!r}")
    return parts[0], parts[1], parts[2], parts[3]


def is_hidden(element: ET.Element) -> bool:
    style = (element.get("style") or "").replace(" ", "").lower()
    if "display:none" in style:
        return True
    return element.tag.split("}")[-1] == "image"


def strip_hidden(element: ET.Element) -> None:
    for child in list(element):
        if is_hidden(child):
            element.remove(child)
        else:
            strip_hidden(child)


def collect_visible_children(root: ET.Element) -> list[ET.Element]:
    children: list[ET.Element] = []
    for child in root:
        tag = child.tag.split("}")[-1]
        if tag in SKIP_TAGS or is_hidden(child):
            continue
        children.append(child)
    return children


def resolve_viewbox(root: ET.Element) -> str:
    viewbox = root.get("viewBox")
    if viewbox:
        return viewbox

    width = root.get("width", "64")
    height = root.get("height", "64")
    nums_w = re.findall(r"[\d.]+", width)
    nums_h = re.findall(r"[\d.]+", height)
    if not nums_w or not nums_h:
        raise ValueError("SVG has no viewBox and no parseable width/height")
    return f"0 0 {nums_w[0]} {nums_h[0]}"


def _format_transform(tx: float, ty: float, scale: float) -> str:
    return f"translate({tx:.6f} {ty:.6f}) scale({scale:.6f})"


def normalize_svg(text: str, options: NormalizeOptions | None = None) -> str:
    options = options or NormalizeOptions()
    root = ET.fromstring(text)
    if root.tag.split("}")[-1] != "svg":
        raise ValueError("Root element is not svg")

    viewbox = resolve_viewbox(root)
    vx, vy, vw, vh = parse_viewbox(viewbox)

    visible = collect_visible_children(root)
    if not visible:
        raise ValueError("No visible SVG content found")

    inner_size = options.target_size - (options.padding * 2)
    if inner_size <= 0:
        raise ValueError("Padding is too large for the target size")

    scale = min(inner_size / vw, inner_size / vh)
    scaled_w = vw * scale
    scaled_h = vh * scale
    tx = options.padding + (inner_size - scaled_w) / 2 - vx * scale
    ty = options.padding + (inner_size - scaled_h) / 2 - vy * scale

    outer = ET.Element(
        f"{{{SVG_NS}}}svg",
        {
            "xmlns": SVG_NS,
            "width": str(options.target_size),
            "height": str(options.target_size),
            "viewBox": f"0 0 {options.target_size} {options.target_size}",
            "fill": "none",
        },
    )

    group = ET.SubElement(
        outer,
        f"{{{SVG_NS}}}g",
        {"transform": _format_transform(tx, ty, scale)},
    )

    for child in visible:
        copied = deepcopy(child)
        strip_hidden(copied)
        group.append(copied)

    xml = ET.tostring(outer, encoding="unicode")
    xml = xml.replace("svg:svg", "svg").replace("svg:g", "g").replace("svg:path", "path")
    xml = re.sub(r'\sxmlns:svg="[^"]*"', "", xml)
    return xml
