---
name: dotnet-concurrency
description: Concurrency and async patterns including Channels, IAsyncEnumerable, parallel operations, and structured concurrency.
allowed-tools: Read, Write, Edit
---

# Concurrency Patterns (Rules Only)

## Async/Await Fundamentals
- ASYNC-BASE-001: Use async/await for all I/O operations
- ASYNC-BASE-002: Never block with .Result or .Wait()
- ASYNC-BASE-003: Apply ConfigureAwait(false) in libraries
- ASYNC-BASE-004: Use ValueTask<T> for sync-fast paths
- ASYNC-BASE-005: Avoid async void except for event handlers

## Cancellation
- ASYNC-CANCEL-001: Accept CancellationToken in all async methods
- ASYNC-CANCEL-002: Propagate cancellation to nested calls
- ASYNC-CANCEL-003: Respect cancellation in loops
- ASYNC-CANCEL-004: Use CancellationTokenSource.CreateLinkedTokenSource() for child operations
- ASYNC-CANCEL-005: Dispose CancellationTokenSource properly

## System.Threading.Channels
- ASYNC-CHAN-001: Use for producer-consumer patterns
- ASYNC-CHAN-002: Apply bounded channels for backpressure
- ASYNC-CHAN-003: Use unbounded only with throttling
- ASYNC-CHAN-004: Prefer over Queue<T> for async scenarios
- ASYNC-CHAN-005: Implement graceful shutdown

## IAsyncEnumerable<T>
- ASYNC-ENUM-001: Use for streaming data
- ASYNC-ENUM-002: Support cancellation via CancellationToken
- ASYNC-ENUM-003: Apply for database query streaming
- ASYNC-ENUM-004: Use await foreach for consumption
- ASYNC-ENUM-005: Implement IAsyncDisposable properly

## Parallel Operations
- ASYNC-PARA-001: Use Parallel.ForEachAsync for concurrent work
- ASYNC-PARA-002: Apply MaxDegreeOfParallelism limits
- ASYNC-PARA-003: Respect CancellationToken
- ASYNC-PARA-004: Use for CPU-bound parallel operations
- ASYNC-PARA-005: Avoid for I/O-bound work (use async instead)

## Task Combinators
- ASYNC-COMB-001: Use Task.WhenAll for parallel async operations
- ASYNC-COMB-002: Apply Task.WhenAny for timeout/race scenarios
- ASYNC-COMB-003: Use ValueTask where appropriate
- ASYNC-COMB-004: Avoid creating unnecessary Task wrappers

## Throttling
- ASYNC-THROT-001: Use SemaphoreSlim for concurrency limits
- ASYNC-THROT-002: Apply rate limiting for API calls
- ASYNC-THROT-003: Implement token bucket or leaky bucket
- ASYNC-THROT-004: Use channels with bounded capacity

## Backpressure
- ASYNC-BACK-001: Implement in producer-consumer scenarios
- ASYNC-BACK-002: Use bounded channels
- ASYNC-BACK-003: Apply flow control in streaming
- ASYNC-BACK-004: Monitor queue depths

## Structured Concurrency
- ASYNC-STRUCT-001: Link CancellationTokenSource for parent-child relationships
- ASYNC-STRUCT-002: Cancel child tasks when parent cancels
- ASYNC-STRUCT-003: Wait for all child tasks before completion
- ASYNC-STRUCT-004: Implement proper cleanup on cancellation

## Thread Safety
- ASYNC-SAFE-001: Use ConcurrentDictionary for thread-safe caching
- ASYNC-SAFE-002: Apply ImmutableCollections for shared state
- ASYNC-SAFE-003: Use Interlocked for atomic operations
- ASYNC-SAFE-004: Implement lock-free algorithms where possible
- ASYNC-SAFE-005: Minimize lock contention

## Lock Types
- ASYNC-LOCK-001: Use Lock type (.NET 9+) over object locks
- ASYNC-LOCK-002: Apply SemaphoreSlim for async locks
- ASYNC-LOCK-003: Use ReaderWriterLockSlim for read-heavy scenarios
- ASYNC-LOCK-004: Minimize time in locks

## Dataflow
- ASYNC-DF-001: Use System.Threading.Tasks.Dataflow for pipelines
- ASYNC-DF-002: Apply blocks for different operations
- ASYNC-DF-003: Implement backpressure via bounded capacity
- ASYNC-DF-004: Use for complex async workflows

## AsyncLocal<T>
- ASYNC-LOCAL-001: Use for async context flow
- ASYNC-LOCAL-002: Apply for correlation IDs and trace context
- ASYNC-LOCAL-003: Flows across await boundaries
- ASYNC-LOCAL-004: Prefer over ThreadLocal<T> in async code

## Timer Operations
- ASYNC-TIMER-001: Use PeriodicTimer (.NET 6+) for recurring work
- ASYNC-TIMER-002: Apply TimeProvider for testable timers
- ASYNC-TIMER-003: Cancel timer operations properly
- ASYNC-TIMER-004: Avoid System.Timers.Timer (use PeriodicTimer)

## Forbidden Patterns
- ASYNC-FORBID-001: No .Result or .Wait() on Tasks
- ASYNC-FORBID-002: No async void (except event handlers)
- ASYNC-FORBID-003: No Task.Run() in libraries
- ASYNC-FORBID-004: No fire-and-forget without error handling
- ASYNC-FORBID-005: No missing CancellationToken
- ASYNC-FORBID-006: No unbounded parallel operations
- ASYNC-FORBID-007: No deadlocks via sync-over-async
- ASYNC-FORBID-008: No ConfigureAwait(true) in libraries
- ASYNC-FORBID-009: No async lambda in LINQ without awareness
- ASYNC-FORBID-010: No unobserved task exceptions
