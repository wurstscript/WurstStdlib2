# AGENTS.md - Wurst Standard Library 2 (pre1.29)

Notes for editing `.wurst` code in the **Wurst Standard Library** repo. This is
a library, not a map project: most packages here are the wrappers and
abstractions that consuming map projects build on, so API shape, naming, and
backwards compatibility matter more than in app code.

## Branch Context: pre1.29 (legacy patch)

This branch targets the **pre-1.29 Warcraft III patches**, i.e. patch **1.28
and lower**.

- It intentionally does **not** contain all of the latest stdlib features.
  Many newer features rely on natives that only exist on patch 1.29+, so they
  cannot be supported here.
- When adding or changing code on this branch, restrict yourself to natives and
  APIs available on 1.28 and earlier. Do not introduce dependencies on
  1.29+-only natives.
- The `master` branch tracks the latest patch and carries the newer features.

## Working Rules

- Prefer simple, maintainable code. Fix root causes; avoid brittle workarounds, duplicated branches, and special-case patches.
- Keep packages focused and below ~500 lines; split by feature, responsibility, or data type.
- Treat the public API as a contract. Avoid breaking signatures, names, or behavior of exported members without good reason.
- Prefer extension functions over bare natives; prefer `group` for unit sets, `force` for player sets, and `LinkedList` for arbitrary collections.
- When unsure about Wurst syntax or local APIs, inspect nearby working code before guessing.
- Keep tests narrow. Add/update tests for behavior, parsing, compiletime generation, or shared utilities.
- Avoid broad refactors unless they directly reduce risk or complexity for the requested change.
- Fix compiler warnings unless they are intentionally suppressed.

## Agent Workflow

Install dependencies:

```bash
grill install
```

After Wurst changes, run quiet checks first:

```bash
grill typecheck --quiet
grill test --quiet
```

If quiet output reports a failure, rerun narrowly using the failed file, line, package, or test name:

```bash
grill typecheck
grill test PackageOrTestName
```

Avoid full noisy reruns unless there is no target. Done means relevant errors/warnings are fixed or explicitly explained.

## Wurst Essentials

Every `.wurst` file starts with a package; blocks are indentation-based (tabs or 4 spaces, never mixed):

```wurst
package MyPackage
import Wurstunit

init
	print("loaded")
```

- Use `let` unless mutation is needed; prefer obvious type inference. Do not write Jass-style `takes` / `returns nothing`.
- Package members are private by default (`public` to export); class members are public by default (`private`/`protected` to restrict).
- Every package implicitly imports `Wurst` unless `NoWurst` is imported. `import public` re-exports; plain `import` does not.
- Package init is top-to-bottom; imports initialize before importers. Avoid `initlater` unless breaking an unavoidable init cycle.
- `continue` skips an iteration; `skip` is a no-op. Statements end at newline; continue after `(`, `[`, operators, or before `.`, `..`, `)`, `]`.

Naming: packages/classes `UpperCamelCase`; tuples/functions/members/locals `lowerCamelCase`; top-level constants `UPPER_SNAKE_CASE`.

## Preferred Wurst Style

- Prefer extension functions for readable APIs and the `..` cascade operator for setup chains.
- Prefer `vec2` tuples over `location` handles unless required.
- Prefer polymorphism/data modeling over large `instanceof`/`typeId` chains. Avoid unchecked `castTo` unless proven safe.
- Use the highest practical abstraction (e.g. hashmap-style over raw hashtables); drop to lower-level only in critical hot paths.
- Use asset constants from asset packages instead of raw asset path strings.

```wurst
CreateTrigger()
	..registerAnyUnitEvent(EVENT_PLAYER_UNIT_ISSUED_ORDER)
	..addCondition(Condition(function cond))
	..addAction(function action)

public function unit.getX2() returns real
	return GetUnitX(this)
```

Lambdas need a target type (no standalone inference). Closures capture locals by value; stored/object-backed closures often need cleanup. Lambdas used as `code` cannot take parameters or capture locals.

## Classes, Tuples, Generics

`new` objects generally need `destroy`. Tuples are value types and must not be destroyed. `super(...)` must be the first constructor statement; overridden methods require `override`. Interfaces declare required methods; modules (`use`) inject reusable members.

Prefer `T:` generics for performance-sensitive or instance-heavy containers; old `T` generics erase through integer casts and can share storage.

```wurst
class Box<T:>
	T value
```

## Compiletime and Objects

Use compiletime generation for object-editor data. Prefer wrappers and ID generators so IDs stay stable and collision-free; avoid hardcoded new object IDs unless existing code intentionally does so.

```wurst
let value = compiletime(fac(5))

@compiletime function createSpell()
	new AbilityDefinitionMountainKingThunderBolt(SPELL_ID)
		..setName("Wurst Bolt")
```

## Tests

```wurst
package MyTests
import Wurstunit

@Test public function multiplicationWorks()
	12.assertEquals(3 * 4)
```

Tests should be small, deterministic, self-contained, and assertion-driven. If quiet output lists a failed package/test, rerun that target before expanding scope.

## Formatting

- spaces around binary operators (`a + b`); no space before call parentheses (`foo(1)`); no spaces around `.`/`..`; no spaces inside `(` `)` / `[` `]`.
- comments use `// Comment`; doc comments `/** ... */` appear in autocomplete.
- avoid manual horizontal alignment; prefix intentionally unused variables with `_`.

## Pitfalls

- Wurst code must be inside `package`; indentation defines blocks.
- `array.length` is only the initial length.
- `new` objects and stored closure objects often need `destroy`.
- Lambdas need a known target type; lambdas used as `code` cannot capture locals.
- Varargs are limited by Jass's 31-argument limit.

## Guideline Priority

When rules conflict:
1. Correctness
2. Performance requirements of the code path
3. Readability and abstraction level
