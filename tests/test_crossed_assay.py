"""Synthetic admission, missingness and interaction checks; no main responses."""
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

import numpy as np

from evoloop.crossed import comparisons, interval, panel, subtract, value
from evoloop.engine import digest
from scripts import crossed_assay as runner


class CrossedArithmeticTests(unittest.TestCase):
    def test_signed_interval_subtraction_and_unbounded_endpoints(self):
        a = interval(Fraction(1, 2), Fraction(3, 4))
        b = interval(Fraction(2, 3), Fraction(5, 6))
        difference = subtract(a, b)
        self.assertEqual(value(difference['lower']), Fraction(-1, 3))
        self.assertEqual(value(difference['upper']), Fraction(1, 12))
        unbounded = interval(Fraction(0), None)
        self.assertEqual(subtract(a, unbounded)['status'], 'unbounded_lower')
        self.assertEqual(subtract(unbounded, a)['status'], 'unbounded_upper')
        self.assertEqual(subtract(unbounded, unbounded)['status'], 'unbounded_both')
        missing = {'status': 'undefined_zero_detected_control', 'lower': None, 'upper': None}
        self.assertEqual(subtract(a, missing)['status'], 'undefined')

    def test_panel_averages_condition_fractions_and_population_means(self):
        cells = [{'D': {'Q': 1, 'C': 1}, 'U': {'Q': 2, 'C': 2},
                  'disturbed_mean': interval(Fraction(1, 5), Fraction(1, 5))},
                 {'D': {'Q': 2, 'C': 2}, 'U': {'Q': 3, 'C': 3},
                  'disturbed_mean': interval(Fraction(2, 5), Fraction(2, 5))}]
        result = panel(cells)
        self.assertEqual(value(result['retention']['lower']), Fraction(7, 12))
        self.assertNotEqual(value(result['retention']['lower']), Fraction(3, 5))
        self.assertEqual(value(result['disturbed_mean']['lower']), Fraction(3, 10))

    def test_all_crossed_cells_and_difference_of_age_differences(self):
        cfg = runner.read(runner.ROOT / 'configs/crossed-v1.json')
        worlds = []
        for state in cfg['states']:
            for age in cfg['ages']:
                for g in cfg['geometries']:
                    for treatment in cfg['treatments']:
                        q = 10 + int(age in (100, 120)) * (4 if g['id'] in ('B', 'F') else 1)
                        if treatment == 'U':
                            q = 20
                        worlds.append({'run_id': f'{state}-age{age}-{g["id"]}-{treatment}',
                            'snapshot_counts': [{'Q': q, 'R': 0, 'C': q} for _ in cfg['source_times']],
                            'samples': [{'scored_cores': q} for _ in range(81)]})
        cells, panels, contrasts = comparisons(cfg, worlds)
        self.assertEqual((len(cells), len(panels), len(contrasts)), (80, 10, 100))
        interactions = [c for c in contrasts if c['kind'] == 'interaction']
        self.assertEqual(len(interactions), 20)
        self.assertTrue(all(value(c['retention']['lower']) == Fraction(3, 20) and
                            value(c['retention']['upper']) == Fraction(3, 20) for c in interactions))
        self.assertTrue(all(value(c['disturbed_mean']['lower']) == 3 for c in interactions))


class CrossedRunnerTests(unittest.TestCase):
    def test_cache_binds_complete_shape_dtype_identity_endpoint_and_configuration(self):
        first = np.array([[1, 2], [3, 4]], np.uint8)
        second = first.reshape(1, 4)
        self.assertEqual(digest(first), digest(second))
        self.assertNotEqual(runner.search_key(first, None, {}), runner.search_key(second, None, {}))
        other_dtype = first.view(np.uint16)
        self.assertEqual(digest(first), digest(other_dtype))
        self.assertNotEqual(runner.search_key(first, None, {}), runner.search_key(other_dtype, None, {}))
        self.assertNotEqual(runner.search_key(first, None, {}), runner.search_key(first, 'known', {}))
        self.assertNotEqual(runner.search_key(first, None, {}), runner.search_key(first, None, {}, True))
        self.assertNotEqual(runner.search_key(first, None, {}), runner.search_key(first, None, {'horizon': 1}))

    def test_same_bytes_wrong_shape_cached_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            grid = np.zeros((32, 32), np.uint8)
            initial = out / 'initial.npz'
            runner.atomic_npz(initial, grid=grid)
            component = np.array([[1, 2], [3, 4]], np.uint8)
            key = runner.search_key(component, None, {})
            runner.atomic_npz(out / 'roots' / f'{key}.npz', snapshot=component.reshape(1, 4))
            cfg = {'horizon': 0, 'structural_sample_interval': 20, 'source_times': [0], 'shape': [32, 32],
                   'search': {}, 'extraction': {'minimum_empty_margin_total': 20},
                   'limits': {'unique_admitted_keys_per_world': 2}}
            spec = {'run_id': 'synthetic', 'state': 'V01', 'treatment': 'D',
                    'initial_file': str(initial), 'initial_hash': digest(grid)}
            loops = [{'core': [1, 1, 1, 1], 'genotype': None,
                      'isolation_snapshot': component, 'extraction_status': 'eligible'}]
            with patch.object(runner, 'OUT', out), patch.object(runner, 'common_binding', return_value={}), \
                    patch.object(runner, 'observation', return_value=({}, [], loops)):
                with self.assertRaisesRegex(ValueError, 'cached complete root changed'):
                    runner.world(spec, {'config': cfg, 'registry': []})

    def test_failed_robust_criterion_retains_unresolved_advantage_and_gates(self):
        cfg = runner.read(runner.ROOT / 'configs/crossed-v1.json')
        m = {'experiment_id': 'synthetic', 'config': cfg, 'calibration_gate_status': 'failed',
             'exposure_verified': True, 'distinct_confirmation_verified': True,
             'states': {state: {'source': {'run_id': f'near-main-{state}'}} for state in cfg['states']}}
        worlds = [{'run_id': f'{state}-age{age}-{geometry["id"]}-{treatment}',
                   'sources': [], 'snapshot_counts': [{'Q': 10, 'R': 0, 'C': 10} for _ in cfg['source_times']],
                   'samples': [{'scored_cores': 10} for _ in range(81)]}
                  for state in cfg['states'] for age in cfg['ages']
                  for geometry in cfg['geometries'] for treatment in cfg['treatments']]
        tied = runner.summary(m, worlds, [])
        self.assertTrue(all(b['relative_robust_superiority'] is False and
                            b['biological_advantage'] == 'unresolved' for b in tied['benefits']))
        for world in worlds:
            if world['run_id'].startswith(('RV01-', 'RV02-')) and world['run_id'].endswith('-D'):
                world['snapshot_counts'] = [{'Q': 20, 'R': 0, 'C': 20} for _ in cfg['source_times']]
        advantage = runner.summary(m, worlds, [])
        self.assertTrue(all(b['relative_robust_superiority'] and b['absolute_robust_superiority'] and
                            not b['joint_confirmed'] and b['biological_advantage'] == 'unresolved'
                            for b in advantage['benefits']))
        self.assertFalse(advantage['gate_checks']['frozen_calibration'])
        self.assertEqual(advantage['joint_confirmed_encounters'], 0)

    def test_cached_keys_consume_local_admission_and_unsearched_sources_remain(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            grid = np.zeros((32, 32), np.uint8)
            initial = out / 'initial.npz'
            runner.atomic_npz(initial, grid=grid)
            spec = {'run_id': 'synthetic', 'state': 'V01', 'age': 0, 'geometry': 'A',
                    'split': 'development', 'treatment': 'D', 'pair_id': 'synthetic',
                    'initial_file': str(initial), 'initial_hash': digest(grid)}
            cfg = {'horizon': 0, 'structural_sample_interval': 20, 'source_times': [0],
                   'shape': [32, 32], 'search': {}, 'extraction': {'minimum_empty_margin_total': 20},
                   'limits': {'unique_admitted_keys_per_world': 2}}
            def organism(index, state):
                return {'core': [index, 1, 1, 1], 'genotype': 'known',
                        'isolation_snapshot': np.array([[state]], np.uint8), 'extraction_status': 'eligible'}
            loops = [organism(1, 1), organism(2, 2), organism(3, 1), organism(4, 3)]
            def fields(outcome, identity, registry):
                return {'transmission_confirmed': outcome is not None}
            with patch.object(runner, 'OUT', out), patch.object(runner, 'common_binding', return_value={}), \
                    patch.object(runner, 'observation', return_value=({'scored_cores': 4}, [], loops)), \
                    patch.object(runner, 'search_fields', side_effect=fields), \
                    patch.object(runner, 'search', side_effect=lambda p, i, m: (
                        runner.search_key(p, i, cfg['search']), {'confirmation': {'identity': i}})) as search:
                result = runner.world(spec, {'config': cfg, 'registry': ['known']})
                self.assertEqual(result['admitted_distinct_keys'], 2)
                self.assertEqual(result['snapshot_counts'], [{'t': 0, 'Q': 3, 'R': 1, 'C': 4}])
                self.assertEqual(search.call_count, 3)
                last = result['sources'][-1]
                self.assertEqual(last['status'], 'unsearched_budget')
                self.assertEqual(last['extraction_status'], 'eligible')
                self.assertIsNone(last['search_dir'])
                self.assertTrue((out / last['snapshot_file']).is_file())
                with patch.object(runner, 'observation', side_effect=AssertionError('must reuse')):
                    self.assertEqual(runner.world(spec, {'config': cfg, 'registry': ['known']}), result)

    def test_readiness_refuses_any_response_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            (out / 'roots').mkdir()
            with patch.object(runner, 'OUT', out), patch.object(runner, 'verify_design', return_value={}):
                with self.assertRaisesRegex(ValueError, 'response evidence must be absent'):
                    runner.freeze_readiness()

    def test_receipt_reuse_rejects_changed_native_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            runner.atomic_json(out / 'result.json', {'Q': 1})
            runner.receipt(out, {'readiness_sha256': 'frozen'})
            self.assertTrue(runner.verify_receipt(out, {'readiness_sha256': 'frozen'}))
            runner.atomic_json(out / 'result.json', {'Q': 2})
            with self.assertRaisesRegex(ValueError, 'artifacts changed'):
                runner.verify_receipt(out, {'readiness_sha256': 'frozen'})


if __name__ == '__main__':
    unittest.main()
