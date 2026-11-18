"""Offline tests for event integration; no AWS/HTTP or change operations."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent/'observation'))
import experiment as e
from test_observation import fixture, stamp


class ExperimentTests(unittest.TestCase):
    def test_hashes_distinct_and_match_application_definition(self):
        hashes = e.application_hashes()
        self.assertEqual(set(hashes), {'v1', 'v2'})
        self.assertNotEqual(hashes['v1'], hashes['v2'])
        self.assertTrue(all(len(h) == 64 for h in hashes.values()))

    def test_event_write_is_complete_and_duplicate_output_rejected(self):
        with TemporaryDirectory() as directory:
            path = Path(directory)/'events.jsonl'
            e.atomic_events(path, [dict(kind='change_started', run_id='synthetic')])
            self.assertEqual(e.rows(path)[0]['kind'], 'change_started')
            e.exclusive(Path(directory)/'config.json', {})
            with self.assertRaises(FileExistsError):
                e.exclusive(Path(directory)/'config.json', {})

    def stabilization(self, mutate=None):
        c, http, control, events = fixture()
        row = control[6]
        for h in http:
            h['finished_utc'] = h['timestamp_utc']
        if mutate:
            mutate(row, http)
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            e.exclusive(folder/'preparation.json', dict(controller=control[0]))
            (folder/'http.jsonl').write_text(''.join(json.dumps(h)+'\n' for h in http))
            pending = copy.deepcopy(c)
            pending['target_launch_template'] = dict(id=None, version=None)
            with patch.object(e.o, 'utc_now', return_value=stamp(61)):
                e.stabilize(pending, folder, events[:1], row)
            return (folder/'config.final.json').exists(), e.rows(folder/'events.jsonl')

    def test_stabilization_requires_terminal_capacity_and_all_backend_http(self):
        ready, events = self.stabilization()
        self.assertTrue(ready)
        self.assertEqual(events[-1]['kind'], 'stabilized')
        self.assertEqual(events[-1]['controller_sample_seq'], 7)
        for mutate in [lambda r,h: r.update(status='InProgress'),
                       lambda r,h: r['targets'][0].update(state='draining'),
                       lambda r,h: [x.update(errors=['timeout_5s']) for x in h]]:
            self.assertEqual(self.stabilization(mutate), (False, []))

    def test_integrated_discovery_uses_provider_start_time_before_sampling(self):
        c, _, _, _ = fixture()
        captured = {}
        original = e.o.controller_sample
        original_write = e.o.Records.write
        try:
            with TemporaryDirectory() as directory:
                def fake_original(config, events, query=None):
                    if query:
                        query(config, 'autoscaling', 'describe-instance-refreshes', [])
                        captured.update(events=copy.deepcopy(events))
                    return dict(errors=[], instances=[dict(id='i-old', lifecycle='InService', health='Healthy')], targets=[dict(id='i-old', state='healthy')])
                def fake_monitor(config, kind, path, folder, seconds):
                    e.o.controller_sample(config, [])
                    return True
                c['base_capacity'] = 1
                with patch.object(e.o, 'controller_sample', side_effect=fake_original), \
                     patch.object(e.o, 'utc_now', return_value=stamp(-60)), \
                     patch.object(e.o, 'aws_read', return_value=dict(InstanceRefreshes=[dict(InstanceRefreshId='ir-real-shape', StartTime=stamp(0))])), \
                     patch.object(e.o, 'monitor', side_effect=fake_monitor):
                    self.assertTrue(e.controller(c, Path(directory), 3600))
                self.assertEqual(captured['events'][0]['timestamp_utc'], stamp(0))
                self.assertEqual(captured['events'][0]['controller_id'], 'ir-real-shape')
        finally:
            e.o.controller_sample = original
            e.o.Records.write = original_write


if __name__ == '__main__':
    unittest.main()
