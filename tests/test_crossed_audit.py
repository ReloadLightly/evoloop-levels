"""Independent exact arithmetic/provenance fixtures, without CA acquisition."""
import copy
import json
import tempfile
import unittest
from collections import Counter
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

import numpy as np

from scripts import verify_crossed as auditor


class CrossedAuditTests(unittest.TestCase):
    @staticmethod
    def bound(lower, upper):
        return {'status': auditor.interval_status(lower, upper),
                'lower': auditor.record_value(Fraction(lower)) if lower is not None else None,
                'upper': auditor.record_value(Fraction(upper)) if upper is not None else None}

    @staticmethod
    def counts(q, c):
        return {'Q': q, 'R': c - q, 'C': c}

    @staticmethod
    def source(confirmed=False, searched=True, extraction='eligible'):
        return {'transmission_confirmed': confirmed, 'confirmed_identity': 'stable' if confirmed else None,
                'extraction_status': extraction, 'search_dir': 'searches/key' if searched else None,
                'search_key': 'key' if searched else None, 'source_identity': None,
                'source_class': 'unknown_identity', 'status': 'confirmed' if confirmed else 'unsearched_budget'}

    @staticmethod
    def fixture():
        cfg = json.loads((auditor.ROOT / 'configs/crossed-v1.json').read_text())
        manifest = {'experiment_id': cfg['experiment_id'], 'config': cfg,
            'calibration_gate_status': 'passed', 'exposure_verified': True, 'distinct_confirmation_verified': True,
            'states': {'RV01': {'source': {'run_id': 'near-main-V02-V03-p20-a-parallel'}},
                       'RV02': {'source': {'run_id': 'near-main-V01-V03-p20-a-parallel'}}}}
        worlds = []
        for spec in auditor.cartesian_specs(cfg):
            late = int(spec['age'] in (100, 120))
            q = (10 + late * (4 if spec['geometry'] in ('B', 'F') else 1)) if spec['treatment'] == 'D' else 20
            sources = []
            censuses = []
            for t in cfg['source_times']:
                censuses.append({'t': t, 'Q': q, 'R': 0, 'C': q})
                for _ in range(q):
                    source = CrossedAuditTests.source(confirmed=True)
                    source.update(run_id=spec['run_id'], state=spec['state'], treatment=spec['treatment'], t=t)
                    sources.append(source)
            worlds.append({**spec, 'snapshot_counts': censuses, 'sources': sources,
                'samples': [{'t': t, 'scored_cores': q} for t in range(0, 1601, 20)]})
        controls = [{'kind': 'phase', 'transmission_confirmed': True, 'search_key': 'key'} for _ in range(30)]
        controls.extend({'kind': 'omitted', 'transmission_confirmed': True, 'search_key': 'key'} for _ in range(3))
        return manifest, worlds, controls

    def test_partition_keeps_unknown_confirmations_once_and_exclusions_in_R(self):
        recovered = self.source(confirmed=True)
        excluded = [self.source(searched=False, extraction=kind)
                    for kind in ('shared_component', 'noncontractible_component', 'component_too_large')]
        rows = [recovered, self.source(searched=False), *excluded]
        self.assertEqual(auditor.partition(rows), {'Q': 1, 'R': 4, 'C': 5})
        self.assertIsNone(recovered['source_identity'])
        self.assertEqual(auditor.partition([]), self.counts(0, 0))
        excluded[0]['transmission_confirmed'] = True
        excluded[0]['confirmed_identity'] = 'invented'
        with self.assertRaises(AssertionError):
            auditor.partition(rows)

    def test_partition_rejects_boolean_or_inconsistent_integer_counts(self):
        for counts in ({'Q': True, 'R': 0, 'C': 1}, {'Q': 2, 'R': 0, 'C': 1},
                       {'Q': 0, 'R': -1, 'C': -1}):
            with self.assertRaises(AssertionError):
                auditor.check_partition(counts)

    def test_zero_recovery_unbounded_control_and_absent_control_are_distinct(self):
        measured_zero = auditor.retention(self.counts(0, 0), self.counts(2, 2))
        self.assertEqual(measured_zero, self.bound(0, 0))
        unbounded = auditor.retention(self.counts(2, 3), self.counts(0, 4))
        self.assertEqual(unbounded, self.bound(Fraction(1, 2), None))
        undefined = auditor.retention(self.counts(0, 0), self.counts(0, 0))
        self.assertEqual(undefined, {'status': 'undefined_zero_detected_control', 'lower': None, 'upper': None})

    def test_panel_averages_per_condition_Fractions_without_pooling(self):
        intervals = [auditor.retention(self.counts(1, 1), self.counts(2, 2)),
                     auditor.retention(self.counts(2, 2), self.counts(3, 3))]
        panel = auditor.average_intervals(intervals)
        self.assertEqual(panel, self.bound(Fraction(7, 12), Fraction(7, 12)))
        self.assertNotEqual(panel['lower'], auditor.fraction_record(3, 5))
        intervals[1] = self.bound(0, None)
        self.assertEqual(auditor.average_intervals(intervals), self.bound(Fraction(1, 4), None))
        intervals[0] = {'status': 'undefined_zero_detected_control', 'lower': None, 'upper': None}
        self.assertEqual(auditor.average_intervals(intervals)['status'], 'undefined_zero_detected_control')

    def test_signed_interval_subtraction_and_all_infinite_directions(self):
        a, b = self.bound(Fraction(1, 2), Fraction(3, 4)), self.bound(Fraction(2, 3), Fraction(5, 6))
        self.assertEqual(auditor.subtract_intervals(a, b), self.bound(Fraction(-1, 3), Fraction(1, 12)))
        unbounded = self.bound(0, None)
        self.assertEqual(auditor.subtract_intervals(a, unbounded)['status'], 'unbounded_lower')
        self.assertEqual(auditor.subtract_intervals(unbounded, a)['status'], 'unbounded_upper')
        self.assertEqual(auditor.subtract_intervals(unbounded, unbounded)['status'], 'unbounded_both')
        missing = {'status': 'undefined_zero_detected_control', 'lower': None, 'upper': None}
        self.assertEqual(auditor.subtract_intervals(a, missing), {'status': 'undefined', 'lower': None, 'upper': None})

    def test_exact_ties_overlap_and_unbounded_inputs_cannot_establish_advantage(self):
        self.assertTrue(auditor.strict_superiority(self.bound(2, 3), [self.bound(0, 1), self.bound(0, Fraction(3, 2))]))
        self.assertFalse(auditor.strict_superiority(self.bound(1, 3), [self.bound(0, 1)]))
        self.assertFalse(auditor.strict_superiority(self.bound(Fraction(1, 2), 2), [self.bound(0, 1)]))
        self.assertIsNone(auditor.strict_superiority(self.bound(2, 3), [self.bound(0, None)]))
        self.assertIsNone(auditor.strict_superiority({'lower': None}, [self.bound(0, 1)]))

    def test_integer_threshold_and_joint_gates_keep_empty_denominator_unresolved(self):
        self.assertTrue(auditor.exact_threshold(4, 5, '4/5'))
        self.assertFalse(auditor.exact_threshold(7999999999999999, 10000000000000000, '4/5'))
        self.assertIsNone(auditor.exact_threshold(0, 0, '4/5'))
        self.assertIsNone(auditor.joint([True, None]))
        self.assertFalse(auditor.joint([True, None, False]))

    def test_local_admission_counts_cached_keys_and_keeps_repeated_observations(self):
        admitted = set()
        globally_cached = {'a', 'b', 'c'}
        for key in ('a', 'b'):
            self.assertIn(key, globally_cached)
            self.assertTrue(auditor.local_admission(key, admitted, 2))
        self.assertFalse(auditor.local_admission('c', admitted, 2))
        self.assertTrue(auditor.local_admission('a', admitted, 2))
        self.assertEqual(admitted, {'a', 'b'})

    def test_complete_key_binds_shape_dtype_identity_endpoint_and_configuration(self):
        component = np.array([[1, 2], [3, 4]], np.uint8)
        cfg = {'horizon': 1600, 'depth': 6}
        base = auditor.cache_key(component, None, False, cfg)
        self.assertEqual(base, auditor.cache_key(component.copy(), None, False, dict(reversed(list(cfg.items())))))
        self.assertEqual(auditor.digest(component), auditor.digest(component.reshape(1, 4)))
        self.assertEqual(auditor.digest(component), auditor.digest(component.view(np.uint16)))
        others = [auditor.cache_key(component.reshape(1, 4), None, False, cfg),
                  auditor.cache_key(component.view(np.uint16), None, False, cfg),
                  auditor.cache_key(component, 'known', False, cfg),
                  auditor.cache_key(component, None, True, cfg),
                  auditor.cache_key(component, None, False, {**cfg, 'depth': 7})]
        self.assertTrue(all(key != base for key in others))

    def test_all80_cells10_panels100_contrasts_have_expected_interaction(self):
        manifest, worlds, _ = self.fixture()
        cells, panels, contrasts = auditor.comparison_summary(manifest['config'], worlds)
        self.assertEqual((len(cells), len(panels), len(contrasts)), (80, 10, 100))
        self.assertTrue(all(panel['conditions'] == 8 for panel in panels))
        interactions = [row for row in contrasts if row['kind'] == 'interaction']
        self.assertEqual(len(interactions), 20)
        self.assertTrue(all(row['retention'] == self.bound(Fraction(3, 20), Fraction(3, 20)) for row in interactions))
        self.assertTrue(all(row['disturbed_mean'] == self.bound(3, 3) for row in interactions))
        self.assertEqual(cells[0]['registry_diagnostic']['D']['samples'], 81)
        self.assertEqual(cells[0]['D']['Q'], 50)
        worlds[0]['snapshot_counts'].pop()
        with self.assertRaises(AssertionError):
            auditor.comparison_summary(manifest['config'], worlds)

    def test_independent_summary_matches_runner_without_sharing_arithmetic(self):
        from scripts import crossed_assay as runner
        manifest, worlds, controls = self.fixture()
        with patch.object(auditor, 'read', return_value={'generation_simulations': 2}), \
                patch.object(runner, 'read', return_value={'generation_simulations': 2}):
            expected = auditor.analysis_summary(manifest, worlds, controls)
            self.assertEqual(expected, runner.summary(manifest, worlds, controls))
            self.assertEqual(expected['unique_searches'], 1)
            self.assertEqual(expected['unresolved_other_candidate_encounters'], 16)
            self.assertFalse(expected['benefits'][0]['joint_confirmed'])
            self.assertEqual(expected['benefits'][0]['biological_advantage'], 'unresolved')

    def test_failed_calibration_and_control_cannot_be_rescued_by_large_candidate(self):
        manifest, worlds, controls = self.fixture()
        for result in worlds:
            if result['state'].startswith('RV') and result['treatment'] == 'D':
                for row in result['snapshot_counts']:
                    row.update(Q=100, R=0, C=100)
        with patch.object(auditor, 'read', return_value={'generation_simulations': 2}):
            successful = auditor.analysis_summary(manifest, worlds, controls)
            self.assertTrue(all(row['joint_confirmed'] for row in successful['benefits']))
            self.assertEqual(successful['yield'][0]['fraction'], auditor.fraction_record(2, 36))
            self.assertEqual(successful['yield'][1]['fraction'], auditor.fraction_record(0, 18))
            manifest['calibration_gate_status'] = 'failed'
            failed = auditor.analysis_summary(manifest, worlds, controls)
            self.assertTrue(all(row['relative_robust_superiority'] and row['absolute_robust_superiority'] for row in failed['benefits']))
            self.assertFalse(any(row['joint_confirmed'] for row in failed['benefits']))
            manifest['calibration_gate_status'] = 'passed'
            controls[0]['transmission_confirmed'] = False
            self.assertFalse(auditor.analysis_summary(manifest, worlds, controls)['gate_checks']['repeated_phase_controls'])

    def test_source_unsearched_fate_preserves_missing_reproduction_and_pending_benefit(self):
        source = self.source(searched=False)
        source.update(root_reproduction_observed=None, isolated_grid_extinction_nodes=[],
            confirmed_identity_in_registry=None, same_as_source_identity=None, search_censoring=[],
            inheritance_unresolved=True, ancestry_ambiguous=True, benefit_pending=None)
        auditor.source_labels(source, {'offspring_per_generation': 3}, [])
        source['root_reproduction_observed'] = False
        with self.assertRaises(AssertionError):
            auditor.source_labels(source, {'offspring_per_generation': 3}, [])

    def test_receipt_requires_readiness_and_complete_artifact_inventory(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / 'result.json').write_text('{}\n')
            binding = {'manifest_sha256': 'm', 'readiness_sha256': 'r'}
            auditor.atomic_json(folder / 'receipt.json', {'binding': binding,
                'artifact_sha256': {'result.json': auditor.sha(folder / 'result.json')}})
            auditor.receipt(folder, binding)
            with self.assertRaises(AssertionError):
                auditor.receipt(folder, {**binding, 'readiness_sha256': 'different'})
            (folder / 'unrecorded.npz').write_bytes(b'child evidence')
            with self.assertRaises(AssertionError):
                auditor.receipt(folder, binding)

    def test_passed_proof_reuse_is_invalidated_by_any_evidence_change(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            for name in ('manifest.json', 'readiness.json', 'design-integrity.json'):
                (out / name).write_text('{}\n')
            paths = [out / 'source.npz']
            paths[0].write_bytes(b'complete initial')
            operation_calls = []
            counts = Counter()
            def operation():
                operation_calls.append(True)
                counts['dense_checks'] += 1
            with patch.object(auditor, 'OUT', out), patch.object(auditor, 'ROOT', out), \
                    patch.object(auditor, 'REUSED', ()), patch.object(auditor, 'FRESH', False), \
                    patch.object(auditor, 'headroom'):
                auditor.proven('world', 'one', paths, 'physical', counts, operation)
                auditor.proven('world', 'one', paths, 'physical', counts, operation)
                self.assertEqual(len(operation_calls), 1)
                self.assertEqual(counts['world_proofs_reused'], 1)
                paths[0].write_bytes(b'changed initial')
                auditor.proven('world', 'one', paths, 'physical', counts, operation)
                self.assertEqual(len(operation_calls), 2)
                self.assertEqual(counts['dense_checks'], 3)

    def test_committed_hash_checks_full_commit_and_exact_git_bytes(self):
        commit = 'a' * 40
        with patch.object(auditor.subprocess, 'check_output', return_value=b'committed proof') as git:
            self.assertEqual(auditor.committed_hash(commit, 'data/crossed-v1/readiness.json'),
                             auditor.hashlib.sha256(b'committed proof').hexdigest())
            git.assert_called_once_with(['git', 'show', f'{commit}:data/crossed-v1/readiness.json'], cwd=auditor.ROOT)
        for invalid in ('HEAD', 'a' * 39, 'z' * 40):
            with self.assertRaises(AssertionError):
                auditor.committed_hash(invalid, 'readiness.json')

    def test_actual_original_catalogue_links_and_denominators_remain_verifiable(self):
        manifest = json.loads((auditor.ROOT / 'data/crossed-v1/manifest.json').read_text())
        auditor.originating_encounters(manifest)
        changed = copy.deepcopy(manifest)
        changed['config']['pairs'][0]['inputs'].reverse()
        with self.assertRaises(AssertionError):
            auditor.originating_encounters(changed)

    def test_memory_stop_and_verification_failure_are_recorded_separately(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            with patch.object(auditor, 'OUT', out), patch.object(auditor.sys, 'argv', ['verify_crossed']), \
                    patch.object(auditor, 'audit', side_effect=auditor.MemoryHeadroomError('synthetic stop')):
                with self.assertRaises(SystemExit) as caught:
                    auditor.main()
            self.assertEqual(caught.exception.code, 75)
            report = json.loads((out / 'integrity.json').read_text())
            self.assertEqual((report['status'], report['mismatches']), ('interrupted', 0))
            with patch.object(auditor, 'OUT', out), patch.object(auditor.sys, 'argv', ['verify_crossed']), \
                    patch.object(auditor, 'audit', side_effect=AssertionError('synthetic mismatch')):
                with self.assertRaises(AssertionError):
                    auditor.main()
            report = json.loads((out / 'integrity.json').read_text())
            self.assertEqual((report['status'], report['mismatches']), ('failed', 1))


if __name__ == '__main__':
    unittest.main()
