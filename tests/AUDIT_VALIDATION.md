# Fresh-master audit fixes — 2026-10-22

Baseline: `fd6dcff3ac7f6a5cf57fa0a255718b4dae142642` (master after #515).

## Changes and compatibility

- LinkedList reports invalid indices and returns before accessing or mutating nodes.
  Lua getters/removal return the default value after reporting an error; setters
  and insertion leave the list unchanged. Valid append-at-size remains supported.
- UnitIndexer rejects same-unit reentrant deindexing. Hooks still see the old
  index, can deindex other units, and retain the outer indexing-unit context.
  The object marks itself as releasing before running hooks, including when
  callers directly destroy its UnitIndex.
- LastOrder re-exports Unit's canonical `abortOrder()` rather than declaring a
  conflicting extension. This also preserves access for NoWurst consumers and
  fixes the old helper's unpause/stop/pause inversion.
- `ORDERS_TO_HOLD` now counts the entire retained history, including the newest
  order. Its default of three retains three rather than four. Consumers relying
  on the accidental fourth entry need to configure a larger limit. A nonpositive
  setting is clamped to one retained order.

## Reproducible native fixture

The opt-in `RegressionAuditTests` package tests public APIs using real unit orders
and native timers. `RegressionAbortOrderConsumer` deliberately imports NoWurst and
LastOrder: the same fixture can exercise the old helper and its replacement.
Ordinary LastOrderTests separately reproduce the old ambiguous-extension compile
error and prevent its return.

From the repository root:

```powershell
rtk proxy python tests/prepare_audit_regressions.py --backend lua --name audit-after
rtk proxy python tests/prepare_audit_regressions.py --backend jass --name audit-after
```

In each printed directory, build and launch the disposable map:

```powershell
rtk proxy grill build ExampleMap.w3x --quiet
rtk proxy grill run ExampleMap.w3x --quiet
```

The map must actually start. After the loading screen, automatic assertions run
and finish with `AUDIT COMPLETE`. The report is written to
`Documents/Warcraft III/CustomMapData/WurstStdlibRegressions.txt`. Check its fresh
timestamp, matching source-manifest build stamp and backend before accepting it.
The standalone runner additionally checks zero uncaught errors, exactly eleven
caught bounds errors, and completion of the native delayed abort assertion.
Keep this test package out of shipping maps.

Prepare a before-fix map by adding `--baseline-ref fd6dcff --baseline-file list`,
`index`, or `history`, with a distinct `--name`. Only that production package is
replaced; tests stay identical. The history baseline includes the original
abortOrder helper unchanged. Its NoWurst consumer can run in game even though a
normal implicit-Wurst consumer fails to compile against that duplicate extension.

## Recorded checks

- `grill typecheck --quiet`: passed.
- `grill test --quiet`: **752/752 passed**.
- Both map preparers: **six Python tests passed**.
- Native bridge guard: **seven self-tests passed**.
- Fresh background native runs used Warcraft III **3.0.1.24371**, at 1x speed,
  with a single client. No foreground PC-control tool was needed for those runs.
  The runner authenticated terminal results using per-run identity, a nonce,
  sequence and checksum; screenshots or launcher success did not determine pass.

Final counts, map hashes, source fingerprints, run identities and failures are
recorded in `audit-native-results.json`. Fixed Lua and Jass runs require zero
failed assertions, zero uncaught errors and exactly eleven caught bounds errors.
Jass has six fewer assertions because a bounds error ends its child thread before
the getter/removal return-value check; Lua continues and checks those values too.

| Production variant | Backend | Passed / assertions | Failed |
| --- | --- | --- | --- |
| Baseline LinkedList only | Lua | 50 / 59 | 9 |
| Baseline UnitIndexer only | Lua | 67 / 70 | 3 |
| Baseline LastOrder only | Lua | 67 / 69 | 2 |
| All fixes | Lua | 69 / 69 | 0 |
| All fixes | Jass | 63 / 63 | 0 |

The before-fix runs must fail for the relevant reason: LinkedList overwrites or
damages list storage, recursive deindexing executes twice and errors, and the old
LastOrder retains a fourth order and leaves an unpaused unit paused. The native
abort check also proves the move order is cancelled and remains stopped across
timer ticks. This work changes no local-player/UI behavior; multiplayer input
coverage from the earlier suite is not claimed here.

The compile-only before check also produced `Call to function abortOrder is
ambiguous`, identifying the Unit and LastOrder declarations. After the fix,
ordinary and NoWurst importing consumers compile and their interpreter tests pass.

Grill's launcher can return status zero while printing a compiler/test failure.
Recorded outcomes use the compiler diagnostics and assertion/terminal results,
not that launcher exit code. Early adapter/build attempts and earlier fixture
iterations are not substituted for the final source-matched matrix.
