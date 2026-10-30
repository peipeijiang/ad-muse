#!/usr/bin/env python3
"""Build an LK888 request from reviewed artifacts. No network or paid action."""
import argparse
import base64
import hashlib
import json
import math
import mimetypes
from pathlib import Path


def digest(data):
    return hashlib.sha256(data).hexdigest()


def build_request(variant_dir):
    root = Path(variant_dir).resolve()
    brief = json.loads((root / 'brief.json').read_text())
    plan = json.loads((root / 'reference_plan.json').read_text())
    shots = json.loads((root / 'shot_rows.json').read_text())
    model = brief.get('model', 'minimax-h3')
    if model not in ('minimax-h3', 'omni-flash', 'omni_flash-10s'):
        raise ValueError('Unsupported model; do not guess aliases')
    h3 = model == 'minimax-h3'
    backend = 'minimax-h3' if h3 else 'omni-flash'
    if plan.get('backend') != backend:
        raise ValueError('Reference plan backend differs from brief')
    duration = float(brief.get('duration', 15 if h3 else 10))
    if not math.isfinite(duration) or not ((4 <= duration <= 15) if h3 else (0 < duration <= 10)):
        raise ValueError('Duration exceeds the selected model envelope')
    if model == 'omni_flash-10s' and duration != 10:
        raise ValueError('Fixed 10-second alias requires exactly 10 seconds')
    if not brief.get('locale') or not brief.get('aspect_ratio'):
        raise ValueError('Explicit locale and aspect_ratio are required')
    if not isinstance(shots, list) or not shots:
        raise ValueError('shot_rows.json must be a nonempty array')
    cursor = 0.0
    for shot in shots:
        start, end = float(shot['start_sec']), float(shot['end_sec'])
        if not all(map(math.isfinite, (start, end))) or abs(start - cursor) > .001 or end <= start:
            raise ValueError('Shot timeline has a gap, overlap or invalid interval')
        cursor = end
    if abs(cursor - duration) > .001:
        raise ValueError('Shot timeline does not match duration; re-author, never truncate')
    prompt_path = root / 'model_prompt.md'
    prompt_bytes = prompt_path.read_bytes()
    prompt = prompt_bytes.decode('utf-8')
    if not prompt.strip() or len(prompt) > (7000 if h3 else 4000):
        raise ValueError('Empty or oversized final prompt; re-author, never truncate')
    images = plan.get('selected_images', [])
    # Conservative common limit for the Omni family; no silent slicing.
    if not 1 <= len(images) <= (9 if h3 else 3):
        raise ValueError('Reference count outside the selected profile')
    encoded, provenance = [], []
    for ref in images:
        path = Path(ref['path'])
        if not path.is_absolute():
            raise ValueError('Selected reference paths must be absolute')
        data = path.read_bytes()
        sha = digest(data)
        if sha != ref.get('sha256') or ref.get('qc') != 'pass' or not ref.get('role'):
            raise ValueError('Reference needs matching hash, role and passed visual QC')
        mime = mimetypes.guess_type(str(path))[0]
        if mime not in ('image/png', 'image/jpeg', 'image/webp'):
            raise ValueError('Unsupported reference image format')
        encoded.append('data:' + mime + ';base64,' + base64.b64encode(data).decode('ascii'))
        provenance.append({'path': str(path), 'sha256': sha, 'role': ref['role']})
    params = {'aspect_ratio': brief['aspect_ratio']}
    params['image_url' if h3 else 'images'] = encoded
    if model != 'omni_flash-10s':
        if not brief.get('resolution'):
            raise ValueError('Explicit provider-supported resolution required')
        params.update(duration=format(duration, 'g'), resolution=brief['resolution'])
    payload = {'model': model, 'prompt': prompt, 'params': params}
    evidence = {'backend': backend, 'model': model, 'duration': duration,
                'prompt_path': str(prompt_path), 'prompt_sha256': digest(prompt_bytes),
                'reference_mode': 'full-reference' if h3 else 'omni-reference',
                'reference_images': provenance, 'locale': brief['locale'],
                'validation': 'structural_only', 'submitted': False}
    return payload, evidence


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('variant_dir', type=Path)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    try:
        payload, evidence = build_request(args.variant_dir)
        # Exclusive creation avoids overwriting a prepared or submitted request.
        with args.output.open('x', encoding='utf-8') as f:
            json.dump({'payload': payload, 'provenance': evidence}, f, ensure_ascii=False, indent=2)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        p.error(str(exc))
    print(json.dumps({'output': str(args.output.resolve()), 'model': payload['model'],
                      'submitted': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
