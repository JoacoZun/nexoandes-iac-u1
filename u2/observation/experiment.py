"""Read-only experiment preparation and integrated observation. Never starts a change."""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
sys.path.insert(0, str(Path(__file__).resolve().parent))
import observe as o

ROOT = Path(__file__).resolve().parents[2]


def exclusive(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2)


def atomic_events(path, rows):
    temp = path.with_suffix('.pending')
    with temp.open('x', encoding='utf-8', newline='\n') as stream:
        for row in rows:
            stream.write(json.dumps(row) + '\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)


def application_hashes():
    raw = (ROOT/'u2/templates/user_data_u2.sh.tpl').read_bytes()
    o.require(hashlib.sha256(raw).hexdigest() == '4445eadace792b80ac3e07886d99b80bfd1f250b892731dfc9abda77b9c9e2e3', 'Teacher artifact changed')
    text = raw.decode('utf-8')
    base = text.split("<<'PYTHON'\n", 1)[1].split('\nPYTHON\n', 1)[0] + '\n'
    installer = text.split("<<'INSTALL_RELEASE'\n", 1)[1].split('\nINSTALL_RELEASE\n', 1)[0]
    tree = ast.parse(installer)
    releases = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == 'releases' for t in n.targets))
    return {v: hashlib.sha256(base.encode()+b'\0'+code.encode()).hexdigest() for v, code in releases.items()}


def prepare(folder):
    tf = ROOT/'.tools/terraform/1.16.6/terraform.exe'
    result = subprocess.run([str(tf), '-chdir='+str(ROOT/'u2/aws'), 'output', '-json'], capture_output=True, text=True, timeout=60)
    o.require(result.returncode == 0, 'Terraform outputs unavailable')
    outputs = {k: v['value'] for k, v in json.loads(result.stdout).items()}
    ctx, ids, ctrl = outputs['context'], outputs['ids'], outputs['controller']
    o.require(ctx['expected_state_key'] == 'u2/c50/a008/aws/terraform.tfstate', 'Unexpected state context')
    c = json.loads((Path(__file__).with_name('run-config.example.json')).read_text())
    c.update(run_id=folder.name, region=ctx['region'], account_id=ctx['account_id'],
             asg_name=ids['asg_name'], target_group_arn=ids['target_group_arn'], endpoint=outputs['endpoint']['url'],
             base_capacity=ctrl['base_capacity'], temporary_capacity=ctrl['temporary_capacity'])
    ident = ctx['identity']
    c['identity'].update(x=ident['x'], student=ident['student'], course=ident['course'])
    hashes = application_hashes()
    c['releases'] = {v: dict(build_ref=ident['build_ref'], artifact_sha256=h) for v, h in hashes.items()}
    snapshot = o.controller_sample(c, [])
    o.require(not snapshot['errors'] and len(o.healthy_ids(snapshot)) == c['base_capacity'], 'Baseline controller not ready: '+str(snapshot['errors']))
    templates = {(i['launch_template']['LaunchTemplateId'], str(i['launch_template']['Version'])) for i in snapshot['instances']}
    o.require(len(templates) == 1, 'Mixed source Launch Templates')
    lt, version = templates.pop()
    c['source_launch_template'] = dict(id=lt, version=version)
    o.validate_config(c, allow_pending_target=True)
    seen = set()
    samples = []
    for _ in range(30):
        row = o.http_sample(c)
        row['timestamp_utc'] = o.utc_now()
        o.require(not row['errors'] and not o.functional_errors(c, row, float('inf'), float('inf')), 'HTTP v1/build/hash/identity mismatch')
        seen.add(row['resource_id'])
        samples.append(row)
        if o.healthy_ids(snapshot) <= seen:
            break
        time.sleep(2)
    o.require(o.healthy_ids(snapshot) <= seen, 'HTTP did not reach every baseline backend')
    folder.mkdir(parents=True, exist_ok=False)
    exclusive(folder/'config.initial.json', c)
    exclusive(folder/'preparation.json', dict(observed_utc=o.utc_now(), controller=snapshot, http=samples,
              target_hash_source='Expected from intact local teacher artifact; not yet deployed',
              target_build_source='Same code build as source; release v2 is a distinct installed artifact'))
    print(str(folder))


def rows(path):
    return o.read_events(path)


def stabilize(c, folder, events, row):
    if len(events) != 1 or row.get('errors'):
        return
    active = o.healthy_ids(row)
    templates = {(i.get('launch_template', {}).get('LaunchTemplateId'), str(i.get('launch_template', {}).get('Version'))) for i in row['instances']}
    if len(templates) != 1:
        return
    lt, version = templates.pop()
    final = dict(c, target_launch_template=dict(id=lt, version=version))
    if final['target_launch_template'] == c['source_launch_template']:
        return
    if not o.target_ready(final, row):
        return
    if (row.get('desired'), row.get('minimum'), row.get('maximum')) != (c['base_capacity'], c['base_capacity'], c['base_capacity']+c['temporary_capacity']):
        return
    now = o.utc_now()
    stamp = o.instant(now)
    try:
        http = rows(folder/'http.jsonl')
    except (FileNotFoundError, json.JSONDecodeError):
        return  # Concurrent append may be incomplete; analyzer still reads full original.
    good = [h for h in http if h.get('kind') == 'http'
            and stamp-30 <= o.instant(h['timestamp_utc']) <= stamp
            and o.instant(h['finished_utc']) <= stamp
            and not o.functional_errors(final, h, o.instant(events[0]['timestamp_utc']), stamp)
            and h.get('version') == final['target_version']]
    if not active <= {h.get('resource_id') for h in good}:
        return
    old = {i['id'] for i in json.loads((folder/'preparation.json').read_text())['controller']['instances']}
    if not old.isdisjoint({i['id'] for i in row['instances']}):
        return
    o.validate_config(final)
    exclusive(folder/'config.final.json', final)
    events.append(dict(kind='stabilized', run_id=c['run_id'], controller_id=events[0]['controller_id'],
                       timestamp_utc=now, controller_sample_seq=row['seq'], http_sample_seqs=[h['seq'] for h in good]))
    atomic_events(folder/'events.jsonl', events)


def controller(c, folder, seconds):
    o.require(not (folder/'events.jsonl').exists(), 'Events already exist; do not reuse an attempt')
    armed = o.utc_now()
    original = o.controller_sample
    writer = o.Records.write

    def sample(config, events):
        def query(context, service, action, arguments):
            result = o.aws_read(context, service, action, arguments)
            if action == 'describe-instance-refreshes' and not events:
                candidates = [r for r in result['InstanceRefreshes'] if o.instant(r['StartTime']) >= o.instant(armed)]
                o.require(len(candidates) <= 1, 'Multiple refreshes since observer armed')
                if candidates:
                    r = candidates[0]
                    events.append(dict(kind='change_started', run_id=c['run_id'], controller_id=r['InstanceRefreshId'], timestamp_utc=r['StartTime']))
                    atomic_events(folder/'events.jsonl', events)
            return result
        return original(config, events, query=query)

    def write(records, row):
        writer(records, row)
        if row.get('kind') == 'controller':
            stabilize(c, folder, rows(folder/'events.jsonl'), row)

    baseline = original(c, [])
    o.require(not baseline['errors'] and len(o.healthy_ids(baseline)) == c['base_capacity'], 'Controller cannot arm: '+str(baseline['errors']))
    o.controller_sample = sample
    o.Records.write = write
    return o.monitor(c, 'controller', folder/'events.jsonl', folder, seconds)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=['prepare', 'controller', 'baseline'])
    p.add_argument('--directory', required=True)
    p.add_argument('--allow-network', action='store_true')
    p.add_argument('--max-seconds', type=int, default=3600)
    a = p.parse_args()
    folder = Path(a.directory).resolve()
    if a.mode == 'prepare':
        o.require(a.allow_network, 'Explicit network opt-in required')
        prepare(folder)
        return 0
    c = o.validate_config(json.loads((folder/'config.initial.json').read_text()), allow_pending_target=True)
    if a.mode == 'controller':
        o.require(a.allow_network and a.max_seconds >= 180, 'Network opt-in and sufficient duration required')
        return 0 if controller(c, folder, a.max_seconds) else 1
    http = [r for r in rows(folder/'http.jsonl') if r.get('kind') == 'http']
    controls = [r for r in rows(folder/'controller.jsonl') if r.get('kind') == 'controller']
    now = time.time()
    lower = now-60
    o.require(not rows(folder/'events.jsonl'), 'Change already started')
    for samples, gap, cadence in [(http, 7, 2), (controls, 30, 20)]:
        end = max(o.instant(r['timestamp_utc']) for r in samples)
        o.require(now-end <= gap and o.coverage(samples, lower, end, gap, cadence)['complete'], 'Baseline coverage incomplete')
    recent = [r for r in controls if o.instant(r['timestamp_utc']) >= lower]
    o.require(all(not r['errors'] and len(o.healthy_ids(r)) >= c['base_capacity'] and not r['active_controller_ids']
                  and (r.get('desired'), r.get('minimum'), r.get('maximum')) == (c['base_capacity'], c['base_capacity'], c['base_capacity']+c['temporary_capacity'])
                  for r in recent), 'Baseline controller failed')
    good = [r for r in http if o.instant(r['timestamp_utc']) >= lower]
    o.require(all(not o.functional_errors(c, r, float('inf'), float('inf')) for r in good), 'Baseline HTTP failed')
    o.require(o.healthy_ids(recent[-1]) <= {r.get('resource_id') for r in good}, 'Missing backend baseline response')
    print('BASELINE READY at '+o.utc_now()+'; both monitors must remain running; authorize change promptly.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
