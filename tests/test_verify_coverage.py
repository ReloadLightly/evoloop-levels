"""Independent coverage-audit endpoint and denominator fixtures; no acquisition."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import verify_coverage as auditor
from scripts.verify_coverage import exact_gate, native_labels, selected_counts


class CoverageAuditTests(unittest.TestCase):
    def test_unknown_identity_is_not_core_loss_and_word_missing_is_not_zero(self):
        core = [1, 2, 4, 4]
        samples = [{'t': t, 'cores': [{'core': core, 'identity': None}],
                    'boundary_activity': False} for t in (0, 20, 40)]
        labels = native_labels({'t': 0, 'core': core, 'identity': None}, samples, 40, 20)
        self.assertIsNone(labels['fixed_core_first_loss_t'])
        self.assertTrue(labels['endpoint_core_present'])
        self.assertEqual(labels['matching_word_status'], 'unknown_source_word')
        self.assertIsNone(labels['matching_word_elsewhere_first_t'])

    def test_recurrence_does_not_erase_sampled_loss(self):
        core = [1, 2, 4, 4]
        samples = [{'t': 0, 'cores': [{'core': core, 'identity': '4:word'}], 'boundary_activity': False},
                   {'t': 20, 'cores': [], 'boundary_activity': True},
                   {'t': 40, 'cores': [{'core': core, 'identity': None}], 'boundary_activity': False}]
        labels = native_labels({'t': 0, 'core': core, 'identity': '4:word'}, samples, 40, 20)
        self.assertEqual(labels['fixed_core_first_loss_t'], 20)
        self.assertEqual(labels['fixed_core_first_recurrence_t'], 40)
        self.assertEqual(labels['boundary_first_t'], 20)
        self.assertEqual(labels['matching_word_status'], 'observed')

    @staticmethod
    def observation(state, success, later_success=False):
        return {'state': state, 'delays': [
            {'delay': 0, 'outcome': {'status': 'confirmed'} if success else None},
            {'delay': 100, 'outcome': {'status': 'confirmed'} if later_success else None},
            {'delay': 400, 'outcome': None}]}

    def test_exact_threshold_and_all_selected_denominator(self):
        controls = [{'outcome': {'status': 'confirmed'}} for _ in range(30)]
        scored = [self.observation('A', i < 9, True) for i in range(10)]
        gate = exact_gate(scored, controls, ['A'])
        self.assertTrue(gate['passed'])
        self.assertEqual((gate['scored_delay0_confirmed'], gate['scored_selected']), (9, 10))
        scored[8] = self.observation('A', False, True)
        gate = exact_gate(scored, controls, ['A'])
        self.assertFalse(gate['passed'])
        self.assertEqual(gate['scored_delay0_confirmed'], 8)

    def test_empty_state_gate_is_unresolved_and_phase_failure_is_failure(self):
        controls = [{'outcome': {'status': 'confirmed'}} for _ in range(30)]
        gate = exact_gate([self.observation('A', True)], controls, ['A', 'B'])
        self.assertIsNone(gate['passed'])
        self.assertIsNone(gate['checks']['each_starting_state_delay0'])
        controls[-1]['outcome']['status'] = 'unresolved'
        self.assertIsNone(exact_gate([self.observation('A', True)], controls, ['A', 'B'])['passed'])
        self.assertFalse(exact_gate([self.observation('A', True)], controls, ['A'])['passed'])

    def test_union_preserves_all_delays_and_does_not_count_repeated_success(self):
        one = self.observation('A', True, True)
        one['delays'][2]['outcome'] = {'status': 'confirmed'}
        for d in one['delays']:
            d['extraction_status'] = 'eligible'
        missing = self.observation('A', False)
        for d in missing['delays']:
            d['extraction_status'] = 'sampled_target_lost'
        summary = selected_counts([one, missing])
        self.assertEqual(summary['confirmed_any_delay'], 1)
        self.assertEqual(summary['confirmed_delays'], 3)
        self.assertEqual((summary['selected'], summary['planned_delays']), (2, 6))

    def test_memory_stop_is_interrupted_and_not_an_evidence_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            with patch.object(auditor, 'OUT', out), \
                    patch.object(auditor.sys, 'argv', ['verify_coverage']), \
                    patch.object(auditor, 'audit', side_effect=auditor.MemoryHeadroomError('synthetic memory stop')):
                with self.assertRaises(SystemExit) as raised:
                    auditor.main()
            self.assertEqual(raised.exception.code, 75)
            report = json.loads((out / 'integrity.json').read_text())
            self.assertEqual(report['status'], 'interrupted')
            self.assertEqual(report['mismatches'], 0)

    def test_independent_summary_matches_runner_with_censoring_and_missingness(self):
        """Compare two derivations on synthetic data without running the CA."""
        from scripts import coverage_assay as runner
        cfg = json.loads((auditor.ROOT / 'configs/coverage-v1.json').read_text())
        cfg['states'] = ['A', 'B']
        manifest = {'config': cfg, 'registry': ['4:registered'], 'experiment_id': 'synthetic',
                    'runs': [{'run_id': 'world', 'condition': {'id': 'development-0'}, 'split': 'development'}]}
        positive = {'status': 'confirmed', 'confirmation': {'identity': '4:registered'},
                    'generation_simulations': 2, 'truncations': [],
                    'nodes': [{'node': i, 'outcome': {'status': 'offspring_observed', 'children': [{}]}}
                              for i in range(2)]}
        negative = {'status': 'unresolved', 'confirmation': None, 'generation_simulations': 1,
                    'truncations': [{'reason': 'simulation_budget', 'depth': 2, 'path': [0]}],
                    'nodes': [{'node': 0, 'outcome': {'status': 'unresolved_at_horizon', 'children': []}}]}
        observations = []
        for index, label in enumerate(('scored', 'valid_unregistered', 'unknown_identity')):
            identity = '4:registered' if label == 'scored' else '4:other' if label == 'valid_unregistered' else None
            delays = []
            for delay in (0, 100, 400):
                report = copy.deepcopy(positive if delay == 100 else negative) if delay != 400 else None
                delays.append({'delay': delay, 'outcome': report,
                    'status': 'confirmed_stable_descendant' if delay == 100 else 'unresolved_search' if delay == 0 else 'sampled_target_lost',
                    'extraction_status': 'eligible' if report is not None else 'sampled_target_lost',
                    **runner.search_fields(report, identity, manifest['registry'])})
            observations.append({'run_id': 'world', 'state': 'A', 'treatment': 'D', 'source_time': 400,
                'source_class': label, 'source_identity': identity, 'delays': delays,
                'native_continuation': {'fixed_core_first_loss_t': 420, 'fixed_core_first_recurrence_t': 440}})
        baselines = [{'identity': '4:registered', 'outcome': copy.deepcopy(positive)} for _ in range(30)]
        baselines[0]['outcome'] = copy.deepcopy(negative)
        recovery = {'worlds': ['world'], 'observations': observations, 'baselines': baselines}
        results = {'world': {'strata': [{'available_cores': 0, 'selected_cores': 0}]}}
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            (out / 'recovery.json').write_text(json.dumps(recovery))
            (out / 'readiness.json').write_text('{}\n')
            with patch.object(auditor, 'OUT', out):
                expected = auditor.analysis_summary(recovery, manifest, results)
                actual = runner.summarize(recovery, manifest)
                actual.update(strata=results['world']['strata'],
                              recovery_sha256=auditor.sha(out / 'recovery.json'),
                              readiness_sha256=auditor.sha(out / 'readiness.json'))
        self.assertEqual(expected, actual)
        self.assertEqual(expected['gate_status'], 'unresolved')
        self.assertEqual(expected['omitted']['confirmed'], 2)
        self.assertEqual(expected['omitted']['planned_delays'], 6)
        self.assertEqual(expected['phase_control_search_censoring']['generation_horizon'], 1)


if __name__ == '__main__':
    unittest.main()
