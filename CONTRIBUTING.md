# Contributing

The standard library has greatly flourished due to amazing feedback, pull requests and issue reports. Bugs and anomalies have been fixed and documented. We highly appreciate any PR with fixes or improvements. However a few points of advice:

* Please keep PRs as small as possible to allow for easier review and faster merging
* Make sure you follow the [Coding Conventions](https://wurstlang.org/manual.html#coding-conventions)
* Keep focused unit tests alongside the end-to-end coverage required below
* Expect there to be requests for changes and suggestions by different members

If further natives need to be implemented for compiletime, they can be requested via a Feature Request.

## Behavior-change test gate

Every behavior change requires an end-to-end regression test and a recorded passing run before merge or release. This includes bug fixes, optimizations, and refactors that affect observable behavior, even when public signatures stay the same.

* Exercise the public API through the real consumer path and assert the observable result. Directly calling an internal dispatcher or mocking the engine event does not prove event registration works.
* For a bug fix, demonstrate that the regression test fails on the buggy revision and passes with the fix. For an intentional behavior change, show the old and new results and state the compatibility impact.
* Run engine-dependent checks in Warcraft III. `grill typecheck` and `grill test` remain required, but the interpreter cannot prove native event delivery, frame interaction, timer behavior, or multiplayer synchronization. Test each affected backend (Jass/Lua), and use multiple clients when locality or synchronization is involved.
* Add automated in-game checks to `wurst/StdlibIngameTests.wurst` where appropriate, or use a focused test-map package for interactive scenarios. Import the test package in a map and run it in the game; compiling a test or adding an unexecuted assertion is not a passing run.
* Record the test source, map/setup, exact reproduction steps or command, Warcraft III version, backend, tested revisions, and failing/passing output in the PR. Interactive tests must have explicit expected results and recorded actual results. Skipped or unavailable scenarios remain unverified and block merge/release of the behavior change.

For frame listeners, use real frame events and check that each live listener runs exactly once per matching event, other frames/event types remain isolated, and removing then re-adding listeners does not duplicate callbacks. Cover listener destruction during dispatch when changing that lifecycle. A synthetic dispatcher call alone misses duplicate native registrations.

Keep the shared native bridge in `ClosureFrames` and `ClosureKeyPresses`; dispatch listeners through Wurst calls. Run `python tests/check_native_bridges.py` when touching either package. For frames, also click a button that creates the next dialog and then click its newly created buttons with real mouse input: `BlzFrameClick` passed on the broken per-pair-trigger implementation in [PR #513](https://github.com/wurstscript/WurstStdlib2/pull/513), fixed by [PR #514](https://github.com/wurstscript/WurstStdlib2/pull/514).

If the runtime or test harness is unavailable, prepare the test and document what remains to run. Keep the change unverified until the required evidence exists; do not substitute a green interpreter-only CI run.

Feel free to join our [Discord](https://discord.gg/mSHZpWcadz) if you would like to contribute.
