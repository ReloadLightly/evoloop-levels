"""Protocol 010 scientific invariants with synthetic fixtures, never CA evidence."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from evoloop.engine import ROOT, digest
from scripts import coverage_assay as assay


class CoverageAssayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = json.loads((ROOT / 'configs/coverage-v1.json').read_text())

    @staticmethod
    def loop(core, identity, snapshot=True, status='complete_single_core_component'):
        return {'core': list(core), 'genotype': identity,
                'isolation_snapshot': np.array([[2, 1], [1, 2]], dtype=np.uint8)
                if snapshot else None,
                'extraction_status': status, 'extraction_bbox': list(core)}

    @staticmethod
    def samples(core, identities, start=400):
        return [{'t': start + 20 * i,
                 'cores': [] if identity == 'absent' else
                 [{'core': list(core), 'identity': identity}],
                 'boundary_activity': False}
                for i, identity in enumerate(identities)]

    def selected(self, identity=None):
        _, selected = assay.select_strata(
            [self.loop([1, 2, 4, 4], identity)], ['4:registered'], 'A-development-0-D', 400)
        return selected[0]

    def test_three_classes_choose_before_extraction_and_preserve_empty_strata(self):
        loops = [self.loop([7, 2, 4, 4], '4:registered'),
                 self.loop([1, 2, 5, 4], '4:registered'),
                 self.loop([1, 2, 4, 4], '4:registered', False, 'shared_component'),
                 self.loop([2, 3, 4, 4], '4:omitted')]
        strata, selected = assay.select_strata(loops, ['4:registered'], 'world', 400)
        by_class = {s['source_class']: s for s in strata}
        self.assertEqual(len(strata), 3)
        self.assertEqual(by_class['scored']['available_cores'], 3)
        self.assertEqual(by_class['scored']['selected_cores'], 1)
        self.assertEqual(by_class['unknown_identity']['available_cores'], 0)
        self.assertEqual(by_class['unknown_identity']['selected_cores'], 0)
        chosen = next(o for o in selected if o['source_class'] == 'scored')
        self.assertEqual(chosen['core'], [1, 2, 4, 4])
        self.assertEqual(len(selected), 2)

    def test_matured_delayed_identity_does_not_change_unknown_source_class(self):
        target = self.selected()
        original = copy.deepcopy(target)
        samples = self.samples(target['core'], [None, None, '4:registered',
                                                  '4:registered', '4:registered', '4:registered'])
        delay, snapshot = assay.delay_selection(
            target, [self.loop(target['core'], '4:registered')], samples, 500,
            ['4:registered'], self.cfg)
        self.assertEqual(target, original)
        self.assertEqual(target['source_class'], 'unknown_identity')
        self.assertEqual(delay['delayed_identity'], '4:registered')
        self.assertEqual(delay['delayed_class'], 'scored')
        self.assertEqual(delay['extraction_status'], 'eligible')
        self.assertIsNotNone(snapshot)

    def test_sampled_loss_followed_by_recurrence_remains_ineligible(self):
        target = self.selected('4:registered')
        samples = self.samples(target['core'], ['4:registered', 'absent',
                                                  '4:registered', '4:registered',
                                                  '4:registered', '4:registered'])
        delay, snapshot = assay.delay_selection(
            target, [self.loop(target['core'], '4:registered')], samples, 500,
            ['4:registered'], self.cfg)
        self.assertEqual(delay['extraction_status'], 'sampled_target_lost')
        self.assertTrue(delay['delayed_core_present'])
        self.assertIsNone(snapshot)
        cfg = copy.deepcopy(self.cfg)
        cfg['native']['continuation_horizon_from_source'] = 100
        labels = assay.native_labels(target, samples, cfg)
        self.assertEqual(labels['fixed_core_first_loss_t'], 420)
        self.assertEqual(labels['fixed_core_first_recurrence_t'], 440)

    def test_unknown_identity_preserves_core_and_missing_word_observation(self):
        target = self.selected()
        samples = self.samples(target['core'], [None] * 6)
        delay, snapshot = assay.delay_selection(
            target, [self.loop(target['core'], None)], samples, 500,
            ['4:registered'], self.cfg)
        self.assertEqual(delay['extraction_status'], 'eligible')
        self.assertIsNone(delay['delayed_identity'])
        self.assertIsNotNone(snapshot)
        cfg = copy.deepcopy(self.cfg)
        cfg['native']['continuation_horizon_from_source'] = 100
        labels = assay.native_labels(target, samples, cfg)
        self.assertIsNone(labels['fixed_core_first_loss_t'])
        self.assertTrue(labels['endpoint_core_present'])
        self.assertIsNone(labels['endpoint_identity'])
        self.assertEqual(labels['matching_word_status'], 'unknown_source_word')
        self.assertIsNone(labels['matching_word_elsewhere_first_t'])

    def test_shared_and_oversize_selections_remain_exclusions(self):
        target = self.selected('4:registered')
        samples = self.samples(target['core'], ['4:registered'])
        shared = self.loop(target['core'], '4:registered', False, 'shared_component')
        delay, snapshot = assay.delay_selection(target, [shared], samples, 400,
                                                ['4:registered'], self.cfg)
        self.assertEqual(delay['extraction_status'], 'shared_component')
        self.assertIsNone(snapshot)
        oversize = self.loop(target['core'], '4:registered')
        oversize['isolation_snapshot'] = np.ones((173, 1), dtype=np.uint8)
        delay, snapshot = assay.delay_selection(target, [oversize], samples, 400,
                                                ['4:registered'], self.cfg)
        self.assertEqual(delay['extraction_status'], 'component_too_large')
        self.assertIsNone(snapshot)

    def test_acquisition_initializes_search_from_measured_delayed_identity(self):
        """Exercise the orchestration link; a source class must not add an edge."""
        target = self.selected()
        snapshot = self.loop(target['core'], '4:registered')['isolation_snapshot']
        unknown = self.loop(target['core'], None)['isolation_snapshot']
        target.update(run_id='world', state='V01', treatment='D')
        target['delays'] = [{'delay': delay, 'delayed_identity': identity,
                             'extraction_status': 'eligible',
                             'snapshot_file': f'snapshot-{delay}.npz',
                             'snapshot_hash': digest(snapshot)}
                            for delay, identity in ((0, None), (100, '4:registered'))]
        report = {'status': 'unresolved', 'confirmation': None, 'truncations': [],
                  'nodes': [{'node': 0, 'outcome': {'children': [],
                                                  'status': 'unresolved_at_horizon'}}]}
        manifest = {'config': self.cfg, 'registry': ['4:registered'],
                    'experiment_id': 'synthetic', 'phase_controls': [],
                    'runs': [{'run_id': 'world'}]}
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            readiness_bytes = b'{}\n'
            (out / 'readiness.json').write_bytes(readiness_bytes)
            assay.atomic_json(out / 'benchmark.json',
                              {'status': 'passed', 'readiness_sha256': assay.sha(out / 'readiness.json')})
            assay.atomic_npz(out / 'snapshot-0.npz', snapshot=unknown)
            assay.atomic_npz(out / 'snapshot-100.npz', snapshot=snapshot)
            result_dir = out / 'worlds/world'
            result_dir.mkdir(parents=True)
            (result_dir / 'result.json').write_text('{}\n')
            with patch.object(assay, 'OUT', out), \
                    patch.object(assay, 'readiness', return_value=manifest), \
                    patch.object(assay.subprocess, 'check_output', return_value=readiness_bytes), \
                    patch.object(assay, 'world', return_value={'observations': [target]}), \
                    patch.object(assay, 'search_one', return_value=report) as search, \
                    patch.object(assay, 'analyze'):
                assay.acquire('synthetic-readiness-commit')
            self.assertEqual([call.args[1] for call in search.call_args_list],
                             [None, '4:registered'])
            saved = json.loads((out / 'recovery.json').read_text())['observations'][0]
            self.assertEqual(saved['source_class'], 'unknown_identity')
            self.assertIsNone(saved['source_identity'])

    def test_unknown_root_needs_known_descendant_then_two_preserving_edges(self):
        cfg = copy.deepcopy(self.cfg)
        cfg['search']['max_depth'] = 2
        def generation(snapshot, config):
            marker = int(snapshot[0, 0])
            child = np.array([[marker + 1]], dtype=np.uint8)
            children = [{'identity': '4:registered', 'detached_t': 10,
                         'core': [1, 2, 4, 4], 'snapshot_hash': digest(child),
                         'size_eligible': True}] if marker < 3 else []
            return {'children': children}, {'child0': child} if children else {}
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            (out / 'manifest.json').write_text('{}\n')
            (out / 'readiness.json').write_text('{}\n')
            with patch.object(assay, 'OUT', out), \
                    patch.object(assay, 'offspring_generation', side_effect=generation):
                root = np.array([[0]], dtype=np.uint8)
                known = assay.search_one(root, '4:registered', {'config': cfg}, out / 'known')
                unknown = assay.search_one(root, None, {'config': cfg}, out / 'unknown')
            self.assertEqual(known['status'], 'confirmed')
            self.assertEqual(known['confirmation']['path'], [0, 0])
            self.assertEqual(unknown['status'], 'unresolved')
            self.assertEqual(unknown['nodes'][0]['input_identity'], None)
            self.assertTrue(any(c['reason'] == 'depth_limit' for c in unknown['truncations']))

    def test_resume_rejects_mutated_bytes_bindings_and_extra_artifacts(self):
        binding = {'snapshot_hash': 'synthetic', 'input_identity': None}
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            self.assertFalse(assay.verify_receipt(folder, binding))
            assay.atomic_json(folder / 'result.json', {'status': 'unresolved'})
            assay.receipt(folder, binding)
            self.assertTrue(assay.verify_receipt(folder, binding))
            with self.assertRaisesRegex(ValueError, 'binding changed'):
                assay.verify_receipt(folder, {**binding, 'input_identity': '4:registered'})
            original = (folder / 'result.json').read_bytes()
            (folder / 'result.json').write_bytes(original + b' ')
            with self.assertRaisesRegex(ValueError, 'artifacts changed'):
                assay.verify_receipt(folder, binding)
            (folder / 'result.json').write_bytes(original)
            (folder / 'unexpected.npz').write_bytes(b'new artifact')
            with self.assertRaisesRegex(ValueError, 'artifacts changed'):
                assay.verify_receipt(folder, binding)

    @staticmethod
    def recovery_observation(index, source_class='scored', zero=True, later=True,
                             state='A'):
        report = {'status': 'confirmed', 'generation_simulations': 2,
                  'confirmation': {'identity': '4:registered'}, 'truncations': [],
                  'nodes': [{'node': 0, 'outcome': {'status': 'offspring_observed',
                                                  'children': [{}]}}]}
        delays = []
        for delay, success in ((0, zero), (100, later), (400, later)):
            delays.append({'delay': delay, 'transmission_confirmed': success,
                           'extraction_status': 'eligible' if success else 'sampled_target_lost',
                           'root_reproduction_observed': True if success else None,
                           'status': 'confirmed_stable_descendant' if success else 'sampled_target_lost',
                           'confirmed_identity_in_registry': True if success else None,
                           'same_as_source_identity': success if source_class == 'scored' else None,
                           'outcome': report if success else None, 'search_censoring': []})
        return {'observation_id': f'synthetic-{index}', 'run_id': 'world', 'state': state,
                'treatment': 'D', 'source_time': 400, 'source_class': source_class,
                'native_continuation': {'fixed_core_first_loss_t': None,
                                        'fixed_core_first_recurrence_t': None},
                'delays': delays}

    def summary_fixture(self, observations, states=('A',)):
        cfg = copy.deepcopy(self.cfg)
        cfg['states'] = list(states)
        manifest = {'config': cfg, 'experiment_id': 'synthetic', 'registry': ['4:registered'],
                    'runs': [{'run_id': 'world', 'condition': {'id': 'development-0'},
                              'split': 'development'}]}
        report = self.recovery_observation(0)['delays'][0]['outcome']
        controls = [{'identity': '4:registered', 'outcome': copy.deepcopy(report)}
                    for _ in range(30)]
        recovery = {'observations': observations, 'baselines': controls, 'worlds': ['world']}
        return recovery, manifest

    def test_gate_uses_exact_delay_zero_denominator_and_union_is_once(self):
        observations = [self.recovery_observation(i, zero=i < 9) for i in range(10)]
        observations.append(self.recovery_observation(10, source_class='unknown_identity'))
        recovery, manifest = self.summary_fixture(observations)
        summary = assay.summarize(recovery, manifest)
        self.assertEqual(summary['gate_status'], 'passed')
        self.assertEqual(summary['scored_delay0']['confirmed'], 9)
        self.assertEqual(summary['scored_delay0']['selected'], 10)
        self.assertEqual(summary['omitted']['confirmed'], 1)
        self.assertEqual(summary['omitted']['confirmed_delays'], 3)
        self.assertEqual(summary['omitted']['planned_delays'], 3)
        observations[8] = self.recovery_observation(8, zero=False)
        summary = assay.summarize(recovery, manifest)
        self.assertEqual(summary['gate_status'], 'failed')
        self.assertEqual(summary['scored_delay0']['confirmed'], 8)
        self.assertEqual(summary['scored_delay0']['selected'], 10)

    def test_empty_scored_state_is_unresolved_even_with_omitted_recovery(self):
        recovery, manifest = self.summary_fixture(
            [self.recovery_observation(0),
             self.recovery_observation(1, source_class='valid_unregistered', state='B')],
            states=('A', 'B'))
        summary = assay.summarize(recovery, manifest)
        self.assertEqual(summary['gate_status'], 'unresolved')
        self.assertIsNone(summary['gate_checks']['each_state_scored_delay0'])
        self.assertTrue(summary['omitted_recoverability_observed'])

    def test_empty_scored_state_remains_unresolved_with_failed_control_check(self):
        recovery, manifest = self.summary_fixture([self.recovery_observation(0)],
                                                 states=('A', 'B'))
        recovery['baselines'][-1]['outcome']['status'] = 'unresolved'
        summary = assay.summarize(recovery, manifest)
        self.assertEqual(summary['gate_status'], 'unresolved')
        self.assertFalse(summary['gate_checks']['phase_controls'])


if __name__ == '__main__':
    unittest.main()
