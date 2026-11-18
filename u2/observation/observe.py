"""U2 observation only. Live I/O requires explicit CLI opt-in; tests inject all I/O.

No API in this module starts/cancels/rolls back a refresh or changes infrastructure.
"""
import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from urllib.parse import urlsplit

HTTP_INTERVAL = 2
HTTP_TIMEOUT = 5
CONTROL_INTERVAL = 20
CONTROL_TIMEOUT = 4
HTTP_GAP = 7
CONTROL_GAP = 30
PRE_SECONDS = 60
POST_SECONDS = 120
TERMINAL = {"Successful", "Failed", "Cancelled", "RollbackSuccessful", "RollbackFailed"}
SUCCESS = {"Successful", "RollbackSuccessful"}
READ_ONLY = {("sts", "get-caller-identity"),
             ("autoscaling", "describe-auto-scaling-groups"),
             ("autoscaling", "describe-instance-refreshes"),
             ("elbv2", "describe-target-health")}


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def instant(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset().total_seconds() != 0:
        raise ValueError("UTC timestamp with explicit timezone required")
    return parsed.timestamp()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_config(c, allow_pending_target=False):
    required = {"run_id", "operation_kind", "region", "account_id", "asg_name",
                "target_group_arn", "endpoint", "identity", "releases", "from_version",
                "target_version", "source_launch_template", "target_launch_template", "base_capacity",
                "temporary_capacity", "controller_owner"}
    require(set(c) == required, "Config fields must match run-config.example.json; no secrets")
    require(isinstance(c["run_id"], str) and re.fullmatch(r"[A-Za-z0-9._-]{4,100}", c["run_id"]), "Invalid run_id")
    require(c["operation_kind"] in ("update", "recovery"), "Invalid operation kind")
    require(c["controller_owner"] == "terraform_aws_provider", "Exactly one declared controller owner required")
    require(isinstance(c["account_id"], str) and re.fullmatch(r"[0-9]{12}", c["account_id"]), "Expected account required")
    require(isinstance(c["region"], str) and re.fullmatch(r"[a-z]{2}(-[a-z]+)+-[0-9]+", c["region"]), "Region required")
    require(isinstance(c["asg_name"], str) and re.fullmatch(r"[A-Za-z0-9._-]{1,255}", c["asg_name"]), "ASG required")
    require(isinstance(c["target_group_arn"], str) and re.fullmatch(
        r"arn:[a-z0-9-]+:elasticloadbalancing:" + re.escape(c["region"]) + ":" + c["account_id"] + r":targetgroup/[A-Za-z0-9-]+/[A-Za-z0-9]+", c["target_group_arn"]), "Target group must match context")
    require(isinstance(c["endpoint"], str), "Endpoint required")
    url = urlsplit(c["endpoint"])
    require(url.scheme in ("http", "https") and url.hostname and not url.username and not url.password
            and url.path in ("", "/") and not url.query and not url.fragment, "Endpoint must be a base URL without credentials/query")
    i = c["identity"]
    require(isinstance(i, dict) and set(i) == {"project", "phase", "provider", "x", "student", "course"}, "Identity fields required")
    require(i["project"] == "NexoAndes" and i["phase"] == "U2" and i["provider"] == "aws", "AWS U2 identity required")
    require(type(i["x"]) is int and 1 <= i["x"] <= 254 and i["student"] == f"a{i['x']:03d}", "X/student mismatch")
    require(isinstance(i["course"], str) and re.fullmatch(r"c[0-9]{2}", i["course"]), "Course must be confirmed")
    require(c["from_version"] in ("v1", "v2") and c["target_version"] in ("v1", "v2") and c["from_version"] != c["target_version"], "Distinct source/target releases required")
    require((c["from_version"], c["target_version"]) == (("v1", "v2") if c["operation_kind"] == "update" else ("v2", "v1")), "This U2 protocol supports update v1-to-v2 or recovery v2-to-v1")
    require(isinstance(c["releases"], dict) and set(c["releases"]) == {"v1", "v2"}, "Both reproducible builds required")
    for release in c["releases"].values():
        require(isinstance(release, dict) and set(release) == {"build_ref", "artifact_sha256"}, "Release fields required")
        require(isinstance(release["build_ref"], str) and re.fullmatch(r"[A-Za-z0-9._-]{4,80}", release["build_ref"]), "Real build ref required")
        require(isinstance(release["artifact_sha256"], str) and re.fullmatch(r"[a-f0-9]{64}", release["artifact_sha256"]), "Installed application artifact hash required")
    for index, lt in enumerate((c["source_launch_template"], c["target_launch_template"])):
        if index == 1 and allow_pending_target and lt == {"id": None, "version": None}:
            continue # Observer can start before Terraform allocates target LT; final analysis cannot.
        require(isinstance(lt, dict) and set(lt) == {"id", "version"} and isinstance(lt.get("id"), str)
                and isinstance(lt.get("version"), str) and re.fullmatch(r"lt-[a-z0-9]+", lt["id"])
                and re.fullmatch(r"[1-9][0-9]*", lt["version"]), "Numeric source/target Launch Template required")
    require(type(c["base_capacity"]) is int and c["base_capacity"] >= 1
            and type(c["temporary_capacity"]) is int and c["temporary_capacity"] >= 1, "Explicit capacity required")
    return c


def read_events(path):
    if not Path(path).exists():
        return []
    # JSONL must be complete. Malformed/partial writes fail; never silently drop a line.
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def operation_events(events, run_id):
    require(all(e.get("run_id") == run_id for e in events), "Events from another run")
    starts = [e for e in events if e.get("kind") == "change_started"]
    stable = [e for e in events if e.get("kind") == "stabilized"]
    require(len(starts) <= 1 and len(stable) <= 1, "Duplicate/conflicting operation events")
    for e in starts + stable:
        instant(e["timestamp_utc"])
        require(isinstance(e.get("controller_id"), str) and e["controller_id"], "Pinned InstanceRefreshId required")
    if stable:
        require(starts and stable[0]["controller_id"] == starts[0]["controller_id"]
                and instant(stable[0]["timestamp_utc"]) >= instant(starts[0]["timestamp_utc"]), "Stabilization must follow same controller")
    return (starts[0] if starts else None, stable[0] if stable else None)


def http_sample(c, execute=subprocess.run):
    url = c["endpoint"].rstrip("/") + "/api/check"
    row = {"endpoint": c["endpoint"], "http": None, "errors": []}
    try:
        # Exactly one request, no redirect following or retries; hard subprocess deadline.
        result = execute(["curl", "--disable", "--silent", "--show-error", "--noproxy", "*", "--max-filesize", "1048576",
                          "--connect-timeout", str(HTTP_TIMEOUT), "--max-time", str(HTTP_TIMEOUT),
                          "--write-out", "\n%{http_code}", url],
                         capture_output=True, text=True, encoding="utf-8", timeout=HTTP_TIMEOUT, check=False)
        if result.returncode:
            row["errors"].append(f"curl_exit_{result.returncode}")
        body, status = result.stdout.rsplit("\n", 1)
        row["http"] = int(status)
        row["body_sha256"] = hashlib.sha256(body.encode()).hexdigest()
        if row["http"] != 200:
            row["errors"].append("http_not_200")
        info = json.loads(body)
        require(isinstance(info, dict), "JSON object required")
        for key in ("project", "phase", "provider", "x", "student", "course", "version", "build_ref",
                    "resource_id", "artifact_sha256", "passed", "profile", "operation", "checks",
                    "metadata_ok", "metadata_stale", "metadata_cached", "metadata_age_seconds",
                    "metadata_last_success_utc", "observed_at_utc", "private_ip", "location"):
            row[key] = info.get(key)
        if info.get("passed") is not True:
            row["errors"].append("functional_check_failed")
    except subprocess.TimeoutExpired:
        row["errors"].append("timeout_5s")
    except (ValueError, TypeError, AttributeError):
        row["errors"].append("invalid_http_or_json")
    except OSError as exc:
        row["errors"].append(type(exc).__name__)
    return row


def aws_read(c, service, action, arguments, execute=subprocess.run):
    require((service, action) in READ_ONLY, "Only allowlisted read-only AWS commands are implemented")
    env = {key: value for key, value in os.environ.items() if not key.startswith("AWS_ENDPOINT_URL")}
    env.update(AWS_MAX_ATTEMPTS="1", AWS_RETRY_MODE="standard", AWS_EC2_METADATA_DISABLED="true",
               AWS_PAGER="", AWS_CLI_AUTO_PROMPT="off")
    result = execute(["aws", service, action, *arguments, "--region", c["region"], "--output", "json",
                      "--no-cli-pager", "--cli-connect-timeout", str(CONTROL_TIMEOUT),
                      "--cli-read-timeout", str(CONTROL_TIMEOUT)],
                     capture_output=True, text=True, timeout=CONTROL_TIMEOUT, check=False, env=env)
    require(result.returncode == 0, f"aws_read_failed_{service}_{action}_{result.returncode}")
    return json.loads(result.stdout)


def controller_sample(c, events, query=aws_read):
    row = {"asg_name": c["asg_name"], "account_id": c["account_id"], "region": c["region"],
           "controller_id": None, "status": None, "instances": [], "targets": [], "errors": []}
    try:
        start, _ = operation_events(events, c["run_id"])
        identity = query(c, "sts", "get-caller-identity", [])
        require(identity.get("Account") == c["account_id"], "account_mismatch")
        groups = query(c, "autoscaling", "describe-auto-scaling-groups", ["--auto-scaling-group-names", c["asg_name"]])["AutoScalingGroups"]
        require(len(groups) == 1 and groups[0]["AutoScalingGroupName"] == c["asg_name"], "asg_mismatch")
        group = groups[0]
        refreshes = query(c, "autoscaling", "describe-instance-refreshes", ["--auto-scaling-group-name", c["asg_name"]])["InstanceRefreshes"]
        row["refreshes"] = [{"id": r["InstanceRefreshId"], "status": r["Status"], "start_time": r.get("StartTime"), "end_time": r.get("EndTime")} for r in refreshes]
        active = [r for r in refreshes if r["Status"] not in TERMINAL]
        row["active_controller_ids"] = [r["InstanceRefreshId"] for r in active]
        require(len(active) <= 1, "multiple_active_controllers")
        if start:
            pinned = start["controller_id"]
            require(not any(r["InstanceRefreshId"] != pinned and r.get("StartTime") and instant(r["StartTime"]) >= instant(start["timestamp_utc"]) for r in refreshes), "foreign_controller_since_start")
            require(not active or active[0]["InstanceRefreshId"] == pinned, "unexpected_active_controller")
            matches = [r for r in refreshes if r["InstanceRefreshId"] == pinned]
            require(len(matches) == 1, "pinned_controller_missing")
            refresh = matches[0]
            row.update(controller_id=pinned, status=refresh["Status"],
                       status_reason=refresh.get("StatusReason"), percentage_complete=refresh.get("PercentageComplete"),
                       instances_to_update=refresh.get("InstancesToUpdate"))
        else:
            require(not active, "controller_active_before_declared_start")
        row.update(desired=group["DesiredCapacity"], minimum=group["MinSize"], maximum=group["MaxSize"])
        row["instances"] = [{"id": i["InstanceId"], "lifecycle": i["LifecycleState"],
                             "health": i["HealthStatus"], "az": i.get("AvailabilityZone"),
                             "launch_template": i.get("LaunchTemplate", {})} for i in group.get("Instances", [])]
        targets = query(c, "elbv2", "describe-target-health", ["--target-group-arn", c["target_group_arn"]])["TargetHealthDescriptions"]
        row["targets"] = [{"id": t["Target"]["Id"], "state": t["TargetHealth"]["State"],
                           "reason": t["TargetHealth"].get("Reason")} for t in targets]
    except (ValueError, KeyError, TypeError, OSError, subprocess.TimeoutExpired) as exc:
        # Never print AWS stderr/tokens or interpret failed queries as zero resources.
        row["errors"].append(str(exc) if isinstance(exc, ValueError) else type(exc).__name__)
    return row


CSV_FIELDS = ["kind", "run_id", "seq", "scheduled_utc", "timestamp_utc", "finished_utc",
              "monotonic_seconds", "schedule_delay_seconds", "duration_seconds", "endpoint", "http",
              "project", "phase", "provider", "x", "student", "course", "version", "build_ref",
              "resource_id", "artifact_sha256", "passed", "metadata_ok", "metadata_stale",
              "body_sha256", "controller_id", "status", "percentage_complete", "instances_to_update",
              "desired", "minimum", "maximum", "healthy_capacity", "old_instance_ids", "new_instance_ids",
              "retired_instance_ids", "instances", "targets", "errors", "reason", "account_id", "region", "asg_name", "active_controller_ids"]


class Records:
    def __init__(self, directory, kind):
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        self.jsonl = (directory / f"{kind}.jsonl").open("x", encoding="utf-8", newline="\n")
        try:
            self.csv_file = (directory / f"{kind}.csv").open("x", encoding="utf-8", newline="")
        except Exception:
            self.jsonl.close()
            raise
        self.csv = csv.DictWriter(self.csv_file, fieldnames=CSV_FIELDS, extrasaction="ignore")
        self.csv.writeheader()
        self.lock = threading.Lock()

    def write(self, row):
        with self.lock:
            self.jsonl.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
            cells = {}
            for key in CSV_FIELDS:
                value = row.get(key)
                if isinstance(value, (dict, list, bool)):
                    value = json.dumps(value, ensure_ascii=False)
                if isinstance(value, str) and value.startswith(("=", "+", "-", "@")):
                    value = "'" + value # CSV spreadsheet formula escaping; JSONL remains canonical.
                cells[key] = value
            self.csv.writerow(cells)
            self.jsonl.flush()
            self.csv_file.flush()

    def close(self):
        self.jsonl.close()
        self.csv_file.close()


def monitor(c, kind, events_path, directory, max_seconds):
    """Fixed-rate scheduler, no retry/catch-up requests. Missing slots become error rows."""
    interval = HTTP_INTERVAL if kind == "http" else CONTROL_INTERVAL
    workers = math.ceil(HTTP_TIMEOUT / HTTP_INTERVAL) if kind == "http" else 1
    start_mono = time.monotonic()
    start_wall = time.time()
    writer = Records(directory, kind)
    futures = []
    baseline = None
    stop_reason = "max_duration_without_complete_window"
    try:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            seq = 0
            next_due = start_mono
            while time.monotonic() < start_mono + max_seconds:
                events = read_events(events_path)
                _, stable = operation_events(events, c["run_id"])
                if stable and time.time() >= instant(stable["timestamp_utc"]) + POST_SECONDS + interval:
                    stop_reason = "post_window_observed_analyzer_required"
                    break
                now = time.monotonic()
                if now >= next_due:
                    futures = [f for f in futures if not f.done() or f.result() is not None]
                    active = sum(not f.done() for f in futures)
                    scheduled = next_due
                    seq += 1
                    def collect(sequence=seq, due=scheduled, snapshot=events):
                        nonlocal baseline
                        began = time.monotonic()
                        actual_start = utc_now()
                        row = http_sample(c) if kind == "http" else controller_sample(c, snapshot)
                        row.update(kind=kind, run_id=c["run_id"], seq=sequence, timestamp_utc=actual_start,
                                   scheduled_utc=datetime.fromtimestamp(start_wall + due - start_mono, timezone.utc).isoformat(),
                                   monotonic_seconds=began-start_mono, schedule_delay_seconds=began-due,
                                   finished_utc=utc_now(), duration_seconds=time.monotonic()-began)
                        if kind == "controller":
                            ids = {i["id"] for i in row["instances"]}
                            if baseline is None and not row["errors"]:
                                baseline = ids
                            row.update(old_instance_ids=sorted(ids & (baseline or set())),
                                       new_instance_ids=sorted(ids - (baseline or set())),
                                       retired_instance_ids=sorted((baseline or set()) - ids),
                                       healthy_capacity=len(healthy_ids(row)))
                        writer.write(row)
                    if active < workers and now - next_due < interval:
                        futures.append(pool.submit(collect))
                    else:
                        writer.write({"kind": kind, "run_id": c["run_id"], "seq": seq,
                                      "timestamp_utc": utc_now(), "monotonic_seconds": now-start_mono,
                                      "scheduled_utc": datetime.fromtimestamp(start_wall + next_due-start_mono, timezone.utc).isoformat(),
                                      "errors": ["missed_schedule_no_retry"]})
                    next_due += interval
                time.sleep(min(0.1, max(0.001, next_due-time.monotonic())))
            for future in futures:
                future.result() # Propagate writer/runtime failures, never silently discard.
        writer.write({"kind": "monitor_stop", "run_id": c["run_id"], "timestamp_utc": utc_now(), "reason": stop_reason})
    finally:
        writer.close()
    return stop_reason == "post_window_observed_analyzer_required"


def healthy_ids(row):
    healthy = {i["id"] for i in row.get("instances", []) if i.get("lifecycle") == "InService" and i.get("health") == "Healthy"}
    return healthy & {t["id"] for t in row.get("targets", []) if t.get("state") == "healthy"}


def functional_errors(c, row, start, stable):
    errors = list(row.get("errors", []))
    if row.get("http") != 200:
        errors.append("http_not_200")
    if row.get("passed") is not True or row.get("metadata_ok") is not True or row.get("metadata_stale") is not False:
        errors.append("function_or_metadata_not_confirmed")
    if any(row.get(k) != value for k, value in c["identity"].items()):
        errors.append("identity_mismatch")
    if type(row.get("x")) is not int:
        errors.append("identity_x_not_integer")
    when = instant(row["timestamp_utc"])
    allowed = {c["from_version"]} if when < start else {c["target_version"]} if when >= stable else {c["from_version"], c["target_version"]}
    version = row.get("version")
    if not isinstance(version, str):
        version = None
        errors.append("invalid_version_schema")
    if version not in allowed:
        errors.append("wrong_version_for_phase")
    release = c["releases"].get(version, {})
    if row.get("build_ref") != release.get("build_ref") or row.get("artifact_sha256") != release.get("artifact_sha256"):
        errors.append("build_or_artifact_mismatch")
    if not isinstance(row.get("resource_id"), str) or not re.fullmatch(r"i-([a-f0-9]{8}|[a-f0-9]{17})", row["resource_id"]):
        errors.append("backend_id_missing_or_invalid")
    expected_profile = {"v1": "basic", "v2": "extended"}.get(version)
    if row.get("profile") != expected_profile or row.get("operation") != "identity_check":
        errors.append("wrong_functional_profile")
    required_checks = {"metadata_available", "resource_identified"}
    if version == "v2":
        required_checks |= {"ipv4_observed", "location_observed", "metadata_fresh"}
    checks = row.get("checks")
    if not isinstance(checks, dict) or not all(checks.get(key) is True for key in required_checks):
        errors.append("functional_checks_missing_or_failed")
    if row.get("endpoint") != c["endpoint"]:
        errors.append("endpoint_changed")
    return sorted(set(errors))


def coverage(rows, lower, upper, max_gap, expected_interval):
    samples = sorted(rows, key=lambda r: instant(r["timestamp_utc"]))
    if not samples:
        return {"complete": False, "max_gap_seconds": None, "clock_errors": [], "samples": 0}
    times = [instant(r["timestamp_utc"]) for r in samples]
    before = [i for i, t in enumerate(times) if t <= lower]
    after = [i for i, t in enumerate(times) if t >= upper]
    left = before[-1] if before else 0
    right = after[0] if after else len(samples)-1
    segment = samples[left:right+1]
    gaps = [instant(b["timestamp_utc"])-instant(a["timestamp_utc"]) for a, b in zip(segment, segment[1:])]
    clock_errors = []
    schedule_errors = []
    by_seq = sorted(samples, key=lambda r: r["seq"])
    for a, b in zip(by_seq, by_seq[1:]):
        utc_delta = instant(b["timestamp_utc"])-instant(a["timestamp_utc"])
        mono_delta = b.get("monotonic_seconds", 0)-a.get("monotonic_seconds", 0)
        if utc_delta < 0 or mono_delta < 0 or abs(utc_delta-mono_delta) > 1:
            clock_errors.append([a["seq"], b["seq"]])
        planned_delta = instant(b.get("scheduled_utc", b["timestamp_utc"]))-instant(a.get("scheduled_utc", a["timestamp_utc"]))
        if b["seq"] != a["seq"]+1 or abs(planned_delta-expected_interval) > 0.01:
            schedule_errors.append([a["seq"], b["seq"]])
    maximum = max(gaps, default=0)
    complete = bool(before and after and lower-times[left] <= max_gap and times[right]-upper <= max_gap and maximum <= max_gap and not clock_errors and not schedule_errors)
    return {"complete": complete, "max_gap_seconds": maximum, "clock_errors": clock_errors,
            "schedule_errors": schedule_errors, "scheduled_interval_seconds": expected_interval, "samples": len(segment)}


def target_ready(c, row):
    expected = c["target_launch_template"]
    active_ids = {t["id"] for t in row.get("targets", []) if t.get("state") != "unused"}
    good = {i["id"] for i in row.get("instances", []) if i.get("launch_template", {}).get("LaunchTemplateId") == expected["id"]
            and str(i.get("launch_template", {}).get("Version")) == expected["version"]}
    success = SUCCESS if c["operation_kind"] == "recovery" else {"Successful"}
    return bool(not row.get("errors") and row.get("status") in success and row.get("instances_to_update") == 0
                and len(healthy_ids(row)) >= c["base_capacity"] and active_ids == healthy_ids(row) and active_ids <= good)


def analyze(c, http_rows, control_rows, events):
    validate_config(c)
    start_event, stable_event = operation_events(events, c["run_id"])
    require(start_event and stable_event, "Incomplete operation events: no acceptance possible")
    t0, ts = instant(start_event["timestamp_utc"]), instant(stable_event["timestamp_utc"])
    lower, upper = t0-PRE_SECONDS, ts+POST_SECONDS
    http = [r for r in http_rows if r.get("kind") == "http"]
    control = [r for r in control_rows if r.get("kind") == "controller"]
    require(all(r.get("run_id") == c["run_id"] for r in http+control), "Mixed run evidence")
    require(len({r["seq"] for r in http}) == len(http) and len({r["seq"] for r in control}) == len(control), "Duplicate sample sequence")
    http_cov = coverage(http, lower, upper, HTTP_GAP, HTTP_INTERVAL)
    control_cov = coverage(control, lower, upper, CONTROL_GAP, CONTROL_INTERVAL)
    failures, outside = [], []
    for row in http:
        errors = functional_errors(c, row, t0, ts)
        nearby = [r for r in control if abs(instant(r["timestamp_utc"])-instant(row["timestamp_utc"])) <= CONTROL_GAP and not r.get("errors")]
        if row.get("resource_id") not in set().union(*(healthy_ids(r) for r in nearby)):
            errors.append("backend_not_correlated_with_provider")
        if errors:
            (failures if lower <= instant(row["timestamp_utc"]) <= upper else outside).append({"seq": row["seq"], "errors": errors})
    control_failures = []
    for row in control:
        when = instant(row["timestamp_utc"])
        if not lower <= when <= upper:
            continue
        errors = list(row.get("errors", []))
        if len(healthy_ids(row)) < c["base_capacity"] or row.get("desired") != c["base_capacity"] or row.get("minimum") != c["base_capacity"] or row.get("maximum") != c["base_capacity"]+c["temporary_capacity"]:
            errors.append("base_capacity_not_confirmed")
        if len(row.get("instances", [])) > c["base_capacity"]+c["temporary_capacity"]:
            errors.append("temporary_capacity_exceeded")
        if row.get("asg_name") != c["asg_name"] or row.get("account_id") != c["account_id"] or row.get("region") != c["region"]:
            errors.append("controller_context_mismatch")
        if len(row.get("active_controller_ids", [])) > 1:
            errors.append("multiple_active_controllers")
        if when >= t0 and row.get("controller_id") != start_event["controller_id"]:
            errors.append("controller_id_mismatch")
        if row.get("status") in ("Failed", "Cancelled", "RollbackFailed"):
            errors.append("controller_failure_recorded")
        if when < t0:
            source = c["source_launch_template"]
            source_ids = {i["id"] for i in row.get("instances", []) if i.get("launch_template", {}).get("LaunchTemplateId") == source["id"]
                          and str(i.get("launch_template", {}).get("Version")) == source["version"]}
            if not healthy_ids(row) <= source_ids:
                errors.append("baseline_template_mismatch")
        if when >= ts:
            if not target_ready(c, row):
                errors.append("controller_or_active_target_template_not_ready")
        if errors:
            control_failures.append({"seq": row["seq"], "errors": sorted(set(errors))})
    stable_proofs = [r for r in control if instant(r["timestamp_utc"]) <= ts
                     and instant(r.get("finished_utc", r["timestamp_utc"])) <= ts
                     and ts-instant(r["timestamp_utc"]) <= CONTROL_GAP and r.get("seq") == stable_event.get("controller_sample_seq")
                     and r.get("status") in SUCCESS and r.get("controller_id") == start_event["controller_id"]
                     and target_ready(c, r)]
    stable_http = [r for r in http if r.get("seq") in stable_event.get("http_sample_seqs", [])
                   and ts-CONTROL_GAP <= instant(r["timestamp_utc"]) <= ts
                   and instant(r.get("finished_utc", r["timestamp_utc"])) <= ts
                   and r.get("version") == c["target_version"] and not functional_errors(c, r, t0, ts)]
    stable_proofs = [r for r in stable_proofs if healthy_ids(r) <= {h.get("resource_id") for h in stable_http}]
    baseline = [r for r in control if instant(r["timestamp_utc"]) < t0 and not r.get("errors")]
    final = [r for r in control if ts <= instant(r["timestamp_utc"]) <= upper and not r.get("errors")]
    old_ids = {i["id"] for i in max(baseline, key=lambda r: instant(r["timestamp_utc"])).get("instances", [])} if baseline else set()
    final_row = max(final, key=lambda r: instant(r["timestamp_utc"])) if final else {}
    final_ids = {i["id"] for i in final_row.get("instances", [])}
    final_active = healthy_ids(final_row)
    baseline_active = healthy_ids(max(baseline, key=lambda r: instant(r["timestamp_utc"]))) if baseline else set()
    seen_baseline = {r.get("resource_id") for r in http if lower <= instant(r["timestamp_utc"]) < t0 and not functional_errors(c, r, t0, ts)}
    missing_baseline = sorted(baseline_active-seen_baseline)
    seen_final = {r.get("resource_id") for r in http if ts <= instant(r["timestamp_utc"]) <= upper and not functional_errors(c, r, t0, ts)}
    missing_backends = sorted(final_active-seen_final)
    replacement_confirmed = bool(old_ids and final_ids and final_ids.isdisjoint(old_ids))
    accepted = bool(http_cov["complete"] and control_cov["complete"] and not failures and not control_failures
                    and stable_proofs and replacement_confirmed and final_active and not missing_backends and not missing_baseline)
    return {"accepted": accepted, "run_id": c["run_id"], "window_start_utc": datetime.fromtimestamp(lower, timezone.utc).isoformat(),
            "window_end_utc": datetime.fromtimestamp(upper, timezone.utc).isoformat(), "http_coverage": http_cov,
            "controller_coverage": control_cov, "http_failures": failures, "controller_failures": control_failures,
            "outside_window_failures": outside, "stabilization_proof_found": bool(stable_proofs),
            "old_instance_ids": sorted(old_ids), "new_instance_ids": sorted(final_ids-old_ids),
            "retired_instance_ids": sorted(old_ids-final_ids), "replacement_confirmed": replacement_confirmed,
            "baseline_backend_http_not_seen": missing_baseline, "final_backend_http_not_seen": missing_backends, "controller_final_status": final_row.get("status"),
            "sampling_limit": "Only observed instants; not proof of absolute availability between samples"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["http", "controller", "analyze"])
    parser.add_argument("--config", required=True)
    parser.add_argument("--events", required=True)
    parser.add_argument("--directory", required=True)
    parser.add_argument("--allow-network", action="store_true", help="Explicit future authorization, not used in tests/CI")
    parser.add_argument("--max-seconds", type=int, default=3600)
    args = parser.parse_args()
    c = validate_config(json.loads(Path(args.config).read_text(encoding="utf-8")), allow_pending_target=args.mode != "analyze")
    if args.mode == "analyze":
        folder = Path(args.directory)
        report = analyze(c, read_events(folder/"http.jsonl"), read_events(folder/"controller.jsonl"), read_events(args.events))
        with (folder/"analysis.json").open("x", encoding="utf-8") as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2)
        print(json.dumps(report, ensure_ascii=False))
        return 0 if report["accepted"] else 1
    require(args.allow_network, "Live observation requires --allow-network and separate authorization")
    require(args.max_seconds >= PRE_SECONDS+POST_SECONDS, "Observation duration too short")
    return 0 if monitor(c, args.mode, args.events, args.directory, args.max_seconds) else 1


if __name__ == "__main__":
    raise SystemExit(main())
