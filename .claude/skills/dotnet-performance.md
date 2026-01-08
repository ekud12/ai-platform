---
name: dotnet-performance
description: Performance optimization including memory management, Span, ArrayPool, zero-allocation patterns, and hot path optimization.
allowed-tools: Read, Write, Edit
---

# .NET Performance Patterns (Rules Only)

## Memory Management
- PERF-MEM-001: Use ArrayPool<T>.Shared for temporary buffers
- PERF-MEM-002: Apply ObjectPool<T> for high-allocation objects
- PERF-MEM-003: Implement MemoryPool<T> for custom pooling
- PERF-MEM-004: Use RecyclableMemoryStream over MemoryStream
- PERF-MEM-005: Mandatory in hot paths

## Span and Memory
- PERF-SPAN-001: Use Span<T> for stack-allocated buffers
- PERF-SPAN-002: Apply ReadOnlySpan<T> for read-only slices
- PERF-SPAN-003: Use Memory<T> and ReadOnlyMemory<T> for heap slices
- PERF-SPAN-004: Replace byte[] with Span<byte> in hot paths
- PERF-SPAN-005: Mandatory for parsing and serialization

## Stack Allocation
- PERF-STACK-001: Use stackalloc for small arrays (<1KB)
- PERF-STACK-002: Apply in performance-critical code only
- PERF-STACK-003: Guard with Span<T> for safety
- PERF-STACK-004: Never escape stack-allocated memory

## Value Types
- PERF-VAL-001: Use readonly struct for immutable value types
- PERF-VAL-002: Apply ref readonly for large struct parameters
- PERF-VAL-003: Use record struct for simple value objects
- PERF-VAL-004: ValueTuple for multi-value returns
- PERF-VAL-005: Pass large structs by ref readonly

## Frozen Collections
- PERF-FROZEN-001: Use FrozenDictionary<TKey, TValue> for lookups
- PERF-FROZEN-002: Apply FrozenSet<T> for read-only sets
- PERF-FROZEN-003: Mandatory for configuration and constants
- PERF-FROZEN-004: Build once, read many times

## String Operations
- PERF-STR-001: Use SearchValues<T> for multi-character searches
- PERF-STR-002: Apply string.Create() for formatted strings
- PERF-STR-003: Use Span-based parsing (int.TryParse(ReadOnlySpan<char>))
- PERF-STR-004: Avoid string allocations in loops
- PERF-STR-005: Use interpolated string handlers for logging

## Regex Performance
- PERF-REGEX-001: Use RegexGenerator source generator
- PERF-REGEX-002: Apply RegexOptions.Compiled for reused patterns
- PERF-REGEX-003: Precompile all regexes
- PERF-REGEX-004: Use NonBacktracking mode where possible
- PERF-REGEX-005: Never instantiate in hot paths

## LINQ Optimization
- PERF-LINQ-001: Avoid chained transformations in hot paths
- PERF-LINQ-002: Use single-pass operations
- PERF-LINQ-003: Apply for-loops over LINQ in critical code
- PERF-LINQ-004: Materialize queries explicitly when needed

## Async Performance
- PERF-ASYNC-001: Use ValueTask<T> for sync-fast async methods
- PERF-ASYNC-002: Apply pooled ValueTask where appropriate
- PERF-ASYNC-003: Avoid Task.Run() in libraries
- PERF-ASYNC-004: Use ConfigureAwait(false) in all library code
- PERF-ASYNC-005: Eliminate unnecessary async in hot paths

## Collection Performance
- PERF-COLL-001: Preallocate collections with known size
- PERF-COLL-002: Use List<T>.Capacity to avoid reallocations
- PERF-COLL-003: Apply Dictionary<TKey, TValue> capacity hints
- PERF-COLL-004: No .ToList() or .ToArray() unless required

## Serialization Performance
- PERF-SER-001: Use System.Text.Json with source generators
- PERF-SER-002: Apply JsonSerializerContext for AOT
- PERF-SER-003: Preallocate buffers for serialization
- PERF-SER-004: Use Utf8JsonWriter for direct writing

## Allocation Reduction
- PERF-ALLOC-001: Eliminate boxing in hot paths
- PERF-ALLOC-002: Use struct over class for small types
- PERF-ALLOC-003: Apply readonly to prevent defensive copies
- PERF-ALLOC-004: Cache delegates and lambda allocations

## GC Optimization
- PERF-GC-001: Minimize allocations in Gen 2
- PERF-GC-002: Use object pooling for large objects
- PERF-GC-003: Avoid finalizers where possible
- PERF-GC-004: Implement IDisposable properly

## Interop Performance
- PERF-INTOP-001: Use LibraryImport source generator
- PERF-INTOP-002: Apply Span-based marshalling
- PERF-INTOP-003: Minimize crossing managed/unmanaged boundary
- PERF-INTOP-004: Batch interop calls

## Forbidden Patterns
- PERF-FORBID-001: No .ToList() or .ToArray() in hot paths
- PERF-FORBID-002: No LINQ in performance-critical loops
- PERF-FORBID-003: No boxing in hot paths
- PERF-FORBID-004: No string concatenation in loops
- PERF-FORBID-005: No Regex without compilation
- PERF-FORBID-006: No allocations in tight loops
- PERF-FORBID-007: No Task.Run() in libraries
- PERF-FORBID-008: No reflection in NativeAOT scenarios
