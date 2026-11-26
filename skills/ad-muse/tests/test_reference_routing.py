import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from validate_reference_plan import RISKS, validate
from prepare_request import build_request
from validate_storyboard_contract import review_digest, validate as validate_storyboard

class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root/'model_prompt.md').write_text('A reviewed product demonstration.')
        # Tiny real PNG; these are structural tests, not visual QC.
        import base64
        (self.root/'ref.png').write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII='))
    def write(self, risks=(), purposes=('identity',), mode='product_images_only', count=1):
        shots=[{'shot_id':f's{i}', 'scene_id':'room','start_sec':i*10/count,'end_sec':(i+1)*10/count} for i in range(count)]
        (self.root/'shot_rows.json').write_text(json.dumps(shots))
        h=lambda p:hashlib.sha256((self.root/p).read_bytes()).hexdigest()
        self.plan={'routing_version':2,'backend':'minimax-h3','mode':mode,'shot_rows_sha256':h('shot_rows.json'),'prompt_sha256':h('model_prompt.md'),'shot_assessments':[{'shot_id':s['shot_id'],'evidence':'Fixture action assessment','risks':{k:k in risks for k in RISKS}} for s in shots], 'selected_images':[{'path':str(self.root/'ref.png'),'sha256':h('ref.png'),'role':'fixture evidence','qc':'pass','visual_qc':'Fixture only; no visual inference','purposes':list(purposes),'covers_shots':[s['shot_id'] for s in shots]}]}
        self.plan['product_reference_review']={k:'Fixture coverage explanation' for k in ['appearance','angles_details','usage_context','selection_reason']}
        self.save()
    def save(self):
        (self.root/'reference_plan.json').write_text(json.dumps(self.plan))
    def test_static_product_only(self):
        self.write();self.assertEqual(validate(self.root)['minimum_mode'],'product_images_only')
    def test_independent_static_cuts_not_forced_to_board(self):
        self.write(count=3);self.assertEqual(validate(self.root)['minimum_mode'],'product_images_only')
    def test_wearing_not_packshot_only(self):
        self.write(risks=['wearing_fit'])
        with self.assertRaisesRegex(ValueError,'usage_context'):validate(self.root)
    def test_stable_wearing_with_fit_photo_no_boards(self):
        self.write(['wearing_fit'],['identity','usage_context'],'product_images_only');validate(self.root)
    def test_contact_sequence_needs_storyboard(self):
        self.write(['finger_contact','temporal_continuity'],['identity','usage_context'],'product_images_only')
        with self.assertRaisesRegex(ValueError,'storyboard'):validate(self.root)
    def test_contact_sequence_with_board_no_previs(self):
        self.write(['finger_contact','temporal_continuity'],['identity','usage_context','storyboard'],'storyboard_plus_product');validate(self.root)
    def test_spatial_does_not_replace_usage_reference(self):
        self.write(['occlusion','wearing_fit'],['identity','storyboard','previs'],'full_spatial_reference')
        with self.assertRaisesRegex(ValueError,'usage_context'):validate(self.root)
    def test_complex_route(self):
        self.write(['installation','two_hand_interaction'],['identity','usage_context','storyboard','previs'],'full_spatial_reference');validate(self.root)
    def test_nonhuman_state_and_interface_routes(self):
        for risk in ['mechanism_state','material_change','surface_contact','contents_transfer','interface_action']:
            with self.subTest(risk=risk):
                self.write([risk,'temporal_continuity'],['identity','usage_context','storyboard'],'storyboard_plus_product')
                self.assertEqual(validate(self.root)['minimum_mode'],'storyboard_plus_product')
    def test_multiple_complementary_product_images(self):
        self.write(['wearing_fit'])
        import copy
        use=copy.deepcopy(self.plan['selected_images'][0])
        (self.root/'usage.png').write_bytes((self.root/'ref.png').read_bytes())
        use.update(path=str(self.root/'usage.png'),purposes=['usage_context'],role='Source usage photo')
        self.plan['selected_images'].append(use);self.save()
        self.assertEqual(validate(self.root)['minimum_mode'],'product_images_only')
    def test_missing_product_selection_review(self):
        self.write();self.plan.pop('product_reference_review');self.save()
        with self.assertRaisesRegex(ValueError,'Product reference review'):validate(self.root)
    def test_removed_operation_route_rejected(self):
        self.write(mode='operation_plus_product')
        with self.assertRaisesRegex(ValueError,'Unknown routing mode'):validate(self.root)
    def test_removed_operation_purpose_rejected(self):
        self.write(purposes=['identity','operation'])
        with self.assertRaisesRegex(ValueError,'recognized purposes'):validate(self.root)
    def test_unknown_risk(self):
        self.write();del self.plan['shot_assessments'][0]['risks']['finger_contact'];self.save()
        with self.assertRaisesRegex(ValueError,'booleans'):validate(self.root)
    def test_stale_prompt(self):
        self.write();(self.root/'model_prompt.md').write_text('New action')
        with self.assertRaisesRegex(ValueError,'Stale'):validate(self.root)
    def test_legacy_plan_blocked_in_request_builder(self):
        self.write();self.plan.pop('routing_version');self.save()
        (self.root/'brief.json').write_text('{}')
        with self.assertRaisesRegex(ValueError,'v2'):build_request(self.root)
    def test_valid_request_builder(self):
        self.write();(self.root/'brief.json').write_text(json.dumps({'model':'minimax-h3','duration':10,'locale':'es-MX','aspect_ratio':'9:16','resolution':'768P'}))
        payload,evidence=build_request(self.root);self.assertFalse(evidence['submitted']);self.assertEqual(evidence['routing']['minimum_mode'],'product_images_only')
    def test_prior_failure_requires_storyboard(self):
        self.write(['prior_anatomy_failure'])
        with self.assertRaisesRegex(ValueError,'storyboard'):validate(self.root)
    def test_wrong_shot_coverage(self):
        self.write(count=2);self.plan['selected_images'][0]['covers_shots']=['s0'];self.save()
        with self.assertRaisesRegex(ValueError,'s1'):validate(self.root)

    def write_storyboard_v3(self, columns=2, rows=3):
        import struct
        import zlib

        self.write(count=2, mode='storyboard_plus_product')
        self.plan['shot_assessments'][0]['risks']['finger_contact'] = True
        board_path = self.root / 'storyboard.png'
        width, height = columns * 9, rows * 16

        def chunk(kind, data):
            return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))

        board_path.write_bytes(b'\x89PNG\r\n\x1a\n' +
                               chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)) +
                               chunk(b'IDAT', zlib.compress((b'\0' + b'\xff\x88\x44' * width) * height)) +
                               chunk(b'IEND', b''))
        board_sha = hashlib.sha256(board_path.read_bytes()).hexdigest()
        cells, observed = [], []
        for row in range(1, rows + 1):
            for column in range(1, columns + 1):
                cell_id = f'r{row}c{column}'
                proof_id = f'proof-{cell_id}'
                cells.append({'cell_id': cell_id, 'shot_ids': ['s0'], 'proof_id': proof_id})
                observed.append({'cell_id': cell_id, 'status': 'pass',
                                 'bounds': [(column - 1) * 9, (row - 1) * 16, 9, 16],
                                 'proof_id': proof_id, 'visible_proof': f'fixture for {cell_id}',
                                 'shot_ids_observed': ['s0']})
        self.plan.update(routing_version=3, reference_video=False, speech_fidelity=False,
                         storyboard={'status': 'required', 'path': str(board_path), 'sha256': board_sha,
                                     'width': width, 'height': height, 'image_provider': 'tt-image-2.6',
                                     'image_fallback': 'none',
                                     'grid': {'columns': columns, 'rows': rows, 'reading_order': 'row-major',
                                              'cell_aspect_ratio': '9:16', 'board_layout_ratio': f'{width}:{height}',
                                              'provider_transport_ratio': f'{width}:{height}'},
                                     'planned_cells': cells, 'observed_cells': observed})
        board = self.plan['storyboard']
        board['review_sha256'] = review_digest(board, self.plan['shot_rows_sha256'])
        self.plan['selected_images'].append({'path': str(board_path), 'sha256': board_sha,
                                             'role': 'Storyboard planning reference', 'qc': 'pass',
                                             'visual_qc': 'Fixture only', 'purposes': ['storyboard'],
                                             'covers_shots': ['s0']})
        self.save()

    def test_v3_no_board_and_replication(self):
        self.write(['wearing_fit'], ['identity', 'usage_context'])
        self.plan.update(routing_version=3, reference_video=False, speech_fidelity=False)
        self.save()
        self.assertEqual(validate(self.root)['production_tier'], 'quick')
        self.plan.update(reference_video=True, speech_fidelity=True)
        self.save()
        result = validate(self.root)
        self.assertEqual(result['production_tier'], 'high')
        self.assertEqual(result['reference_mode'], 'product_images_only')
        self.assertIn('local_asr', result['required_checks'])
        self.assertNotIn('storyboard', result['required_artifacts'])

    def test_v3_review_override_preserves_all_no_board_payloads(self):
        for model, backend, resolution in (
            ('minimax-h3', 'minimax-h3', '768P'),
            ('omni-flash', 'omni-flash', '720P'),
            ('omni_flash-10s', 'omni-flash', '720P'),
        ):
            with self.subTest(model=model):
                self.write()
                self.plan['backend'] = backend
                self.save()
                (self.root / 'brief.json').write_text(json.dumps({
                    'model': model, 'duration': 10, 'locale': 'es-MX',
                    'aspect_ratio': '9:16', 'resolution': resolution,
                }))
                old_payload, _ = build_request(self.root)
                self.plan.update(routing_version=3, reference_video=False,
                                 speech_fidelity=False, minimum_production_tier='high')
                self.save()
                payload, evidence = build_request(self.root)
                self.assertEqual(evidence['routing']['production_tier'], 'high')
                self.assertEqual(evidence['routing']['reference_mode'], 'product_images_only')
                self.assertEqual(payload, old_payload)

    def test_v3_preflight_before_prompt_and_assets(self):
        self.write(['finger_contact', 'installation', 'identity_ambiguity', 'wearing_fit'])
        self.plan.update(routing_version=3, reference_video=False, speech_fidelity=False)
        self.plan.pop('mode')
        assessment = self.plan['shot_assessments'][0]
        (self.root / 'model_prompt.md').unlink()
        assessment['spatial_dependency'] = False
        self.save()
        self.assertEqual(validate(self.root, plan_only=True)['production_tier'], 'standard')
        assessment['spatial_dependency'] = True
        self.save()
        result = validate(self.root, plan_only=True)
        self.assertEqual(result['production_tier'], 'high')
        self.assertEqual(result['reference_mode'], 'full_spatial_reference')
        self.assertEqual(set(result['required_coverage']),
                         {'identity', 'identity_sheet', 'usage_context', 'storyboard', 'previs'})

    def test_v3_stale_prompt_or_unattached_board_blocks_request(self):
        self.write_storyboard_v3()
        (self.root / 'brief.json').write_text(json.dumps({'model': 'minimax-h3', 'duration': 10,
                                                         'locale': 'es-MX', 'aspect_ratio': '9:16',
                                                         'resolution': '768P'}))
        brief = self.root / 'brief.json'
        original_brief = brief.read_text()
        brief.write_text(original_brief.replace('9:16', '16:9'))
        with self.assertRaisesRegex(ValueError, 'cell ratio differs'):
            build_request(self.root)
        brief.write_text(original_brief)
        payload, evidence = build_request(self.root)
        self.assertEqual(len(payload['params']['image_url']), 2)
        self.assertEqual(len(evidence['request_sha256']), 64)
        (self.root / 'model_prompt.md').write_text('Revised CTA')
        with self.assertRaisesRegex(ValueError, 'prompt_sha256'):
            build_request(self.root)
        self.plan['prompt_sha256'] = hashlib.sha256((self.root / 'model_prompt.md').read_bytes()).hexdigest()
        self.save()
        self.assertNotEqual(build_request(self.root)[1]['request_sha256'], evidence['request_sha256'])
        self.plan['selected_images'].pop()
        self.save()
        with self.assertRaisesRegex(ValueError, 'reviewed storyboard exactly once'):
            build_request(self.root)

    def test_v3_current_shot_hash_does_not_refresh_board_review(self):
        self.write_storyboard_v3()
        path = self.root / 'shot_rows.json'
        shots = json.loads(path.read_text())
        shots[0]['action'] = 'Use the left hand instead'
        path.write_text(json.dumps(shots))
        self.plan['shot_rows_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        self.save()
        with self.assertRaisesRegex(ValueError, 'Stale storyboard review'):
            validate(self.root)

    def test_v3_rejects_wrong_observed_shot_or_cell(self):
        for field, value in [('shot_ids_observed', ['s1']), ('bounds', [9, 0, 9, 16])]:
            with self.subTest(field=field):
                self.write_storyboard_v3()
                self.plan['storyboard']['observed_cells'][0][field] = value
                self.save()
                with self.assertRaisesRegex(ValueError, 'r1c1'):
                    validate(self.root)

    def test_color_storyboard_v3_contract(self):
        self.write_storyboard_v3()
        result = validate_storyboard(self.root)
        self.assertEqual(result['grid'], {'columns': 2, 'rows': 3})
        self.assertEqual(validate(self.root)['routing_version'], 3)

    def test_storyboard_contract_rejects_wrong_board_ratio(self):
        self.write_storyboard_v3()
        self.plan['storyboard']['grid']['board_layout_ratio'] = '9:16'
        self.save()
        with self.assertRaisesRegex(ValueError, 'board_layout_ratio'):
            validate_storyboard(self.root)

    def test_storyboard_contract_rejects_unobserved_cell(self):
        self.write_storyboard_v3()
        self.plan['storyboard']['observed_cells'][0]['status'] = 'pending'
        self.save()
        with self.assertRaisesRegex(ValueError, 'observed cell'):
            validate_storyboard(self.root)

if __name__=='__main__':unittest.main()
