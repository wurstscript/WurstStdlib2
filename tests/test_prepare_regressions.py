"""CLI checks using only the preparer's checked-in inputs, without a local map."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


class PrepareRegressionsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        source = Path(__file__).resolve().parents[1]
        for name in ('tests/prepare_regressions.py', 'tests/fixtures/RegressionBase.w3x',
                     'wurst.build', 'wurst_run.args', 'wurst/tests/RegressionChecks.wurst'):
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source / name, target)

    def prepare(self, backend):
        return subprocess.run(
            [sys.executable, str(self.root / 'tests/prepare_regressions.py'),
             '--backend', backend], cwd=self.root.parent,
            text=True, capture_output=True)

    def test_both_backends_prepare_without_an_ignored_root_map(self):
        self.assertFalse((self.root / 'ExampleMap.w3x').exists())
        base = (self.root / 'tests/fixtures/RegressionBase.w3x').read_bytes()
        for backend in ('jass', 'lua'):
            with self.subTest(backend=backend):
                result = self.prepare(backend)
                self.assertEqual(result.returncode, 0, result.stderr)
                project = self.root / '_build' / ('regression-map-' + backend)
                self.assertEqual((project / 'ExampleMap.w3x').read_bytes(), base)
                manifest = json.loads((project / 'source-manifest.json').read_text())
                self.assertEqual(manifest['base_map_sha256'], hashlib.sha256(base).hexdigest())
                self.assertEqual(manifest['backend'], backend)
                options = (project / 'wurst_run.args').read_text().splitlines()
                self.assertEqual('-lua' in options, backend == 'lua')
                self.assertIn('"' + manifest['build'] + '"',
                              (project / 'wurst/tests/RegressionChecks.wurst').read_text())

    def test_missing_fixture_fails_before_creating_a_project(self):
        (self.root / 'tests/fixtures/RegressionBase.w3x').unlink()
        result = self.prepare('lua')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Required regression input is missing', result.stderr)
        self.assertFalse((self.root / '_build').exists())

    def test_repeated_preparation_preserves_existing_evidence(self):
        self.assertEqual(self.prepare('lua').returncode, 0)
        project = self.root / '_build/regression-map-lua'
        evidence = project / 'runtime-report.txt'
        evidence.write_text('preserve this run')
        self.assertNotEqual(self.prepare('lua').returncode, 0)
        self.assertEqual(evidence.read_text(), 'preserve this run')


if __name__ == '__main__':
    unittest.main()
