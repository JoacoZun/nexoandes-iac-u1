#!/usr/bin/env bash
# Linux-only, fail closed. No cloud command or external connectivity probe.
set -euo pipefail
[[ "$(uname -s)" == Linux ]] || { echo 'ERROR: Linux network isolation required' >&2; exit 1; }
[[ $# -ge 2 ]] || { echo 'Usage: run_offline_linux.sh ABS_PYTHON COMMAND [ARGS...]' >&2; exit 1; }
for required in sudo unshare ip setpriv readlink; do
  command -v "$required" >/dev/null || { echo "ERROR: missing $required" >&2; exit 1; }
done
python_bin="$1"
shift
[[ "$python_bin" = /* && -x "$python_bin" ]] || { echo 'ERROR: absolute executable Python required' >&2; exit 1; }
caller_uid="$(id -u)"
caller_gid="$(id -g)"
[[ "$caller_uid" != 0 ]] || { echo 'ERROR: invoke from the unprivileged runner user' >&2; exit 1; }
parent_netns="$(readlink /proc/self/ns/net)"
# Only creation/setup of a new namespace is privileged. The preflight and command
# run as the original uid, without groups/capabilities/elevation or inherited secrets.
sudo -n unshare --net -- bash -c '
  set -euo pipefail
  python_bin="$1"; parent_netns="$2"; caller_uid="$3"; caller_gid="$4"
  caller_home="$5"; caller_path="$6"; caller_ld="$7"; shift 7
  ip link set lo up
  exec setpriv --reuid="$caller_uid" --regid="$caller_gid" --clear-groups \
    --bounding-set=-all --inh-caps=-all --ambient-caps=-all --no-new-privs \
    env -i HOME="$caller_home" PATH="$caller_path" LD_LIBRARY_PATH="$caller_ld" \
    CHECKPOINT_DISABLE=1 TF_IN_AUTOMATION=true TF_INPUT=false \
    AWS_EC2_METADATA_DISABLED=true PYTHONDONTWRITEBYTECODE=1 \
    bash -c '\''
      set -euo pipefail
      python_bin="$1"; parent_netns="$2"; shift 2
      "$python_bin" -B u2/scripts/ci_network_probe.py --parent-netns "$parent_netns"
      exec "$@"
    '\'' bash "$python_bin" "$parent_netns" "$@"
' bash "$python_bin" "$parent_netns" "$caller_uid" "$caller_gid" "$HOME" "$PATH" "${LD_LIBRARY_PATH:-}" "$@"
