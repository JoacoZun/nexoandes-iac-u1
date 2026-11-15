"""Linux CI preflight. Local kernel inspection only, no external connections."""
import argparse
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys


def assess(interfaces, routes, *, parent_netns=None, current_netns=None, loopback_up=True, security=None):
    errors = []
    if set(interfaces) != {"lo"}:
        errors.append("interfaces_other_than_loopback")
    if any(route.get("dev") not in (None, "lo") for route in routes):
        errors.append("external_route")
    if any(route.get("dst") in ("default", "0.0.0.0/0", "::/0") for route in routes):
        errors.append("default_route")
    if parent_netns is not None:
        if not re.fullmatch(r"net:\[[0-9]+\]", parent_netns) or not isinstance(current_netns, str) or not re.fullmatch(r"net:\[[0-9]+\]", current_netns):
            errors.append("network_namespace_unknown")
        elif parent_netns == current_netns:
            errors.append("network_namespace_not_changed")
    if not loopback_up:
        errors.append("loopback_not_up")
    if security is not None:
        if not isinstance(security.get("uid"), int) or security["uid"] == 0:
            errors.append("root_execution_forbidden")
        if security.get("NoNewPrivs") != "1":
            errors.append("privilege_elevation_not_blocked")
        for field in ("CapEff", "CapPrm", "CapBnd", "CapInh", "CapAmb"):
            try:
                if int(security[field], 16) != 0:
                    errors.append("capabilities_not_dropped")
                    break
            except (KeyError, TypeError, ValueError):
                errors.append("capability_status_unknown")
                break
    return {"isolated": not errors, "interfaces": sorted(interfaces), "errors": errors,
            "parent_netns": parent_netns, "current_netns": current_netns, "loopback_up": loopback_up}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent-netns", required=True)
    args = parser.parse_args()
    if sys.platform != "linux":
        raise SystemExit("Linux-only network namespace preflight; not verified on Windows")
    interfaces = [name for _, name in socket.if_nameindex()]
    routes = []
    for family in ("-4", "-6"):
        result = subprocess.run(["ip", family, "-j", "route", "show", "table", "all"],
                                capture_output=True, text=True, timeout=5, check=True)
        routes.extend(json.loads(result.stdout))
    link = subprocess.run(["ip", "-j", "link", "show", "lo"], capture_output=True, text=True, timeout=5, check=True)
    links = json.loads(link.stdout)
    status = dict(line.split(":", 1) for line in Path("/proc/self/status").read_text().splitlines() if ":" in line)
    security = {key: value.strip() for key, value in status.items()}
    security["uid"] = os.geteuid()
    report = assess(interfaces, routes, parent_netns=args.parent_netns,
                    current_netns=str(Path("/proc/self/ns/net").readlink()),
                    loopback_up=len(links) == 1 and "UP" in links[0].get("flags", []), security=security)
    print(json.dumps(report))
    return 0 if report["isolated"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
