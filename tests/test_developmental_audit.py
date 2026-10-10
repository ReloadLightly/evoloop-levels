"""Independent resolved-share, missingness and censoring fixtures; no acquisition."""
import copy
import json
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

import numpy as np

from scripts import verify_developmental as auditor


class DevelopmentalAuditTests(unittest.TestCase):
    @staticmethod
    def source(status='eligible', confirmed=False, identity=None, searched=True):
        return {'extraction_status': status, 'transmission_confirmed': confirmed,
                'confirmed_identity': identity, 'search_dir': 'searches/x' if searched else None}

    def test_unknown_recovery_counts_source_once_without_retroassigned_identity(self):
        unknown = self.source(confirmed=True, identity='stable:word')
        unknown['source_identity'] = None
        unknown['source_class'] = 'unknown_identity'
        unresolved = self.source()
        self.assertEqual(auditor.source_partition([unknown, unresolved]), {'Q': 1, 'R': 1, 'C': 2})
        self.assertIsNone(unknown['source_identity'])

    def test_shared_oversized_nonconfirming_and_unsearched_remain_R(self):
        sources = [self.source('shared_component', searched=False),
                   self.source('component_too_large', searched=False),
                   self.source(), self.source(searched=False)]
        self.assertEqual(auditor.source_partition(sources), {'Q': 0, 'R': 4, 'C': 4})
        self.assertEqual(auditor.source_partition([]), {'Q': 0, 'R': 0, 'C': 0})
        sources[0]['transmission_confirmed'] = True
        sources[0]['confirmed_identity'] = 'invented'
        with self.assertRaises(AssertionError):
            auditor.source_partition(sources)

    def test_integer_threshold_preserves_exact_boundary(self):
        self.assertTrue(auditor.exact_threshold(4, 5, '4/5'))
        self.assertFalse(auditor.exact_threshold(7999999999999999, 10000000000000000, '4/5'))
        self.assertIsNone(auditor.exact_threshold(0, 0, '4/5'))

    def test_zero_is_observation_and_missing_denominator_is_none(self):
        self.assertEqual(auditor.fraction_record(0, 10), {'numerator': 0, 'denominator': 1})
        self.assertIsNone(auditor.fraction_record(0, 0))
        self.assertEqual(auditor.fraction_record(8, 10), {'numerator': 4, 'denominator': 5})

    def test_retention_uses_crossed_envelope_terms(self):
        bounds = auditor.bounded_retention({'Q': 3, 'R': 2, 'C': 5}, {'Q': 4, 'R': 2, 'C': 6})
        self.assertEqual(bounds, {'lower': {'numerator': 1, 'denominator': 2},
            'upper': {'numerator': 5, 'denominator': 4}, 'status': 'finite'})

    def test_zero_undisturbed_confirmation_retains_unbounded_upper(self):
        bounds = auditor.bounded_retention({'Q': 2, 'R': 1, 'C': 3}, {'Q': 0, 'R': 4, 'C': 4})
        self.assertEqual(bounds['lower'], {'numerator': 1, 'denominator': 2})
        self.assertIsNone(bounds['upper'])
        self.assertEqual(bounds['status'], 'unbounded_upper')

    def test_absent_undisturbed_structure_makes_ratio_undefined(self):
        bounds = auditor.bounded_retention({'Q': 0, 'R': 0, 'C': 0}, {'Q': 0, 'R': 0, 'C': 0})
        self.assertEqual(bounds, {'lower': None, 'upper': None,
                                 'status': 'undefined_no_undisturbed_detected_cores'})
        with self.assertRaises(AssertionError):
            auditor.bounded_retention({'Q': 2, 'R': 0, 'C': 1}, {'Q': 1, 'R': 0, 'C': 1})

    def test_panel_averages_exact_condition_ratios_without_pooling(self):
        conditions = [({'Q': 1, 'R': 0, 'C': 1}, {'Q': 1, 'R': 0, 'C': 1}),
                      ({'Q': 1, 'R': 0, 'C': 1}, {'Q': 9, 'R': 0, 'C': 9})]
        panel = auditor.average_retention(conditions)
        self.assertEqual(panel['lower'], {'numerator': 5, 'denominator': 9})
        self.assertEqual(panel['upper'], panel['lower'])
        self.assertNotEqual(panel['lower'], auditor.fraction_record(2, 10))

    def test_overlap_and_ties_fail_strict_superiority_missing_bounds_unresolved(self):
        def bound(n, d):
            return {'lower': auditor.fraction_record(n, d), 'upper': auditor.fraction_record(n, d)}
        self.assertTrue(auditor.strict_superiority(bound(2, 1), [bound(1, 1), bound(3, 2)]))
        self.assertFalse(auditor.strict_superiority(bound(1, 1), [bound(1, 1)]))
        self.assertFalse(auditor.strict_superiority(bound(1, 1), [bound(2, 1)]))
        self.assertIsNone(auditor.strict_superiority(bound(2, 1), [{'upper': None}]))

    def test_shared_component_rejection_is_independently_checked(self):
        grid = np.zeros((10, 10), np.uint8)
        grid[2, 2:7] = 1
        loops = [{'core': [3, x, 3, 3], 'isolation_snapshot': None,
                  'extraction_status': 'shared_component'} for x in (2, 6)]
        counts = Counter()
        auditor.independent_extraction(grid, loops, counts)
        self.assertEqual(counts['shared_components_verified'], 2)
        loops[0]['extraction_status'] = 'complete_single_core_component'
        with self.assertRaises(AssertionError):
            auditor.independent_extraction(grid, loops, Counter())

    def test_noncontractible_component_is_not_an_eligible_zero(self):
        grid = np.zeros((10, 10), np.uint8)
        grid[:, 2] = 1
        loop = {'core': [3, 2, 3, 3], 'isolation_snapshot': None,
                'extraction_status': 'noncontractible_component'}
        counts = Counter()
        auditor.independent_extraction(grid, [loop], counts)
        self.assertEqual(counts['noncontractible_components_verified'], 1)
        loop['extraction_status'] = 'shared_component'
        with self.assertRaises(AssertionError):
            auditor.independent_extraction(grid, [loop], Counter())

    def test_cache_key_requires_whole_input_identity_endpoint_and_limits(self):
        cfg = {'generation_horizon': 1600, 'stable_transmissions': 2}
        component = np.array([[0, 1], [4, 7]], np.uint8)
        key = auditor.cache_key(component, None, False, cfg)
        self.assertEqual(key, auditor.cache_key(component.copy(), None, False, dict(reversed(list(cfg.items())))))
        altered = component.copy()
        altered[0, 0] = 1
        other_keys = [auditor.cache_key(altered, None, False, cfg),
                      auditor.cache_key(component, 'known', False, cfg),
                      auditor.cache_key(component, None, True, cfg),
                      auditor.cache_key(component, None, False, {**cfg, 'generation_horizon': 1601})]
        self.assertTrue(all(other != key for other in other_keys))

    def test_unsearched_unknown_remains_unresolved_with_reproduction_missing(self):
        row = {'extraction_status': 'eligible', 'source_identity': None, 'search_dir': None,
            'status': 'unsearched_budget', 'root_reproduction_observed': None,
            'isolated_grid_extinction_nodes': [], 'transmission_confirmed': False,
            'confirmed_identity': None, 'confirmed_identity_in_registry': None,
            'same_as_source_identity': None, 'search_censoring': [],
            'inheritance_unresolved': True, 'ancestry_ambiguous': True, 'benefit_pending': None}
        auditor.verify_source_labels(row, {'offspring_per_generation': 3}, [])
        row['root_reproduction_observed'] = False
        with self.assertRaises(AssertionError):
            auditor.verify_source_labels(row, {'offspring_per_generation': 3}, [])

    def test_independent_summary_matches_runner_and_failed_gate_cannot_be_rescued(self):
        from scripts import developmental_measure as runner
        cfg = json.loads((auditor.ROOT / 'configs/developmental-v1.json').read_text())
        cfg['states'] = ['A', 'B']
        manifest = {'config': cfg}
        rows = []
        for index in range(10):
            confirmed = index < 9
            row = self.source(confirmed=confirmed, identity='registered' if confirmed else None,
                              searched=confirmed)
            row.update(state='A', treatment='D' if index < 5 else 'U', source_class='scored',
                       search_key='input' if confirmed else None, status='confirmed' if confirmed else 'unsearched_budget',
                       root_reproduction_observed=True if confirmed else None)
            rows.append(row)
        controls = [{'kind': 'phase', 'transmission_confirmed': True, 'search_key': 'input'} for _ in range(30)]
        controls.extend({'kind': 'omitted', 'transmission_confirmed': True, 'search_key': 'input'} for _ in range(3))
        worlds = [{'sources': rows, 'snapshot_counts': [{'t': 0, 'Q': 9, 'R': 1, 'C': 10}]}]
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            search = out / 'searches/input'
            search.mkdir(parents=True)
            (search / 'result.json').write_text('{"generation_simulations":2}')
            with patch.object(auditor, 'OUT', out), patch.object(runner, 'OUT', out):
                expected = auditor.analysis_summary(manifest, worlds, controls)
                self.assertEqual(expected, runner.summary(manifest, worlds, controls))
                self.assertEqual(expected['gate_status'], 'unresolved')
                self.assertTrue(expected['gate_checks']['scored_overall'])
                self.assertIsNone(expected['gate_checks']['scored_per_state'])
                controls[0]['transmission_confirmed'] = False
                self.assertEqual(auditor.analysis_summary(manifest, worlds, controls)['gate_status'], 'failed')
                cfg['states'] = ['A']
                controls[0]['transmission_confirmed'] = True
                rows[8]['transmission_confirmed'] = False
                rows[8]['confirmed_identity'] = None
                failed = auditor.analysis_summary(manifest, worlds, controls)
                self.assertFalse(failed['gate_checks']['scored_overall'])
                self.assertEqual(failed['gate_status'], 'failed')
                self.assertEqual(failed['prior_coverage_gate'], 'failed; unchanged')

    def test_memory_stop_records_interruption_and_zero_mismatches(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            with patch.object(auditor, 'OUT', out), patch.object(auditor.sys, 'argv', ['verify_developmental']), \
                    patch.object(auditor, 'audit', side_effect=auditor.MemoryHeadroomError('synthetic stop')):
                with self.assertRaises(SystemExit) as caught:
                    auditor.main()
            self.assertEqual(caught.exception.code, 75)
            report = json.loads((out / 'integrity.json').read_text())
            self.assertEqual(report['status'], 'interrupted')
            self.assertEqual(report['mismatches'], 0)


if __name__ == '__main__':
    unittest.main()
