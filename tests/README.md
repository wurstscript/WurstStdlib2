# Runtime regression suite

Run `rtk proxy python tests/check_native_bridges.py` to guard the single native
frame/key bridge. `--self-test` checks that the guard rejects per-pair triggers,
extra native actions and native-condition dispatch. This is a structural check,
not proof that the engine delivers events.

`wurst/tests/StdlibRegressionTests.wurst` is an opt-in test-map entry point.
Import `StdlibRegressionTests` into a disposable map to run the suite. Never import
it into a shipping map: it creates test units, UI and temporary terrain deformation.
The repository build compiles all its own source packages, so the offline copy below
already includes the entry point. Existing consuming maps do not import it implicitly.

## Prepare and run

From the repository root, prepare separate copies for both backends:

The tracked `tests/fixtures/RegressionBase.w3x` supplies the base map, so these
commands work in a fresh checkout without an ignored root `ExampleMap.w3x`.
The preparer also installs the indexing-policy fixture and its test-only
`UnitIndexer_config` from `tests/fixtures/`; these stay outside library sources so
they cannot replace a consuming map's indexing policy.

```powershell
rtk proxy python tests/prepare_regressions.py --backend jass --name after
rtk proxy python tests/prepare_regressions.py --backend lua --name after
```

In each printed project directory run:

```powershell
rtk proxy grill build ExampleMap.w3x --quiet
rtk proxy grill run ExampleMap.w3x --quiet
```

Keep the generated map, compiler version, Warcraft III build, backend, source revision
and run log together. The `backend=` line in the runtime report must match the build
being tested. The report's `build=` must match `source-manifest.json` in that project.
A launcher message or successful compilation does not prove a game run.

Run `python -m unittest discover -s tests -p "test_prepare_regressions.py"` to check
preparation from a clean input tree, backend selection, and missing-input handling.

Automatic checks start one second into the game and finish approximately 1.5 seconds
later. The report is printed and written to
`Documents/Warcraft III/CustomMapData/WurstStdlibRegressions.txt` on every client.
Preserve each report before launching another run; verify its timestamp is fresh.

For UI/key checks, enable human slots 0 and 1 in the test map and host it with two
human clients. On either client click buttons 1 and 2 twice, then click button 3 to
create the next dialog inside its click handler. Click BOTH newly created buttons
(4 and 5) twice using real mouse clicks. `BlzFrameClick` is insufficient: it passed
on the broken per-pair-trigger implementation corrected by PR #514. Players 0 and 1
must each press F6 twice without modifiers; also press F7 twice. Close chat before
pressing keys. Then type `-stdlibregressionfinish`. Compare both clients' reports.
Missing input is a failure at finalization; an automatic summary still says
`INTERACTIVE PENDING`. Every recorded check must pass on both clients.

## Coverage and expected regression failures

| Fix | Real consumer path | Before-fix failure |
| --- | --- | --- |
| Player key isolation | F6 for two players plus a global listener; independent native trigger counts inputs | Both player callbacks run for either player's key |
| TimedLoop lifetime | Destroy a running object, immediately reuse its ID, start replacement/control; destroy self and another object during native timer dispatch | Stale-slot access, duplicate replacement ticks, or missing surviving ticks |
| Listener mutation | Actual stop orders (unit/global/nested), an actual Berserk cast (unit/global), frame clicks and F7 | Removed successor runs, traversal crashes, or tail is skipped |
| ArrayList bounds | Public get/set/removal/insertion/truncate against two adjacent capacity-one lists | Lua continues after error, mutates size/data or reads/writes neighbouring storage |
| Frame registration lifetime | Remove/re-add the last click listener three times, then keep two listeners; independent native trigger counts real clicks | Live listeners run multiple times per click |
| Shared frame bridge (#514) | Real click creates two new buttons; real clicks on each new button | Guards the reported failure path; the generic fixture also passes the old per-pair implementation, so Castle Fight's specific regression remains unreproduced |
| Spell registration before indexing | Create and register caster during init, then issue a real Berserk order after init | Listener left at index zero misses the spell effect |
| Indexing-policy compatibility | Exclude an init caster via `shouldIndex`; explicitly deindex a runtime caster; issue real casts from both | Registration force-indexes excluded/recycled units, fires index hooks and receives their casts |
| Deferred startup registration | Install a later package's index hook; cancel queued listeners and deindex queued units with forced object-id reuse; mix registration and manual indexing | Eager indexing bypasses the late hook; queue mistakes resurrect cancelled listeners or reverse dispatch order |
| Terrain Y normal | Temporary asymmetric terrain sample; compare public normal with cross product of actual X/Y surface tangents | Y uses the X slope; a flat/non-distinguishing fixture also fails |

Invalid ArrayList operations run inside `try`: Jass ends the child thread, while Lua
returns from `error()`. Both must report an error and preserve the two lists. **Lua
execution is required to prove that fix**; interpreter/Jass checks alone cannot.
Terrain heights are used only for diagnostic assertions, never gameplay decisions.
Frames and input registrations are created synchronously and retained for the map's
lifetime; the suite does not destroy UI frames.

## Before/after evidence

Run exactly the same tests against the old implementation. For a clean historical
baseline, prepare copies with `--baseline-ref <commit>` and a different `--name`.
This changes only the six repaired production files; it keeps the tests identical.
For a baseline containing local edits, preserve those six files before applying fixes
and restore them only inside a disposable prepared project.

The interpreter supplement can also run in either project:

```powershell
rtk proxy grill test RegressionRegistrationTests --quiet
```

It checks that registration does not force indexing or write a listener into index
zero. Deferred binding, late index hooks, cancellation, and real spell effects are
asserted separately in the game. Interpreter tests do not stand in for native
event/input or timer execution.
