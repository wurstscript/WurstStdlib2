"""Ensure the audit map is isolated and reproducible from tracked inputs."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


class PrepareAuditTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        source = Path(__file__).resolve().parents[1]
        for name in ('tests/prepare_audit_regressions.py', 'tests/fixtures/RegressionBase.w3x',
                     'wurst.build', 'wurst_run.args', 'wurst/tests/RegressionChecks.wurst',
                     'wurst/tests/RegressionAuditTests.wurst', 'wurst/data/LinkedList.wurst',
                     'wurst/tests/RegressionAbortOrderConsumer.wurst',
                     'wurst/tests/StdlibRegressionTests.wurst', 'wurst/StdlibIngameTests.wurst'):
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source / name, target)

    def prepare(self, backend='lua', name='probe'):
        return subprocess.run([sys.executable, str(self.root / 'tests/prepare_audit_regressions.py'),
                               '--backend', backend, '--name', name], text=True, capture_output=True)

    def test_backends_only_include_the_selected_native_suite(self):
        for backend in ('lua', 'jass'):
            result = self.prepare(backend)
            self.assertEqual(result.returncode, 0, result.stderr)
            project = self.root / '_build' / ('probe-' + backend)
            self.assertFalse((project / 'wurst/StdlibIngameTests.wurst').exists())
            self.assertFalse((project / 'wurst/tests/StdlibRegressionTests.wurst').exists())
            self.assertTrue((project / 'wurst/data/LinkedList.wurst').is_file())
            self.assertEqual('-lua' in (project / 'wurst_run.args').read_text().splitlines(), backend == 'lua')
            manifest = json.loads((project / 'source-manifest.json').read_text())
            self.assertIn(manifest['build'], (project / 'wurst/tests/RegressionChecks.wurst').read_text())
            self.assertIn('abortAuditCompleted', (project / 'wurst/tests/AuditRegressionRunner.wurst').read_text())

    def test_missing_input_does_not_create_a_partial_project(self):
        (self.root / 'tests/fixtures/RegressionBase.w3x').unlink()
        self.assertNotEqual(self.prepare().returncode, 0)
        self.assertFalse((self.root / '_build').exists())

    def test_repeated_runs_preserve_the_previous_project(self):
        self.assertEqual(self.prepare().returncode, 0)
        marker = self.root / '_build/probe-lua/retained.txt'
        marker.write_text('evidence')
        self.assertNotEqual(self.prepare().returncode, 0)
        self.assertEqual(marker.read_text(), 'evidence')


if __name__ == '__main__':
    unittest.main()
