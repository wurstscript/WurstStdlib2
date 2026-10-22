"""Prepare an isolated map for the four fresh-master audit regressions."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

FILES = {
    'list': 'wurst/data/LinkedList.wurst',
    'index': 'wurst/util/UnitIndexer.wurst',
    'history': 'wurst/event/LastOrder.wurst',
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backend', choices=('lua', 'jass'), required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--baseline-ref')
    parser.add_argument('--baseline-file', choices=FILES)
    args = parser.parse_args()
    if not args.name or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in args.name):
        parser.error('name must contain only letters, digits, hyphens and underscores')
    if bool(args.baseline_ref) != bool(args.baseline_file):
        parser.error('baseline-ref and baseline-file must be specified together')
    root = Path(__file__).resolve().parents[1]
    for name in ('tests/fixtures/RegressionBase.w3x', 'wurst.build', 'wurst_run.args',
                 'wurst/tests/RegressionChecks.wurst', 'wurst/tests/RegressionAuditTests.wurst',
                 'wurst/tests/RegressionAbortOrderConsumer.wurst'):
        if not (root / name).is_file():
            parser.error('Required regression input is missing: ' + name)
    destination = root / '_build' / (args.name + '-' + args.backend)
    destination.mkdir(parents=True, exist_ok=False)
    for source in (root / 'wurst').rglob('*.wurst'):
        relative = source.relative_to(root)
        if source.name.endswith('Tests.wurst') or source.name.startswith('StdlibIngame') or 'tests' in relative.parts:
            continue
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    testdir = destination / 'wurst/tests'
    testdir.mkdir()
    for name in ('RegressionChecks.wurst', 'RegressionAuditTests.wurst', 'RegressionAbortOrderConsumer.wurst'):
        shutil.copy2(root / 'wurst/tests' / name, testdir / name)
    baseline_note = None
    if args.baseline_file:
        filename = FILES[args.baseline_file]
        content = subprocess.check_output(['git', 'show', args.baseline_ref + ':' + filename], cwd=root).decode()
        (destination / filename).write_text(content)
    (testdir / 'AuditRegressionRunner.wurst').write_text('''package AuditRegressionRunner
import RegressionChecks
import RegressionAuditTests
import ClosureTimers
import ErrorHandling

var unexpectedErrors = 0
var expectedErrors = 0

class AuditErrors implements ErrorListener
\toverride function onError(string _message)
\t\tif suppressErrorMessages
\t\t\texpectedErrors++
\t\telse
\t\t\tunexpectedErrors++

init
\taddErrorListener(new AuditErrors())
\tdoAfter(1.) ->
\t\tregressionNote("Audit regressions; build=" + REGRESSION_BUILD + "; backend=" + (isLua ? "Lua" : "Jass"))
\t\tregressionGuard("LinkedList", () -> runLinkedListAuditRegressions())
\t\tregressionGuard("order history", () -> runOrderHistoryAuditRegressions())
\t\tregressionGuard("abort order", () -> runAbortOrderAuditRegressions())
\t\tregressionGuard("UnitIndexer", () -> runDeindexAuditRegressions())
\t\tdoAfter(0.5) ->
\t\t\tregressionCheck(abortAuditCompleted, "native abort timer completed")
\t\t\tregressionCheck(unexpectedErrors == 0, "zero uncaught runtime errors")
\t\t\tregressionCheck(expectedErrors == 11, "exactly eleven caught bounds errors")
\t\t\tregressionSummary("AUDIT COMPLETE")
''')
    shutil.copy2(root / 'wurst.build', destination / 'wurst.build')
    shutil.copy2(root / 'tests/fixtures/RegressionBase.w3x', destination / 'ExampleMap.w3x')
    options = [x for x in (root / 'wurst_run.args').read_text().splitlines() if x.strip() != '-lua']
    if args.backend == 'lua':
        options.append('-lua')
    (destination / 'wurst_run.args').write_text('\n'.join(options) + '\n')
    hashes = {str(p.relative_to(destination)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted((destination / 'wurst').rglob('*.wurst'))}
    stamp = hashlib.sha256(json.dumps([hashes, options], sort_keys=True).encode()).hexdigest()[:16]
    support = testdir / 'RegressionChecks.wurst'
    support.write_text(support.read_text().replace('"working-tree"', '"' + stamp + '"'))
    (destination / 'source-manifest.json').write_text(json.dumps({
        'build': stamp, 'backend': args.backend, 'baseline_ref': args.baseline_ref,
        'baseline_file': args.baseline_file, 'baseline_note': baseline_note,
        'files_before_stamp': hashes, 'options': options,
    }, indent=2) + '\n')
    print(destination)


if __name__ == '__main__':
    main()
