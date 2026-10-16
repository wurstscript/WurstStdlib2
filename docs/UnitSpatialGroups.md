# Maintained unit subsets

`UnitSpatialGroup` shares `UnitSpatialIndex`'s position cache, sweep and conservative movement bound,
but keeps its own partition chains. Querying defenders does not visit a crowd of enemies beside them.

```wurst
constant UnitSpatialPredicate DEFENDERS = u -> u.getOwner() == Player(0) and u.isAlive()
constant defenders = new UnitSpatialGroup(DEFENDERS)

// On indexed unit creation and every owner/alive eligibility change:
// defenders.refreshMembership(changedUnit)

let count = defenders.beginQuery(center, radius)
for i = 0 to count - 1
    let u = spatialIndexQueryUnit(i)
    // Use u; nested queries keep independent snapshots.
spatialIndexEndQuery()
```

Predicates must be synchronous and side-effect free. Membership is event-owned by default: notify the
group with `defenders.refreshMembership(u)` after registration and predicate input changes. The
predicate is rechecked before returning a match. Call `unit.updateSpatialIndex()` after teleports and
collision-size changes; position updates do not poll event-owned membership.
The caller owns the predicate; destroy the group before destroying its predicate. Destroying a group
removes its membership and releases its partition group for reuse.

For event-owned membership, use `new UnitSpatialGroup(DEFENDERS)` and call
`defenders.refreshMembership(u)` when an input changes. These groups do not run predicates during
position refreshes or the periodic sweep. Construction populates existing indexed units; later
registrations need an explicit membership refresh. The query still checks the predicate, so stale
members are rejected immediately. The caller must notify newly eligible units. Membership refresh
does not register units and is safe during deindex. This mode suits a map that already owns spawn,
death and membership-state hooks. A map that needs periodic membership polling owns that schedule
and calls `refreshMembership` from it. The position sweep contains no predicate list, callback loop
or membership-policy work. `updateSpatialIndex()` updates spatial data, not caller-owned membership.

Explicit subsets apply their predicate as their visibility policy. Ordinary `SpatialIndexForUnits`
queries continue to follow Warcraft's range/rect enumeration rules (including corpses, excluding
hidden and live Locust units). A subset can include hidden/Locust units if its predicate allows them.

Pair every `beginQuery` with `spatialIndexEndQuery`, including empty queries. The shared snapshot
releases handles on close and has no fixed result cap. Do not yield or run arbitrary callbacks while
a raw snapshot is open; copy it into a caller-owned list and close it first for those uses.

Collision queries use squared distance against `radius + cachedCollisionSize`. Only collision queries
read that size, at most once per unit per sweep tick. An explicit `updateSpatialIndex()` invalidates
it immediately, including mutations within the same tick. Position sweeps do not read collision size.
`MAX_COLLISION_SIZE` must cover the map's unit sizes, as with the native
closure's broadphase. The interpreter cannot read collision size; tests inject known cached radii,
and live engine parity needs an in-game test.

# Degenerate queries

The partition chooses a dense per-group scan when the query's cell window costs at least as much as
visiting that group's members. It retains coarse occupancy pruning for narrower grid windows.
Tight queries in cells with at least `SPATIAL_PARTITION_SPLIT_THRESHOLD` members lazily cache sixteen
subcell chains. Position and membership changes invalidate the cell's cache; the next tight query
rebuilds it from the main chains. Refreshes do not maintain subcells, and full-cell/dense queries
need no subcell cache. Repeated tight queries visit only intersecting subcells. A pile at one exact
point necessarily costs its matching population.
All routes use the same distance and uncertainty tests; none caps or samples answers.

`spatialPartitionLastQueryVisits`, `spatialPartitionLastQueryBlocksSkipped` and
`spatialPartitionLastQueryUsedDenseScan` expose deterministic traversal counters for calibration.
`spatialPartitionLastQueryRebuildVisits` separately reports entries read to rebuild subcell caches;
include that work when assessing a cold or invalidated query, rather than counting traversal alone.
Subdivision is enabled on Lua and in compiletime tests; Jass runtime retains the bounded fine grid.
