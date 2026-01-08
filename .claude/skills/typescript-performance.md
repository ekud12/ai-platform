---
name: typescript-performance
description: TypeScript performance optimization patterns for hot paths, zero-allocation transforms, Map/Set usage, and memory-efficient operations.
allowed-tools: Read, Write, Edit
---

# TypeScript Performance Patterns (Rules Only)

## Purpose
Enforce performance-critical patterns for hot paths, reduce allocations, and optimize memory usage in TypeScript applications.

## Collection Types

### Prefer Efficient Collections
- TS-PERF-001: Use `Map` over objects for dynamic key-value collections
- TS-PERF-002: Use `Set` over arrays for membership testing
- TS-PERF-003: Use `Record<K, V>` for static known-key objects
- TS-PERF-004: Use `Set.has()` instead of `Array.includes()` for large arrays
- TS-PERF-005: Use `Map.get()` instead of object property access for dynamic keys

### Typed Arrays
- TS-PERF-006: Use `Uint8Array`, `Float32Array` for binary/large data
- TS-PERF-007: Use typed arrays for performance-critical numeric operations
- TS-PERF-008: Preallocate typed arrays where size is known
- TS-PERF-009: Use `DataView` for mixed-type binary data

## Array Operations

### Single-Pass Transforms
- TS-PERF-010: Avoid chained `.map().filter()` - use single-pass `.reduce()`
- TS-PERF-011: Avoid `.flatMap()` followed by `.filter()` - combine operations
- TS-PERF-012: Use fused loops instead of multiple transformation passes
- TS-PERF-013: Implement custom iterators for complex transformations

### Preallocation
- TS-PERF-014: Preallocate arrays where size is known
- TS-PERF-015: No implicit `.push()` growth in hot paths
- TS-PERF-016: Use `new Array(size)` then fill, instead of progressive push
- TS-PERF-017: Reserve capacity for buffers and pools upfront

### Array Anti-Patterns
- TS-PERF-018: No `.slice()` or `.concat()` in hot paths unless memoized
- TS-PERF-019: No `.splice()` for removal - use filtering or swap-and-pop
- TS-PERF-020: Avoid `.toString()` or `.join()` on large arrays - use iterators
- TS-PERF-021: No array spreading in hot paths `{...a, ...b}` - use explicit merge

## Regular Expressions

### Regex Optimization
- TS-PERF-022: Compile and reuse regexes - no inline instantiation in loops
- TS-PERF-023: Store regex as constants outside functions
- TS-PERF-024: Avoid catastrophic backtracking patterns
- TS-PERF-025: Use atomic groups or possessive quantifiers where appropriate
- TS-PERF-026: Test regex performance with large inputs

## String Operations

### String Performance
- TS-PERF-027: Use template literals for single concatenations
- TS-PERF-028: Use array join for multiple concatenations
- TS-PERF-029: Avoid repeated string concatenation in loops
- TS-PERF-030: Use `StringBuilder` pattern for complex string building
- TS-PERF-031: No `.substring()` or `.slice()` in tight loops

## Object Operations

### Object Performance
- TS-PERF-032: Deep-freeze all config trees or shared objects
- TS-PERF-033: Use `Object.create(null)` for hash maps (no prototype)
- TS-PERF-034: Avoid `Object.assign` in hot paths - use structured spread or explicit assignment
- TS-PERF-035: Use `structuredClone` for deep copies where appropriate
- TS-PERF-036: Cache computed property access in hot paths

### Property Access
- TS-PERF-037: Extract once, reuse - avoid re-evaluating same expression
- TS-PERF-038: Cache frequently accessed properties in local variables
- TS-PERF-039: Use dot notation over bracket notation where possible
- TS-PERF-040: Avoid dynamic property access in loops

## Number Operations

### Numeric Performance
- TS-PERF-041: Use `Number.isFinite()` instead of implicit coercion
- TS-PERF-042: Use `Number.isInteger()` for integer checks
- TS-PERF-043: Avoid implicit math coercion (`+value`, `~~value`)
- TS-PERF-044: Use bitwise operations for integer math where appropriate
- TS-PERF-045: Use `Math.floor/ceil/round` explicitly, not tricks

## JSON Operations

### JSON Performance
- TS-PERF-046: No `JSON.stringify()` in hot paths - extract required fields
- TS-PERF-047: Use streaming serializers for large objects
- TS-PERF-048: Cache `JSON.stringify()` results where appropriate
- TS-PERF-049: Use selective serialization (only serialize needed fields)
- TS-PERF-050: Avoid `JSON.parse()` in loops - parse once, reuse

## Function Optimization

### Function Performance
- TS-PERF-051: Extract pure functions outside loops
- TS-PERF-052: Use function memoization for expensive pure computations
- TS-PERF-053: Avoid creating closures in hot paths
- TS-PERF-054: Inline small functions in performance-critical paths
- TS-PERF-055: Use arrow functions for callbacks (no `this` binding overhead)

## Memory Management

### Memory Efficiency
- TS-PERF-056: Use object pools for frequently allocated objects
- TS-PERF-057: Implement LRU caches for expensive computations
- TS-PERF-058: Reuse buffers and arrays where safe
- TS-PERF-059: Clear large data structures when done (set to null)
- TS-PERF-060: Use WeakMap/WeakSet for automatic garbage collection

### Zero-Allocation Patterns
- TS-PERF-061: Zero-allocation transforms on stable structures
- TS-PERF-062: Avoid `.slice()`, `.concat()` unless memoized
- TS-PERF-063: Reuse temporary objects in loops
- TS-PERF-064: Use structured pooling for repeat-heavy logic

## Lazy Evaluation

### Deferred Computation
- TS-PERF-065: Lazy evaluation for all logging - no template construction unless needed
- TS-PERF-066: Use generators for large dataset processing
- TS-PERF-067: Implement lazy initialization for expensive resources
- TS-PERF-068: Defer non-critical work with `queueMicrotask`
- TS-PERF-069: Use `requestIdleCallback` for UI update deferral (browser)

## Loop Optimization

### Loop Performance
- TS-PERF-070: Hoist invariant expressions out of loops
- TS-PERF-071: Cache array length in loop variables
- TS-PERF-072: Use `for` loops instead of `.forEach()` in hot paths
- TS-PERF-073: Break early when condition met
- TS-PERF-074: Use `continue` to skip unnecessary iterations

## Iteration Patterns

### Efficient Iteration
- TS-PERF-075: Use iterators and generators for large datasets
- TS-PERF-076: Implement custom iterators for complex traversals
- TS-PERF-077: Use `for...of` for iterables (more efficient than index loops)
- TS-PERF-078: Batch operations in iteration for better cache locality

## Caching Strategies

### Memoization
- TS-PERF-079: Memoize pure function results
- TS-PERF-080: Use LRU cache for bounded memoization
- TS-PERF-081: Cache expensive property getters
- TS-PERF-082: Invalidate caches explicitly when data changes

## Framework Optimization

### React/Vue Performance
- TS-PERF-083: No implicit reactivity without explicit bounds
- TS-PERF-084: Memoize expensive components (React.memo)
- TS-PERF-085: Use useMemo for expensive computations
- TS-PERF-086: Use useCallback to prevent unnecessary re-renders
- TS-PERF-087: Virtualize long lists
- TS-PERF-088: Code-split large components

## Network Optimization

### API Performance
- TS-PERF-089: Batch API requests where possible
- TS-PERF-090: Implement request deduplication
- TS-PERF-091: Use streaming for large responses
- TS-PERF-092: Compress request/response payloads
- TS-PERF-093: Implement proper pagination (no unbounded queries)

## Profiling & Monitoring

### Performance Monitoring
- TS-PERF-094: Profile hot paths with Chrome DevTools or Node.js profiler
- TS-PERF-095: Use performance.mark() and performance.measure()
- TS-PERF-096: Monitor memory usage and garbage collection
- TS-PERF-097: Track performance metrics over time
- TS-PERF-098: Set performance budgets for critical operations

## Forbidden Patterns

### Performance Anti-Patterns
- TS-PERF-099: No deep cloning in loops or hot paths
- TS-PERF-100: No unnecessary object creation in loops
- TS-PERF-101: No synchronous file I/O in Node.js
- TS-PERF-102: No blocking operations in event loop
- TS-PERF-103: No memory leaks from unclosed resources
- TS-PERF-104: No unbounded data structures
- TS-PERF-105: No quadratic algorithms where linear exists

## Activation Criteria
Use these patterns when:
- Optimizing hot paths and performance-critical code
- Reducing memory allocations and garbage collection
- Improving application responsiveness
- Meeting performance budgets and SLAs
