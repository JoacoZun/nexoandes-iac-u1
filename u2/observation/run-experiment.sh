#!/usr/bin/env bash
# Git Bash runner. Read-only AWS profile; never starts an infrastructure change.
set -euo pipefail
if [[ $# -ne 2 ]]; then
  echo 'Usage: bash u2/observation/run-experiment.sh {preflight|http|controller|baseline|analyze} u2/observation/runs/RUN_ID' >&2
  exit 2
fi
mode="$1"
directory="$2"
repo="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo"
export AWS_PROFILE=nexoandes-u2
export AWS_PAGER=''
export AWS_CLI_AUTO_PROMPT=off
export AWS_EC2_METADATA_DISABLED=true
export PATH="/c/Program Files/Amazon/AWSCLIV2:$PATH"
python_bin="$repo/.tools/python/python.exe"
[[ -x "$python_bin" ]] || { echo 'Portable Python unavailable' >&2; exit 1; }
case "$mode" in
  preflight)
    command -v aws >/dev/null
    command -v curl >/dev/null
    "$python_bin" -B -c 'import sys,json; sys.path.insert(0,"u2/observation"); import observe; observe.validate_config(json.load(open(sys.argv[1],encoding="utf-8")),allow_pending_target=True); print("CONFIG OK; no network used by preflight")' "$directory/config.initial.json"
    ;;
  http)
    exec "$python_bin" -B u2/observation/observe.py http --config "$directory/config.initial.json" --events "$directory/events.jsonl" --directory "$directory" --max-seconds 3600 --allow-network
    ;;
  controller)
    exec "$python_bin" -B u2/observation/experiment.py controller --directory "$directory" --max-seconds 3600 --allow-network
    ;;
  baseline)
    exec "$python_bin" -B u2/observation/experiment.py baseline --directory "$directory"
    ;;
  analyze)
    exec "$python_bin" -B u2/observation/observe.py analyze --config "$directory/config.final.json" --events "$directory/events.jsonl" --directory "$directory"
    ;;
  *) echo 'Unknown mode' >&2; exit 2 ;;
esac
