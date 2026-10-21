"""Prepare an offline, disposable test project without modifying the source map.

Run from any directory. Requires Python 3; the base map is a tracked test fixture.
Use --baseline-ref to replace only the six repaired production files with an older revision;
the current regression tests stay identical. No commands are executed in the prepared project.
"""
import argparse
from pathlib import Path
import shutil
import subprocess
import hashlib
import json

REPAIRED = (
    'wurst/closures/ClosureEvents.wurst',
    'wurst/closures/ClosureFrames.wurst',
    'wurst/closures/ClosureKeyPresses.wurst',
    'wurst/data/ArrayList.wurst',
    'wurst/util/TimerUtils.wurst',
    'wurst/util/TerrainUtils.wurst',
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backend', choices=('jass', 'lua'), required=True)
    parser.add_argument('--baseline-ref', help='Git revision for the repaired files only')
    parser.add_argument('--name', default='regression-map')
    args = parser.parse_args()
    if not args.name or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in args.name):
        parser.error('--name must contain only letters, digits, hyphens and underscores')
    root = Path(__file__).resolve().parents[1]
    base_map = root / 'tests/fixtures/RegressionBase.w3x'
    for required in (base_map, root / 'wurst.build', root / 'wurst_run.args',
                     root / 'wurst/tests/RegressionChecks.wurst'):
        if not required.is_file():
            parser.error('Required regression input is missing: ' + str(required))
    destination = root / '_build' / (args.name + '-' + args.backend)
    # Never overwrite another prepared run or its evidence.
    destination.mkdir(parents=True, exist_ok=False)
    shutil.copytree(root / 'wurst', destination / 'wurst')
    shutil.copy2(root / 'wurst.build', destination / 'wurst.build')
    shutil.copy2(base_map, destination / 'ExampleMap.w3x')
    options = [line for line in (root / 'wurst_run.args').read_text().splitlines() if line.strip() != '-lua']
    if args.backend == 'lua':
        options.append('-lua')
    (destination / 'wurst_run.args').write_text('\n'.join(options) + '\n')
    if args.baseline_ref:
        for filename in REPAIRED:
            content = subprocess.check_output(['git', 'show', args.baseline_ref + ':' + filename], cwd=root)
            (destination / filename).write_bytes(content)
    files = {str(path.relative_to(destination)).replace('\\', '/'): hashlib.sha256(path.read_bytes()).hexdigest()
             for path in sorted((destination / 'wurst').rglob('*.wurst'))}
    fingerprint = hashlib.sha256(json.dumps([files, options], sort_keys=True).encode()).hexdigest()
    support = destination / 'wurst/tests/RegressionChecks.wurst'
    support.write_text(support.read_text().replace('"working-tree"', '"' + fingerprint[:16] + '"'))
    (destination / 'source-manifest.json').write_text(json.dumps({
        'build': fingerprint[:16], 'sha256': fingerprint, 'backend': args.backend,
        'base_map_sha256': hashlib.sha256(base_map.read_bytes()).hexdigest(),
        'baseline_ref': args.baseline_ref, 'files_before_stamp': files, 'options': options,
    }, indent=2) + '\n')
    print(destination)
    print('Build there: rtk proxy grill build ExampleMap.w3x --quiet')
    print('Launch there: rtk proxy grill run ExampleMap.w3x --quiet')


if __name__ == '__main__':
    main()
