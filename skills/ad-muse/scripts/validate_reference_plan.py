#!/usr/bin/env python3
"""Validate declared per-shot routing evidence. No network or image recognition."""
import argparse
import hashlib
import json
from pathlib import Path

RISKS = ('wearing_fit', 'finger_contact', 'two_hand_interaction', 'grip_change',
         'occlusion', 'installation', 'transfer', 'multi_actor_interaction',
         'directional_effect', 'complex_camera', 'identity_ambiguity', 'prior_anatomy_failure',
         'temporal_continuity', 'mechanism_state', 'material_change', 'surface_contact',
         'contents_transfer', 'interface_action')
ACTION_SEQUENCE = {'finger_contact', 'two_hand_interaction', 'grip_change',
                   'installation', 'transfer', 'multi_actor_interaction', 'prior_anatomy_failure',
                   'mechanism_state', 'material_change', 'contents_transfer', 'interface_action',
                   'temporal_continuity'}
SPATIAL = {'occlusion', 'installation', 'transfer', 'multi_actor_interaction',
           'directional_effect', 'complex_camera'}
PURPOSES = {'identity', 'identity_sheet', 'usage_context', 'storyboard', 'previs'}
MODES = {'product_images_only', 'identity_plus_product',
         'storyboard_plus_product', 'full_spatial_reference'}


def reference_hash(path, reference_bytes):
    data = path.read_bytes() if reference_bytes is None else reference_bytes[path]
    return hashlib.sha256(data).hexdigest()


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def routing_version(plan):
    version = plan.get('routing_version')
    if type(version) is not int or version not in (2, 3):
        raise ValueError('Routing v2 or v3 assessment required')
    return version


def validate(root, *, plan_only=False):
    root = Path(root)
    plan = json.loads((root / 'reference_plan.json').read_bytes())
    shot_bytes = (root / 'shot_rows.json').read_bytes()
    prompt_bytes = None if plan_only else (root / 'model_prompt.md').read_bytes()
    return validate_inputs(plan, shot_bytes, prompt_bytes, plan_only=plan_only)


def validate_inputs(plan, shot_bytes, prompt_bytes, *, plan_only=False, reference_bytes=None):
    version = routing_version(plan)
    if plan_only and version != 3:
        raise ValueError('Planning-only validation requires routing v3')
    shots = json.loads(shot_bytes)
    bindings = [('shot_rows_sha256', shot_bytes)]
    if not plan_only:
        bindings.append(('prompt_sha256', prompt_bytes))
    for name, data in bindings:
        if plan.get(name) != hashlib.sha256(data).hexdigest():
            raise ValueError('Stale or missing ' + name + '; reassess current actions')
    if not isinstance(shots, list) or not shots:
        raise ValueError('Nonempty shot rows required')
    ids = [s.get('shot_id') for s in shots]
    if any(not nonempty(i) for i in ids) or len(ids) != len(set(ids)):
        raise ValueError('Every shot needs a unique shot_id')
    scenes = [s.get('scene_id') for s in shots]
    if any(not nonempty(i) for i in scenes):
        raise ValueError('Every shot needs scene_id for spatial routing')
    assessments = plan.get('shot_assessments', [])
    if not isinstance(assessments, list) or len(assessments) != len(ids):
        raise ValueError('One risk assessment per shot required')
    seen, needed = set(), {p: set() for p in PURPOSES}
    needed['identity'].update(ids)
    elevated_review = False
    for a in assessments:
        sid = a.get('shot_id')
        if sid not in ids or sid in seen or not nonempty(a.get('evidence')):
            raise ValueError('Invalid, duplicate or unexplained shot assessment')
        seen.add(sid)
        risks = a.get('risks', {})
        if set(risks) != set(RISKS) or any(type(v) is not bool for v in risks.values()):
            raise ValueError('All risk flags must be explicit booleans; unknown is not low risk')
        active = {k for k, v in risks.items() if v}
        elevated_review |= 'prior_anatomy_failure' in active
        if active & ACTION_SEQUENCE:
            needed['storyboard'].update(ids if version == 2 else [sid])
        if risks['wearing_fit'] or risks['surface_contact']:
            needed['usage_context'].add(sid)
        if active & SPATIAL:
            spatial = version == 2 or a.get('spatial_dependency')
            if type(spatial) is not bool:
                raise ValueError(f'{sid}: explain whether spatial previs is needed using spatial_dependency')
            if spatial:
                needed['previs'].add(sid)
        if risks['identity_ambiguity']:
            needed['identity_sheet'].add(sid)
    if needed['previs']:
        needed['storyboard'].update(ids if version == 2 else needed['previs'])
    minimum = ('full_spatial_reference' if needed['previs'] else
               'storyboard_plus_product' if needed['storyboard'] else
               'identity_plus_product' if needed['identity_sheet'] else 'product_images_only')
    mode = plan.get('mode', minimum if version == 3 else None)
    if mode not in MODES:
        raise ValueError('Unknown routing mode')
    rank = {m: i for i, m in enumerate(('product_images_only', 'identity_plus_product',
                                      'storyboard_plus_product', 'full_spatial_reference'))}
    if rank[mode] < rank[minimum]:
        raise ValueError('Under-routed actions: minimum mode is ' + minimum)
    # Even an optional higher-tier route must actually contain its advertised evidence.
    for purpose in {'identity_plus_product': ['identity_sheet'],
                    'storyboard_plus_product': ['storyboard'], 'full_spatial_reference': ['storyboard', 'previs']}.get(mode, []):
        if not needed[purpose]:
            needed[purpose].update(ids)
    product_coverage = plan.get('product_reference_review')
    if not isinstance(product_coverage, dict) or any(not nonempty(product_coverage.get(k)) for k in ('appearance', 'angles_details', 'usage_context', 'selection_reason')):
        raise ValueError('Product reference review must explain appearance, angles/details, usage-context coverage and selection')
    result = {'routing_version': version, 'minimum_mode': minimum, 'mode': mode,
              'required_coverage': {p: sorted(v) for p, v in needed.items() if v},
              'validation': 'declared_risks_and_evidence_only', 'anatomy_verified_by_code': False}
    if version == 3:
        for name in ('reference_video', 'speech_fidelity'):
            if type(plan.get(name)) is not bool:
                raise ValueError(f'{name} must be an explicit boolean')
        if plan['speech_fidelity'] and not plan['reference_video']:
            raise ValueError('Source speech fidelity requires a reference video')
        checks = ['technical_qc', 'creative_sample']
        if plan['reference_video']:
            checks.append('source_cut_mapping')
        if plan['speech_fidelity']:
            checks.append('local_asr')
        checks.extend(p + '_qc' for p in ('identity_sheet', 'usage_context', 'storyboard', 'previs') if needed[p])
        if elevated_review:
            checks.append('anatomy_review')
        tier = ('high' if plan['reference_video'] or needed['previs'] or elevated_review else
                'standard' if needed['storyboard'] or needed['identity_sheet'] else 'quick')
        tiers = ('quick', 'standard', 'high')
        requested_depth = plan.get('minimum_production_tier', tier)
        if requested_depth not in tiers:
            raise ValueError('Unknown minimum_production_tier')
        tier = tiers[max(tiers.index(tier), tiers.index(requested_depth))]
        artifacts = ['shot_rows', 'action_prompt_draft', 'model_prompt']
        if plan['reference_video']:
            artifacts.append('source_cut_mapping')
        if plan['speech_fidelity']:
            artifacts.append('transcript')
        artifacts.extend(p for p in ('identity_sheet', 'storyboard', 'previs') if needed[p])
        if needed['storyboard']:
            artifacts.append('storyboard_prompt')
        result.update(production_tier=tier, reference_mode=mode, required_checks=checks,
                      required_artifacts=artifacts)
        if plan_only:
            return result
        if needed['storyboard']:
            from validate_storyboard_contract import validate_board
            board_shots = validate_board(plan, set(ids), reference_bytes=reference_bytes)['covered_shots']
            board = plan['storyboard']
    covered = {p: set() for p in PURPOSES}
    refs = plan.get('selected_images')
    if not isinstance(refs, list) or not refs:
        raise ValueError('Selected references required')
    storyboard_count = 0
    for ref in refs:
        purposes, covers = ref.get('purposes'), ref.get('covers_shots')
        if not isinstance(purposes, list) or not purposes or any(p not in PURPOSES for p in purposes):
            raise ValueError('Reference needs recognized purposes')
        if not isinstance(covers, list) or not covers or any(s not in ids for s in covers):
            raise ValueError('Reference needs valid shot coverage')
        if version == 3 and 'storyboard' in purposes:
            storyboard_count += 1
            if not needed['storyboard']:
                raise ValueError('No-board route cannot submit a storyboard')
            if (purposes != ['storyboard'] or ref.get('sha256') != board['sha256']
                    or Path(ref['path']).resolve() != Path(board['path']).resolve()
                    or set(covers) != set(board_shots)):
                raise ValueError('Selected storyboard must match the reviewed board and observed shot coverage')
        path = Path(ref['path'])
        if not path.is_absolute() or not path.is_file() or ref.get('sha256') != reference_hash(path, reference_bytes):
            raise ValueError('Missing or changed reference file')
        if ref.get('qc') != 'pass' or not nonempty(ref.get('visual_qc')) or not nonempty(ref.get('role')):
            raise ValueError('Reference requires passed visual review with observations and role')
        for purpose in purposes:
            covered[purpose].update(covers)
    if version == 3 and needed['storyboard'] and storyboard_count != 1:
        raise ValueError('Select the reviewed storyboard exactly once')
    for purpose, required in needed.items():
        if required - covered[purpose]:
            raise ValueError('Missing ' + purpose + ' evidence for ' + ', '.join(sorted(required - covered[purpose])))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('variant_dir', type=Path)
    parser.add_argument('--plan-only', action='store_true', help='Derive v3 needs before board creation or final prompt')
    args = parser.parse_args()
    try:
        print(json.dumps(validate(args.variant_dir, plan_only=args.plan_only), indent=2))
    except (ValueError, OSError, KeyError, TypeError, AttributeError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
