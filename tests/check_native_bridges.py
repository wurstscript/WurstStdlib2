"""Guard the shared frame/key bridges; this supplements, never replaces, in-game tests."""
from pathlib import Path
import re
import sys
import unittest


def check_bridge(source):
    # Strip comments while retaining strings as tokens, so comment examples cannot affect counts.
    tokens = re.sub(r'"(?:\\.|[^"\\])*"|//[^\n]*|/\*.*?\*/',
                    lambda m: '""' if m[0].startswith('"') else '', source, flags=re.S)
    errors = []
    if len(re.findall(r'\bCreateTrigger\s*\(', tokens)) != 1:
        errors.append('expected exactly one shared native trigger')
    if not re.search(r'^constant\s+\w+\s*=\s*CreateTrigger\s*\(', tokens, flags=re.M):
        errors.append('the bridge must be created once at package scope, not inside registration')
    if len(re.findall(r'\b(?:addAction|TriggerAddAction)\s*\(', tokens)) != 1:
        errors.append('expected exactly one action bridging into Wurst dispatch')
    if re.search(r'\b(?:addCondition|TriggerAddCondition|TriggerEvaluate|TriggerExecute|evaluate|execute|Condition|Filter)\s*\(', tokens):
        errors.append('native condition/trigger dispatch added to the listener layer')
    return errors


class GuardTests(unittest.TestCase):
    valid = 'constant BRIDGE = CreateTrigger()..addAction(function dispatch)'

    def test_shared_bridge(self):
        self.assertEqual(check_bridge(self.valid), [])

    def test_per_pair_trigger_is_rejected(self):
        # The actual mistake has ONE syntactic factory call, but executes it once per pair.
        self.assertTrue(check_bridge('function addListener()\n let t = CreateTrigger()..addAction(function dispatch)'))

    def test_additional_trigger_is_rejected(self):
        self.assertTrue(check_bridge(self.valid + '\nfunction addListener()\n let t = CreateTrigger()'))

    def test_extra_native_action_is_rejected(self):
        self.assertTrue(check_bridge(self.valid + '\nbridge.addAction(function callback)'))

    def test_native_conditions_are_rejected(self):
        self.assertTrue(check_bridge(self.valid + '\nbridge.addCondition(Condition(function callback))'))

    def test_native_dispatch_wrapper_is_rejected(self):
        self.assertTrue(check_bridge(self.valid + '\nlistenerTrigger.evaluate()'))

    def test_comments_and_strings_do_not_count(self):
        self.assertEqual(check_bridge(self.valid + '\n// CreateTrigger()\n/* addAction() */\n"Filter()"'), [])


if __name__ == '__main__':
    if '--self-test' in sys.argv:
        unittest.main(argv=[sys.argv[0]])
    else:
        root = Path(__file__).resolve().parents[1]
        failed = False
        for name in ('ClosureFrames', 'ClosureKeyPresses'):
            path = root / 'wurst/closures' / (name + '.wurst')
            errors = check_bridge(path.read_text())
            print(name + ': ' + ('; '.join(errors) if errors else 'shared bridge OK'))
            failed |= bool(errors)
        sys.exit(1 if failed else 0)
