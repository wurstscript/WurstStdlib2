# Maintained unit subsets

`UnitSpatialGroup` shares `UnitSpatialIndex`'s position cache, sweep and conservative movement bound,
but keeps its own partition chains. Querying defenders does not visit a crowd of enemies beside them.

```wurst
constant UnitSpatialPredicate DEFENDERS = u -> u.getOwner() == Player(0) and u.isAlive()
constant defenders = new UnitSpatialGroup(DEFENDERS)

let count = defenders.beginQuery(center, radius)
for i = 0 to count - 1
    let u = spatialIndexQueryUnit(i)
    // Use u; nested queries keep independent snapshots.
spatialIndexEndQuery()
```

Predicates must be synchronous and side-effect free. They run when units register or refresh and are
rechecked before returning a match. When predicate inputs change, call `unit.updateSpatialIndex()` to
make new membership visible immediately. Call it after teleports and collision-size changes too.
The caller owns the predicate; destroy the group before destroying its predicate. Destroying a group
removes its membership and releases its partition group for reuse.

Explicit subsets apply their predicate as their visibility policy. Ordinary `SpatialIndexForUnits`
queries continue to follow Warcraft's range/rect enumeration rules (including corpses, excluding
hidden and live Locust units). A subset can include hidden/Locust units if its predicate allows them.

Pair every `beginQuery` with `spatialIndexEndQuery`, including empty queries. The shared snapshot
releases handles on close and has no fixed result cap. Do not yield or run arbitrary callbacks while
a raw snapshot is open; copy it into a caller-owned list and close it first for those uses.

Collision queries use squared distance against `radius + cachedCollisionSize`. Registration and
refresh update that size. `MAX_COLLISION_SIZE` must cover the map's unit sizes, as with the native
closure's broadphase. The interpreter cannot read collision size; tests inject known cached radii,
and live engine parity needs an in-game test.

# Degenerate queries

The partition chooses a dense per-group scan when the query's cell window costs at least as much as
visiting that group's members. It retains coarse occupancy pruning for narrower grid windows.
Cells with at least `SPATIAL_PARTITION_SPLIT_THRESHOLD` members subdivide into sixteen chains until
they empty; movement inside the original cell updates those chains too. A tight query then visits
only intersecting subcells. A pile at one exact point necessarily costs its matching population.
All routes use the same distance and uncertainty tests; none caps or samples answers.

`spatialPartitionLastQueryVisits`, `spatialPartitionLastQueryBlocksSkipped` and
`spatialPartitionLastQueryUsedDenseScan` expose deterministic work counters for calibration.
Subdivision is enabled on Lua and in compiletime tests; Jass runtime retains the bounded fine grid.
