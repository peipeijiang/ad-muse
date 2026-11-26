#!/usr/bin/env python3
"""Validate AdMuse's offline color-storyboard contract. No network or image recognition."""
import hashlib
import json
import struct
from fractions import Fraction
from pathlib import Path


def text(value):
    return isinstance(value, str) and bool(value.strip())


def dimensions(data):
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24 and data[12:16] == b"IHDR":
        return struct.unpack(">II", data[16:24])
    if data.startswith(b"\xff\xd8"):
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            i += 2
            if marker == 0xD9 or marker == 0xDA:
                break
            length = struct.unpack(">H", data[i:i + 2])[0]
            if length < 2 or i + length > len(data):
                break
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
    shot_bytes = (root / "shot_rows.json").read_bytes()
    if plan.get("shot_rows_sha256") != hashlib.sha256(shot_bytes).hexdigest():
        raise ValueError("Stale shot_rows_sha256; recheck storyboard inputs")
    shots = json.loads(shot_bytes)
    return validate_board(plan, {shot["shot_id"] for shot in shots})


def review_digest(board, shot_rows_sha256):
    """Fingerprint the board and observations at the time of visual approval."""
    reviewed = {key: value for key, value in board.items() if key != "review_sha256"}
    snapshot = {"storyboard": reviewed, "shot_rows_sha256": shot_rows_sha256}
    return hashlib.sha256(json.dumps(snapshot, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode("utf-8")).hexdigest()


def validate_board(plan, known_shots, *, reference_bytes=None):
    board = plan.get("storyboard")
    if not isinstance(board, dict) or board.get("status") != "required":
        raise ValueError("Required storyboard declaration is missing")
    grid = board.get("grid")
    if not isinstance(grid, dict):
        raise ValueError("Storyboard grid declaration is required")
    columns, rows = grid.get("columns"), grid.get("rows")
    if type(columns) is not int or type(rows) is not int or (columns, rows) not in {(2, 3), (3, 2), (3, 3)}:
        raise ValueError("Storyboard grid must be 2×3, 3×2 or 3×3")
    cells = columns * rows
    if grid.get("reading_order") != "row-major":
        raise ValueError("Storyboard reading_order must be row-major")
    cell_ratio = ratio(grid.get("cell_aspect_ratio"))
    board_ratio = ratio(grid.get("board_layout_ratio"))
    expected = Fraction(columns * cell_ratio.numerator, rows * cell_ratio.denominator)
    if board_ratio != expected:
        raise ValueError("Storyboard board_layout_ratio does not match grid and cell ratio")
    ratio(grid.get("provider_transport_ratio"))
    if board.get("image_provider") != "tt-image-2.6" or board.get("image_fallback") != "none":
        raise ValueError("AdMuse storyboard requires tt-image-2.6 with no fallback")
    path = Path(board.get("path", ""))
    if not path.is_absolute() or not path.is_file():
        raise ValueError("Storyboard path must identify the reviewed local image")
    data = (reference_bytes[path] if reference_bytes is not None and path in reference_bytes
            else path.read_bytes())
    if board.get("sha256") != hashlib.sha256(data).hexdigest():
        raise ValueError("Storyboard sha256 does not match the reviewed bytes")
    width, height = dimensions(data)
    if board.get("width") != width or board.get("height") != height:
        raise ValueError("Storyboard dimensions do not match the delivered image")
    if width <= 0 or height <= 0 or Fraction(width, height) != board_ratio:
        raise ValueError("Delivered storyboard does not match board_layout_ratio")
    planned = board.get("planned_cells")
    observed = board.get("observed_cells")
    if not isinstance(planned, list) or len(planned) != cells:
        raise ValueError("One planned cell record is required for every grid cell")
    if not isinstance(observed, list) or len(observed) != cells:
        raise ValueError("One observed cell record is required for every grid cell")
    expected_ids = [f"r{r}c{c}" for r in range(1, rows + 1) for c in range(1, columns + 1)]
    for records in (planned, observed):
        if any(not isinstance(item, dict) for item in records) or [item.get("cell_id") for item in records] != expected_ids:
            raise ValueError("Cell IDs must cover every grid position in row-major order")
    covered = set()
    for index, (intent, actual) in enumerate(zip(planned, observed)):
        cell_id = intent["cell_id"]
        shot_ids = intent.get("shot_ids")
        if not isinstance(shot_ids, list) or not shot_ids or any(not text(s) or s not in known_shots for s in shot_ids):
            raise ValueError(f"{cell_id}: planned cell needs current shot IDs")
        if not text(intent.get("proof_id")):
            raise ValueError(f"{cell_id}: planned cell needs a proof_id")
        bounds = actual.get("bounds")
        if actual.get("status") != "pass" or not isinstance(bounds, list) or len(bounds) != 4 or any(type(v) is not int for v in bounds):
            raise ValueError(f"{cell_id}: observed cell needs pass status and integer bounds")
        row, column = divmod(index, columns)
        left, right = width * column // columns, width * (column + 1) // columns
        top, bottom = height * row // rows, height * (row + 1) // rows
        x, y, cell_width, cell_height = bounds
        if not (left <= x < x + cell_width <= right and top <= y < y + cell_height <= bottom):
            raise ValueError(f"{cell_id}: observed bounds must stay within the assigned grid cell")
        if (not text(actual.get("visible_proof")) or actual.get("shot_ids_observed") != shot_ids
                or actual.get("proof_id") != intent["proof_id"]):
            raise ValueError(f"{cell_id}: observed proof and shot IDs must match the planned evidence")
        covered.update(shot_ids)
    if board.get("review_sha256") != review_digest(board, plan.get("shot_rows_sha256")):
        raise ValueError("Stale storyboard review; recheck the board and cell mapping against current shot rows")
    return {"routing_version": 3, "grid": {"columns": columns, "rows": rows},
            "board_ratio": str(board_ratio), "cell_ratio": str(cell_ratio), "observed_cells": cells,
            "covered_shots": sorted(covered)}


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
