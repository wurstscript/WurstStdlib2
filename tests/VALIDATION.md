# Regression validation - 2026-10-21

Based on master `f0dcafc`, including the shared frame bridge restored by PR #514.
Changes already fixed on master are covered by regressions without reimplementing
them. Final acceptance still has the explicit gaps below.

## Completed checks

- Repository typecheck succeeds; full interpreter suite: **748/748 passed**.
- Disposable Jass and Lua maps compile, including native event, timer, terrain,
  bounds and interactive fixtures.
- Review follow-up: the base map is now tracked at
  `tests/fixtures/RegressionBase.w3x`. Preparation succeeds for both backends from
  a tracked-files-only export with no root `ExampleMap.w3x`. All three preparer CLI
  tests pass; the same tests fail against the old preparer (four assertion
  failures), reproducing the fresh-checkout issue.
- Shared frame/key bridge guard and its seven self-tests pass. It rejects
  per-registration trigger creation, extra bridges/actions and native-condition
  dispatch. Input-counting oracle triggers exist only in the opt-in test fixture.
- Native runs used Warcraft III **3.0.1.24371**, with authenticated terminal reports
  and preserved artifacts. Each before case replaces the relevant production
  package in the same fixture.

## Native before/after evidence

| Scenario | Before | Fixed source |
| --- | --- | --- |
| Automatic suite, Lua (including startup lifecycle) | See isolated cases below | **99/99 pass**, zero uncaught errors, 16 expected caught bounds errors |
| Automatic suite, Jass (including startup lifecycle) | Isolated before cases tested on Lua | **90/90 pass**, zero uncaught errors, 16 expected caught bounds errors |
| ArrayList invalid bounds / adjacent storage | master package: **51/72**, invalid results and storage corruption | Lua and Jass automatic suites pass |
| TimedLoop destroyed object ID reuse | master package: **71/72**, replacement ticks too often | Lua and Jass automatic suites pass |
| Terrain normal axis sampling | master package: **71/72**, independent tangent comparison fails | Lua and Jass automatic suites pass |
| Init spell registration | master package: **71/72**, real spell effect misses unit listener | Lua and Jass automatic suites pass |
| Init exclusions and explicit runtime deindexing | `507df7b` ClosureEvents: **76/82**, six policy/real-cast checks fail | Lua **82/82**, Jass **73/73**; rejected units stay unindexed, fire no index hooks, and receive no unit-specific cast callback |
| Deferred indexing and pending-listener lifetime | `f8c673f` ClosureEvents: **97/99**, eager indexing misses the later package's hook | Lua **99/99**, Jass **90/90**; late hook sees the caster once, cancellation/deindexing survive forced listener-ID reuse, and mixed registrations retain newest-first dispatch |
| Frame registration and mutation | `4727413` package: **13/19**, duplicate callbacks and mutation failures; one uncaught E66 in `ClosureFrames.onEvent` | Lua real-input suite **19/19**, zero errors |
| Player-specific key filtering | `4727413` package: **17/19**, other player's listener fires | Lua real-input suite **19/19**, zero errors |
| Unit/global/nested listener mutation | `4727413` package: **67/76**, removed successors execute and callback errors occur | Lua and Jass automatic suites pass |

Jass has fewer bounds assertions because its failing child thread exits before
the return-value assertion; Lua continues and verifies the default result too.
The Lua input run delivered two independently counted native inputs to each
tested button/key, including both buttons created inside a click callback.
Player 0's F6 listener matched the raw oracle; player 1's listener remained silent.

The final implementation does not force indexing. Init-time requests for unindexed
units wait until the normal deferred indexing pass completes; units left unindexed
remain rejected. Later init-time requests for a unit already awaiting binding join
the same queue, preserving order even if the map manually indexes it meanwhile.
Destroying a listener clears its queued slot before ID reuse; deindexing a unit
cancels its queued registrations. After startup, an unindexed unit remains rejected.
The exclusion configuration is installed only into disposable maps from
`tests/fixtures/`; a separate importing package installs the late index hook.
Historical subset results remain recorded above and in `native-results.json`.
The original spell-mutation fixture now filters its global counters to its own
caster, so the policy fixture's real casts cannot interfere with it.
The deindex-ID fixture retains intervening allocations until the listener ID is
reused (bounded to eight); Lua also frees the UnitIndex object, so assuming the
listener ID is the very next allocation gave an inconclusive earlier attempt.

## Remaining verification and limits

- **Jass UI now passes 19/19**, with zero runtime errors. The completion run used
  1x game speed and 850 ms between clicks. The earlier 16/17 attempt missed one
  input according to its independent oracle; it remains recorded as an incomplete
  attempt, not a pass.
- **Two-client multiplayer input remains unverified and unavailable in the
  maintainer's 3.0.1 setup.** The maintainer confirmed that a second connected
  client is not available. Two disconnected local games would not establish
  multiplayer behavior. Single-client filtering does not prove synchronization.
- **Castle Fight's PR #514 failure is not reproduced by this generic fixture.**
  The per-pair implementation from `cce7909` also passed 19/19 real-input checks,
  including callback-created buttons. The structural guard rejects that design,
  but this is not behavioral proof of the specific Castle Fight regression.
- Earlier input attempts failed because no key input arrived or foreground
  acquisition failed. Those attempts are not counted as passes. Foreground input
  automation was disabled at the user's request. The maintainer subsequently
  reauthorized foreground input for the completion runs.

## PR #514 analysis

[PR #513](https://github.com/wurstscript/WurstStdlib2/pull/513) replaced the shared
frame bridge with per-`(frame,event)` triggers, identity filtering and retirement
while fixing listener bookkeeping. That unnecessarily changed the engine-facing
registration lifecycle. Dispatcher tests and synthetic clicks did not establish
equivalence for real input. The resulting breakage was reported in Castle Fight.

[PR #514](https://github.com/wurstscript/WurstStdlib2/pull/514) restores the shared
bridge and reports working Campaign/Ready interactions. That supports retaining
the original bridge; it does not isolate the engine mechanism behind the failure.
This task's real-input fixture also cannot establish that mechanism. No measured
performance evidence justifies introducing extra trigger lifecycles.

Production retains one shared frame trigger and one shared key trigger; Wurst
listener calls dispatch after native entry. Future behavioral changes require
relevant failing-before/passing-after native evidence. Missing acceptance evidence
must stay explicit rather than being replaced by compilation or synthetic input.
