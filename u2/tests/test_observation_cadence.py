"""Concurrent five-second timeouts on a virtual clock. No sockets/subprocess/sleep."""
from concurrent.futures import ThreadPoolExecutor as RealPool
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import threading
import unittest
from unittest.mock import patch

from test_observation import O, fixture, stamp, EPOCH


class VirtualTimeoutClock:
    def __init__(self, pause=False):
        self.now = 0.0
        self.cv = threading.Condition()
        self.entries = []
        self.pause = pause
        self.paused = False
        self.cancelled = False

    def monotonic(self):
        with self.cv:
            return self.now

    def timeout(self, args, **kwargs):
        if kwargs["timeout"] != 5:
            raise AssertionError("HTTP timeout must stay at five seconds")
        with self.cv:
            entry = {"start": self.now, "due": self.now+5, "future": None}
            self.entries.append(entry)
            self.cv.notify_all()
            if not self.cv.wait_for(lambda: self.now+1e-8 >= entry["due"] or self.cancelled, timeout=2):
                raise AssertionError("Virtual scheduler stopped advancing")
        raise subprocess.TimeoutExpired("synthetic-curl-no-subprocess", 5)

    def notify(self, future):
        with self.cv:
            self.cv.notify_all()

    def advance(self, seconds):
        with self.cv:
            if self.pause and not self.paused and self.now >= 2:
                seconds += 10
                self.paused = True
            self.now = round(self.now+seconds, 9) # Stable virtual nanoseconds, not float accumulation drift.
            self.cv.notify_all()
            due = [entry for entry in self.entries if entry["due"] <= self.now+1e-8 and entry["future"] is not None]
            if not self.cv.wait_for(lambda: all(entry["future"].done() for entry in due), timeout=2):
                raise AssertionError("Due synthetic workers failed to finish")

    def drain(self):
        while True:
            with self.cv:
                pending = [entry for entry in self.entries if entry["future"] is not None and not entry["future"].done()]
                if not pending:
                    return
                delta = max(0.001, min(entry["due"] for entry in pending)-self.now)
            self.advance(delta)


def run_virtual_monitor(pause):
    config, *_ = fixture()
    clock = VirtualTimeoutClock(pause)
    sizes = []
    class Executor:
        def __init__(self, max_workers):
            sizes.append(max_workers)
            self.pool = RealPool(max_workers=max_workers)
        def __enter__(self): return self
        def submit(self, call):
            with clock.cv:
                index = len(clock.entries)
            future = self.pool.submit(call)
            with clock.cv:
                if not clock.cv.wait_for(lambda: len(clock.entries) > index, timeout=2):
                    raise AssertionError("Worker never started")
                deadline = clock.entries[index]["due"]
                class ScheduledFuture:
                    def done(self): return future.done()
                    def result(self):
                        # monitor waits for outstanding workers before leaving its
                        # executor context. Advance virtual time during that wait.
                        if not future.done():
                            clock.advance(max(0.001, deadline-clock.monotonic()))
                        return future.result(timeout=2)
                wrapped = ScheduledFuture()
                clock.entries[index]["future"] = wrapped
            future.add_done_callback(clock.notify)
            return wrapped
        def __exit__(self, *args):
            try:
                clock.drain()
            finally:
                with clock.cv:
                    clock.cancelled = True
                    clock.cv.notify_all()
                self.pool.shutdown(wait=True)
    actual_sample = O.http_sample
    with TemporaryDirectory() as directory:
        with patch.object(O, "ThreadPoolExecutor", Executor), patch.object(O, "read_events", return_value=[]), \
             patch.object(O, "http_sample", side_effect=lambda c: actual_sample(c, clock.timeout)), \
             patch.object(O.time, "monotonic", side_effect=clock.monotonic), \
             patch.object(O.time, "time", side_effect=lambda: EPOCH+clock.monotonic()), \
             patch.object(O.time, "sleep", side_effect=clock.advance), \
             patch.object(O, "utc_now", side_effect=lambda: stamp(clock.monotonic())):
            result = O.monitor(config, "http", "unused", directory, 16 if pause else 10)
        rows = [json.loads(line) for line in (Path(directory)/"http.jsonl").read_text().splitlines()]
        csv_text = (Path(directory)/"http.csv").read_text()
    return result, rows, clock.entries, csv_text, sizes


class ConcurrentCadenceTests(unittest.TestCase):
    def test_five_second_timeouts_keep_two_second_launch_cadence(self):
        result, rows, entries, csv_text, sizes = run_virtual_monitor(False)
        self.assertFalse(result) # Deliberately short synthetic window, never an accepted trial.
        self.assertEqual(sizes, [3])
        starts = [entry["start"] for entry in entries]
        self.assertEqual(len(starts), 5)
        for actual, expected in zip(starts, [0, 2, 4, 6, 8]):
            self.assertAlmostEqual(actual, expected, places=4)
        samples = [row for row in rows if row["kind"] == "http"]
        self.assertEqual(len(samples), 5)
        self.assertTrue(all(row["errors"] == ["timeout_5s"] for row in samples))
        self.assertTrue(all(abs(row["duration_seconds"]-5) < 0.001 for row in samples))
        self.assertEqual(csv_text.count("timeout_5s"), 5)

    def test_scheduler_pause_records_missing_slots_without_retry_burst(self):
        result, rows, entries, csv_text, _ = run_virtual_monitor(True)
        self.assertFalse(result)
        samples = [row for row in rows if row["kind"] == "http"]
        missed = [row for row in samples if "missed_schedule_no_retry" in row["errors"]]
        self.assertEqual(len(samples), 8) # Every scheduled slot 0..14 remains present.
        self.assertEqual(len(missed), 4) # Slots 4,6,8,10 were missed, not retried.
        self.assertEqual(len(entries), 4)
        self.assertEqual(sorted(row["seq"] for row in samples), list(range(1, 9)))
        coverage = O.coverage(samples, EPOCH, EPOCH+14, O.HTTP_GAP, O.HTTP_INTERVAL)
        self.assertFalse(coverage["complete"])
        self.assertGreater(coverage["max_gap_seconds"], 7)
        self.assertEqual(csv_text.count("missed_schedule_no_retry"), 4)


if __name__ == "__main__":
    unittest.main()
