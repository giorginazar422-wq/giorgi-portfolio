"""Pixel comparison helpers for the visual regression tests."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageChops


@dataclass
class VisualDiff:
    changed_ratio: float      # 0.0 .. 1.0
    changed_pixels: int
    total_pixels: int
    size_mismatch: bool
    diff_path: Path | None


def compare_images(baseline: Path, current: Path, diff_out: Path, tolerance: int) -> VisualDiff:
    """Compares two screenshots and writes a side-by-side diff image.

    Pixels whose max channel difference is below ``tolerance`` are treated as identical,
    which hides anti-aliasing noise. The diff image shows baseline | current | changes in red.
    """
    a = Image.open(baseline).convert("RGB")
    b = Image.open(current).convert("RGB")
    size_mismatch = a.size != b.size
    if size_mismatch:
        w, h = max(a.width, b.width), max(a.height, b.height)
        a2, b2 = Image.new("RGB", (w, h), "white"), Image.new("RGB", (w, h), "white")
        a2.paste(a, (0, 0)); b2.paste(b, (0, 0))
        a, b = a2, b2

    diff = ImageChops.difference(a, b).convert("L")
    mask = diff.point(lambda v: 255 if v > tolerance else 0)
    changed = mask.histogram()[255]
    total = a.width * a.height

    red = Image.new("RGB", a.size, (220, 40, 40))
    faded = Image.blend(a, Image.new("RGB", a.size, "white"), 0.6)
    highlighted = Image.composite(red, faded, mask)
    gap = 8
    canvas = Image.new("RGB", (a.width * 3 + gap * 2, a.height), (240, 240, 240))
    canvas.paste(a, (0, 0)); canvas.paste(b, (a.width + gap, 0)); canvas.paste(highlighted, (2 * (a.width + gap), 0))
    diff_out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(diff_out)

    return VisualDiff(changed / total if total else 0.0, changed, total, size_mismatch, diff_out)
