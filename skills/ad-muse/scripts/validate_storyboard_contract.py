#!/usr/bin/env python3
"""Validate AdMuse's offline color-storyboard contract. No network or image recognition."""
import hashlib
import json
import struct
from fractions import Fraction
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text(value):
    return isinstance(value, str) and bool(value.strip())


def dimensions(path):
    data = path.read_bytes()
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        return struct.unpack(">II", data[16:24])
    if data.startswith(b"\xff\xd8"):
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            i += 2
            if marker in (0xD8, 0xD9):
                continue
            length = struct.unpack(">H", data[i:i + 2])[0]
            if marker in range(0xC0, 0xC4) or marker in range(0xC5, 0xC8) or marker in range(0xC9, 0xCC) or marker in range(0xCD, 0xD0):
                return struct.unpack(">HH", data[i + 3:i + 7])[::-1]
            i += length
    raise ValueError("Storyboard must be a readable PNG or JPEG")


def ratio(value):
    if not isinstance(value, str) or ":" not in value:
        raise ValueError("Storyboard ratios must use W:H strings")
    try:
        width, height = (int(item) for item in value.split(":", 1))
    except ValueError as exc:
        raise ValueError("Storyboard ratios must use positive integers") from exc
    if width <= 0 or height <= 0:
        raise ValueError("Storyboard ratios must be positive")
    return Fraction(width, height)


def validate(root):
    root = Path(root).resolve()
    plan = json.loads((root / "reference_plan.json").read_text())
    if plan.get("routing_version") != 3:
        raise ValueError("Storyboard contract requires routing_version 3")
    board = plan.get("storyboard")
    if not isinstance(board, dict) or board.get("status") != "required":
        raise ValueError("Required storyboard declaration is missing")
    grid = board.get("grid")
    if not isinstance(grid, dict):
        raise ValueError("Storyboard grid declaration is required")
    columns, rows = grid.get("columns"), grid.get("rows")
    if not isinstance(columns, int) or not isinstance(rows, int) or columns <= 0 or rows <= 0:
        raise ValueError("Storyboard grid needs positive integer columns and rows")
    cells = columns * rows
    if cells not in (6, 9):
        raise ValueError("AdMuse storyboard grid must contain six or nine cells")
    if grid.get("reading_order") != "row-major":
        raise ValueError("Storyboard reading_order must be row-major")
    cell_ratio = ratio(grid.get("cell_aspect_ratio"))
    board_ratio = ratio(grid.get("board_layout_ratio"))
    expected = Fraction(columns * cell_ratio.numerator, rows * cell_ratio.denominator)
    if board_ratio != expected:
        raise ValueError("Storyboard board_layout_ratio does not match grid and cell ratio")
    if not text(grid.get("provider_transport_ratio")):
        raise ValueError("Storyboard provider_transport_ratio is required")
    if board.get("image_provider") != "tt-image-2.6" or board.get("image_fallback") != "none":
        raise ValueError("AdMuse storyboard requires tt-image-2.6 with no fallback")
    path = Path(board.get("path", ""))
    if not path.is_absolute() or not path.is_file() or board.get("sha256") != sha(path):
        raise ValueError("Storyboard path or sha256 does not match the reviewed bytes")
    width, height = dimensions(path)
    if board.get("width") != width or board.get("height") != height:
        raise ValueError("Storyboard dimensions do not match the delivered image")
    planned = board.get("planned_cells")
    observed = board.get("observed_cells")
    if not isinstance(planned, list) or len(planned) != cells:
        raise ValueError("One planned cell record is required for every grid cell")
    if not isinstance(observed, list) or len(observed) != cells:
        raise ValueError("One observed cell record is required for every grid cell")
    expected_ids = {f"r{r}c{c}" for r in range(1, rows + 1) for c in range(1, columns + 1)}
    if {item.get("cell_id") for item in planned} != expected_ids or {item.get("cell_id") for item in observed} != expected_ids:
        raise ValueError("Cell IDs must cover every row-major grid position")
    for item in planned:
        if not isinstance(item.get("shot_ids"), list) or not item["shot_ids"]:
            raise ValueError("Each planned cell needs at least one mapped shot_id")
        if not text(item.get("proof_id")):
            raise ValueError("Each planned cell needs a proof_id")
    for item in observed:
        bounds = item.get("bounds")
        if item.get("status") != "pass" or not isinstance(bounds, list) or len(bounds) != 4 or any(not isinstance(v, int) for v in bounds):
            raise ValueError("Each observed cell needs pass status and integer bounds")
        x, y, cell_width, cell_height = bounds
        if x < 0 or y < 0 or cell_width <= 0 or cell_height <= 0 or x + cell_width > width or y + cell_height > height:
            raise ValueError("Observed cell bounds exceed storyboard dimensions")
        if not text(item.get("visible_proof")) or not text(item.get("shot_ids_observed")):
            raise ValueError("Each observed cell needs visible proof and observed shot IDs")
    return {"routing_version": 3, "grid": {"columns": columns, "rows": rows}, "board_ratio": str(board_ratio), "cell_ratio": str(cell_ratio), "observed_cells": cells}


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("variant_dir", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(validate(args.variant_dir), indent=2))
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
