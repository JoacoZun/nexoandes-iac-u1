"""Synthetic evidence only. No HTTP, AWS, subprocess or clock waits are executed."""
import copy
import csv
import importlib.util
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

BASE = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


O = module("u2_observation", BASE / "observation/observe.py")
N = module("u2_network_probe", BASE / "scripts/ci_network_probe.py")
EPOCH = 1893456000 # 2030-01-01, synthetic only.
OLD = ["i-00000000000000001", "i-00000000000000002"]
NEW = ["i-00000000000000003", "i-00000000000000004"]


def stamp(seconds):
    return O.datetime.fromtimestamp(EPOCH+seconds, O.timezone.utc).isoformat()


def fixture():
    c = {
        "run_id": "synthetic-test-only", "operation_kind": "update", "region": "us-east-1",
        "account_id": "000000000000", "asg_name": "synthetic-asg",
        "target_group_arn": "arn:aws:elasticloadbalancing:us-east-1:000000000000:targetgroup/synthetic/0000000000000000",
        "endpoint": "http://synthetic.invalid", "identity": {"project": "NexoAndes", "phase": "U2", "provider": "aws", "x": 8, "student": "a008", "course": "c99"},
        "releases": {"v1": {"build_ref": "synthetic-v1", "artifact_sha256": "1"*64}, "v2": {"build_ref": "synthetic-v2", "artifact_sha256": "2"*64}},
        "from_version": "v1", "target_version": "v2", "source_launch_template": {"id": "lt-00000000000000000", "version": "1"}, "target_launch_template": {"id": "lt-00000000000000000", "version": "2"},
        "base_capacity": 2, "temporary_capacity": 1, "controller_owner": "terraform_aws_provider"}
    http = []
    for seq, t in enumerate(range(-60, 182, 2), 1):
        version = "v1" if t < 20 else "v2"
        ids = OLD if t < 20 else NEW
        checks = {"metadata_available": True, "resource_identified": True}
        if version == "v2":
            checks.update(ipv4_observed=True, location_observed=True, metadata_fresh=True)
        http.append(dict(kind="http", run_id=c["run_id"], seq=seq, timestamp_utc=stamp(t), scheduled_utc=stamp(t),
                         monotonic_seconds=t+60, endpoint=c["endpoint"], http=200, **c["identity"], version=version,
                         build_ref=c["releases"][version]["build_ref"], artifact_sha256=c["releases"][version]["artifact_sha256"],
                         resource_id=ids[seq % 2], passed=True, metadata_ok=True, metadata_stale=False,
                         profile="basic" if version == "v1" else "extended", operation="identity_check", checks=checks, errors=[]))
    control = []
    for seq, t in enumerate(range(-60, 181, 20), 1):
        ids = OLD if t < 20 else NEW
        instances = [{"id": i, "lifecycle": "InService", "health": "Healthy", "launch_template": {
            "LaunchTemplateId": c["target_launch_template"]["id"], "Version": "1" if t < 20 else "2"}} for i in ids]
        control.append(dict(kind="controller", run_id=c["run_id"], seq=seq, timestamp_utc=stamp(t), scheduled_utc=stamp(t),
                            finished_utc=stamp(t), monotonic_seconds=t+60, asg_name=c["asg_name"], account_id=c["account_id"], region=c["region"],
                            controller_id=None if t < 0 else "ir-synthetic", status=None if t < 0 else "InProgress" if t < 60 else "Successful",
                            active_controller_ids=["ir-synthetic"] if 0 <= t < 60 else [], instances_to_update=2 if t < 60 else 0,
                            desired=2, minimum=2, maximum=3, instances=instances, targets=[{"id": i, "state": "healthy"} for i in ids], errors=[]))
    events = [{"kind": "change_started", "run_id": c["run_id"], "timestamp_utc": stamp(0), "controller_id": "ir-synthetic"},
              {"kind": "stabilized", "run_id": c["run_id"], "timestamp_utc": stamp(60), "controller_id": "ir-synthetic", "controller_sample_seq": 7, "http_sample_seqs": [60, 61]}]
    return c, http, control, events


class ObservationTests(unittest.TestCase):
    def test_complete_synthetic_window_accepted_and_ids_correlated(self):
        r = O.analyze(*fixture())
        self.assertTrue(r["accepted"])
        self.assertEqual(r["old_instance_ids"], OLD)
        self.assertEqual(r["new_instance_ids"], NEW)
        self.assertEqual(r["retired_instance_ids"], OLD)
        self.assertEqual(r["http_coverage"]["scheduled_interval_seconds"], 2)

    def test_http_gap_over_seven_seconds_is_incomplete(self):
        c, h, p, e = fixture()
        h = [r for r in h if not 4 <= O.instant(r["timestamp_utc"])-EPOCH <= 10]
        report = O.analyze(c, h, p, e)
        self.assertFalse(report["accepted"])
        self.assertGreater(report["http_coverage"]["max_gap_seconds"], 7)

    def test_controller_gap_over_thirty_seconds_is_incomplete(self):
        c, h, p, e = fixture()
        del p[4]
        self.assertFalse(O.analyze(c, h, p, e)["controller_coverage"]["complete"])

    def test_transient_failure_is_not_hidden_by_later_success(self):
        c, h, p, e = fixture()
        h[40].update(http=None, errors=["timeout_5s"])
        report = O.analyze(c, h, p, e)
        self.assertFalse(report["accepted"])
        self.assertIn("timeout_5s", report["http_failures"][0]["errors"])
        self.assertEqual(h[40]["errors"], ["timeout_5s"])

    def test_identity_build_metadata_and_post_version_fail(self):
        for change in [{"student": "a007"}, {"build_ref": "wrong-build"}, {"metadata_ok": False}, {"version": "v1"}]:
            c, h, p, e = fixture()
            h[-1].update(change)
            self.assertFalse(O.analyze(c, h, p, e)["accepted"], change)

    def test_failed_controller_and_two_controllers_rejected(self):
        for change in [{"status": "Failed"}, {"active_controller_ids": ["ir-synthetic", "ir-other"]}, {"desired": 1}]:
            c, h, p, e = fixture()
            p[-1].update(change)
            self.assertFalse(O.analyze(c, h, p, e)["accepted"], change)

    def test_capacity_requires_healthy_inservice_registered_targets(self):
        c, h, p, e = fixture()
        p[5]["targets"][0]["state"] = "draining"
        self.assertFalse(O.analyze(c, h, p, e)["accepted"])

    def test_same_instances_do_not_prove_replacement(self):
        c, h, p, e = fixture()
        for row in p[4:]:
            for i, instance in enumerate(row["instances"]): instance["id"] = OLD[i]
            for i, target in enumerate(row["targets"]): target["id"] = OLD[i]
        self.assertFalse(O.analyze(c, h, p, e)["replacement_confirmed"])

    def test_every_final_backend_needs_functional_http_evidence(self):
        c, h, p, e = fixture()
        for row in h:
            if O.instant(row["timestamp_utc"]) >= EPOCH+60:
                row["resource_id"] = NEW[0]
        self.assertEqual(O.analyze(c, h, p, e)["final_backend_http_not_seen"], [NEW[1]])

    def test_partial_window_and_missing_events_never_accept(self):
        c, h, p, e = fixture()
        self.assertFalse(O.analyze(c, h[:-2], p, e)["accepted"])
        with self.assertRaises(ValueError): O.analyze(c, h, p, e[:1])

    def test_clock_jump_and_alternative_six_second_cadence_rejected(self):
        c, h, p, e = fixture()
        h[30]["monotonic_seconds"] += 10
        self.assertFalse(O.analyze(c, h, p, e)["http_coverage"]["complete"])
        c, h, p, e = fixture()
        for i, row in enumerate(h): row["scheduled_utc"] = stamp(-60+6*i)
        self.assertFalse(O.analyze(c, h, p, e)["accepted"])

    def test_stabilization_requires_terminal_correct_template_proof(self):
        c, h, p, e = fixture()
        e[1]["controller_sample_seq"] = 6
        self.assertFalse(O.analyze(c, h, p, e)["accepted"])
        c, h, p, e = fixture()
        p[6]["instances"][0]["launch_template"]["Version"] = "1"
        self.assertFalse(O.analyze(c, h, p, e)["accepted"])

    def test_outside_failures_retained_but_separate(self):
        c, h, p, e = fixture()
        row = copy.deepcopy(h[-1]); row.update(seq=len(h)+1, timestamp_utc=stamp(182), scheduled_utc=stamp(182), monotonic_seconds=242, http=503, errors=["http_not_200"])
        h.append(row)
        report = O.analyze(c, h, p, e)
        self.assertTrue(report["accepted"])
        self.assertEqual(len(report["outside_window_failures"]), 1)

    def test_http_command_once_no_retries_and_timeout(self):
        c, h, _, _ = fixture()
        calls = []
        def execute(args, **kwargs):
            calls.append(args)
            self.assertEqual(kwargs["timeout"], 5)
            self.assertEqual(args[1], "--disable")
            self.assertNotIn("--retry", args)
            self.assertNotIn("--location", args)
            return SimpleNamespace(returncode=0, stdout=json.dumps(h[0])+"\n200")
        row = O.http_sample(c, execute)
        self.assertEqual(row["http"], 200)
        self.assertEqual(len(calls), 1)
        def timeout(*args, **kwargs): raise subprocess.TimeoutExpired("synthetic", 5)
        self.assertEqual(O.http_sample(c, timeout)["errors"], ["timeout_5s"])

    def test_write_once_jsonl_csv_preserve_errors(self):
        with TemporaryDirectory() as directory:
            writer = O.Records(directory, "http")
            writer.write({"kind": "http", "timestamp_utc": stamp(0), "http": 503, "errors": ["http_not_200"]})
            writer.close()
            row = json.loads((Path(directory)/"http.jsonl").read_text())
            self.assertEqual(row["http"], 503)
            with (Path(directory)/"http.csv").open(newline="") as stream:
                exported = next(csv.DictReader(stream))
            self.assertEqual(json.loads(exported["errors"]), ["http_not_200"])
            with self.assertRaises(FileExistsError): O.Records(directory, "http")

    def test_aws_allowlist_refuses_mutation_before_subprocess(self):
        c, *_ = fixture()
        with self.assertRaises(ValueError):
            O.aws_read(c, "autoscaling", "start-instance-refresh", [], lambda *a, **k: self.fail("No subprocess allowed"))

    def test_wrong_account_and_competing_controller_are_errors(self):
        c, _, _, e = fixture()
        def wrong(*args): return {"Account": "111111111111"}
        self.assertIn("account_mismatch", O.controller_sample(c, e, wrong)["errors"])
        def competing(c, service, action, args):
            if action == "get-caller-identity": return {"Account": c["account_id"]}
            if action == "describe-auto-scaling-groups": return {"AutoScalingGroups": [{"AutoScalingGroupName": c["asg_name"]}]}
            if action == "describe-instance-refreshes": return {"InstanceRefreshes": [{"InstanceRefreshId": "a", "Status": "InProgress"}, {"InstanceRefreshId": "b", "Status": "InProgress"}]}
            self.fail("Must stop before target health query")
        self.assertIn("multiple_active_controllers", O.controller_sample(c, e, competing)["errors"])

    def test_config_does_not_accept_placeholders_or_credentials(self):
        with self.assertRaises(ValueError): O.validate_config(json.loads((BASE/"observation/run-config.example.json").read_text()))
        c, *_ = fixture(); c["endpoint"] = "http://user:secret@synthetic.invalid"
        with self.assertRaises(ValueError): O.validate_config(c)

    def test_network_probe_is_pure_and_fail_closed(self):
        self.assertTrue(N.assess(["lo"], [{"dev": "lo", "dst": "127.0.0.0/8"}])["isolated"])
        self.assertFalse(N.assess(["lo", "eth0"], [{"dev": "eth0", "dst": "default"}])["isolated"])
        self.assertFalse(N.assess(["lo"], [{"dst": "::/0"}])["isolated"])

    def test_network_namespace_and_privilege_preflight_fail_closed(self):
        safe = {"uid": 1001, "NoNewPrivs": "1", **{key: "0000000000000000" for key in ("CapEff", "CapPrm", "CapBnd", "CapInh", "CapAmb")}}
        args = dict(parent_netns="net:[100]", current_netns="net:[200]", loopback_up=True, security=safe)
        self.assertTrue(N.assess(["lo"], [], **args)["isolated"])
        for changes in [{"current_netns": "net:[100]"}, {"current_netns": None}, {"loopback_up": False},
                        {"security": dict(safe, uid=0)}, {"security": dict(safe, NoNewPrivs="0")},
                        {"security": dict(safe, CapBnd="0000000000000001")}, {"security": {}}]:
            self.assertFalse(N.assess(["lo"], [], **dict(args, **changes))["isolated"], changes)

    def test_live_modes_require_explicit_opt_in_before_monitor(self):
        c, *_ = fixture()
        with TemporaryDirectory() as directory:
            path = Path(directory)/"config.json"
            path.write_text(json.dumps(c))
            for mode in ("http", "controller"):
                with patch("sys.argv", ["observe.py", mode, "--config", str(path), "--events", str(Path(directory)/"events.jsonl"), "--directory", directory]), patch.object(O, "monitor", side_effect=AssertionError("No live I/O allowed")):
                    with self.assertRaisesRegex(ValueError, "allow-network"):
                        O.main()

    def test_planned_recovery_v2_to_v1_uses_new_instances_and_same_endpoint(self):
        c, h, p, e = fixture()
        c.update(operation_kind="recovery", from_version="v2", target_version="v1")
        c["source_launch_template"]["version"] = "2"
        c["target_launch_template"]["version"] = "1"
        for row in h:
            row["version"] = "v2" if row["version"] == "v1" else "v1"
            v = row["version"]
            row.update(build_ref=c["releases"][v]["build_ref"], artifact_sha256=c["releases"][v]["artifact_sha256"], profile="basic" if v == "v1" else "extended")
            if v == "v2": row["checks"].update(ipv4_observed=True, location_observed=True, metadata_fresh=True)
        for row in p:
            for instance in row["instances"]:
                lt = instance["launch_template"]
                lt["Version"] = "2" if lt["Version"] == "1" else "1"
        self.assertTrue(O.analyze(c, h, p, e)["accepted"])

    def test_pending_target_is_allowed_for_capture_but_never_acceptance(self):
        c, h, p, e = fixture()
        c["target_launch_template"] = {"id": None, "version": None}
        O.validate_config(c, allow_pending_target=True)
        with self.assertRaises(ValueError): O.analyze(c, h, p, e)

    def test_scheduler_runs_every_two_seconds_without_real_time_or_io(self):
        c, *_ = fixture()
        now = [0.0]
        rows, requests = [], []
        class Writer:
            def __init__(self, *args): pass
            def write(self, row): rows.append(row)
            def close(self): pass
        class Future:
            def __init__(self, call): self.value = call()
            def done(self): return True
            def result(self): return self.value
        class Executor:
            def __init__(self, **kwargs): self.workers = kwargs["max_workers"]
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def submit(self, call): return Future(call)
        def sample(config):
            requests.append(now[0])
            return {"http": 200, "errors": []}
        with patch.object(O, "Records", Writer), patch.object(O, "ThreadPoolExecutor", Executor), patch.object(O, "read_events", return_value=[]), patch.object(O, "http_sample", side_effect=sample), patch.object(O.time, "monotonic", side_effect=lambda: now[0]), patch.object(O.time, "time", side_effect=lambda: EPOCH+now[0]), patch.object(O.time, "sleep", side_effect=lambda n: now.__setitem__(0, now[0]+n)), patch.object(O, "utc_now", side_effect=lambda: stamp(now[0])):
            self.assertFalse(O.monitor(c, "http", "unused", "unused", 6))
        self.assertEqual(len(requests), 3)
        self.assertAlmostEqual(requests[1]-requests[0], 2, places=4)
        self.assertAlmostEqual(requests[2]-requests[1], 2, places=4)
        self.assertEqual(rows[-1]["reason"], "max_duration_without_complete_window")


if __name__ == "__main__":
    unittest.main()
