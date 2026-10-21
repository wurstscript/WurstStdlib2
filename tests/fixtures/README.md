# Regression base map

`RegressionBase.w3x` is the 2018 Wurst Team example map (16,582 bytes), retained as
a tracked input for the disposable regression projects. It contains the base
terrain, player setup, and a sample hero; the build injects the current library and
opt-in regression entry point. The Jass and Lua native results in this PR used
this same base map.

The preparer copies it to `ExampleMap.w3x` inside each disposable project and
records its SHA-256 in `source-manifest.json`. Keep this fixture independent of
generated test-map outputs and local root map files.

`RegressionIndexerPolicy.wurst`, `RegressionLateIndexHook.wurst`, and
`UnitIndexer_config.wurst` are installed only
in prepared test maps. They prove that cast registration respects an exclusion
predicate during initialization and explicit deindexing after startup. Keeping
the configuration here prevents it from changing the library or consuming maps.
The importing late-hook package proves that registration cannot index a caster
before later importers install their hooks. The policy fixture also checks queued
listener cancellation, deindex cancellation, forced ID reuse and dispatch order.
