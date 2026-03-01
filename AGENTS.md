# AGENTS.md

## WurstScript Project Rules

- Prefer extension functions over calling bare natives directly.
- Prefer chaining extension calls with the `..` cascade operator when it improves readability and keeps call chains efficient.
- Avoid `location` handles. Use `vec2`-based APIs instead.
- For sets of units, prefer `group`.
- For sets of players, prefer `force`.
- For arbitrary data collections, prefer `LinkedList`.
- Use the highest abstraction level that is practical:
  - Example: prefer hashmap-style abstractions over raw hashtable usage when performance is not a critical hot path.
- In critical hot paths, choose the more performant lower-level approach.
- Use asset constants from asset packages instead of raw asset path strings.
- Follow WurstScript language rules strictly (e.g. no `continue`; use valid Wurst constructs only).

## Guideline Priority

When rules conflict:
1. Correctness
2. Performance requirements of the code path
3. Readability and abstraction level
