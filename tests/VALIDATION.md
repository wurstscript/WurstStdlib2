# Regression validation - 2026-10-21

Based on master `f0dcafc`, including the shared frame bridge restored by PR #514.
Changes already fixed on master are covered by regressions without reimplementing
them. Final acceptance still has the explicit gaps below.

## Completed checks

- Repository typecheck succeeds; full interpreter suite: **748/748 passed**.
- Disposable Jass and Lua maps compile, including native event, timer, terrain,
  bounds and interactive fixtures.
- Shared frame/key bridge guard and its seven self-tests pass. It rejects
  per-registration trigger creation, extra bridges/actions and native-condition
  dispatch. Input-counting oracle triggers exist only in the opt-in test fixture.
- Native runs used Warcraft III **3.0.1.24371**, with authenticated terminal reports
  and preserved artifacts. Each before case replaces the relevant production
  package in the same fixture.

## Native before/after evidence

| Scenario | Before | Fixed source |
| --- | --- | --- |
| Automatic suite, Lua | See isolated cases below | **72/72 pass**, zero uncaught errors, 16 expected caught bounds errors |
| Automatic suite, Jass | Isolated before cases tested on Lua | **63/63 pass**, zero uncaught errors, 16 expected caught bounds errors |
| ArrayList invalid bounds / adjacent storage | master package: **51/72**, invalid results and storage corruption | Lua and Jass automatic suites pass |
| TimedLoop destroyed object ID reuse | master package: **71/72**, replacement ticks too often | Lua and Jass automatic suites pass |
| Terrain normal axis sampling | master package: **71/72**, independent tangent comparison fails | Lua and Jass automatic suites pass |
| Init spell registration | master package: **71/72**, real spell effect misses unit listener | Lua and Jass automatic suites pass |
| Frame registration and mutation | `4727413` package: **13/19**, duplicate callbacks and mutation failures; one uncaught E66 in `ClosureFrames.onEvent` | Lua real-input suite **19/19**, zero errors |
| Player-specific key filtering | `4727413` package: **17/19**, other player's listener fires | Lua real-input suite **19/19**, zero errors |
| Unit/global/nested listener mutation | `4727413` package: **67/76**, removed successors execute and callback errors occur | Lua and Jass automatic suites pass |

Jass has fewer bounds assertions because its failing child thread exits before
the return-value assertion; Lua continues and verifies the default result too.
The Lua input run delivered two independently counted native inputs to each
tested button/key, including both buttons created inside a click callback.
Player 0's F6 listener matched the raw oracle; player 1's listener remained silent.

## Remaining verification and limits

- **Jass UI is incomplete:** the input oracle observed only one of two initial
  button clicks. Received events matched their listeners, but completion failed
  (16/17). This is not a full pass.
- **Two-client multiplayer input remains unverified.** Single-client filtering
  does not prove both players' input or synchronization.
- **Castle Fight's PR #514 failure is not reproduced by this generic fixture.**
  The per-pair implementation from `cce7909` also passed 19/19 real-input checks,
  including callback-created buttons. The structural guard rejects that design,
  but this is not behavioral proof of the specific Castle Fight regression.
- Earlier input attempts failed because no key input arrived or foreground
  acquisition failed. Those attempts are not counted as passes. Foreground input
  automation was subsequently disabled at the user's request; further execution
  must remain in the background.

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
