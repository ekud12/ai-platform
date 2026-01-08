---
name: typescript-async
description: TypeScript async/concurrency patterns with AbortSignal, p-limit, Promise.allSettled, and structured concurrency. Zero tolerance for floating promises.
allowed-tools: Read, Write, Edit
---

# TypeScript Async & Concurrency Patterns (Rules Only)

## Purpose
Enforce disciplined async/await patterns, prevent floating promises, and ensure proper cancellation support in all asynchronous TypeScript code.

## Promise Handling

### Await Discipline
- TS-ASYNC-001: Await all promises - never let them float
- TS-ASYNC-002: No floating promises in any context
- TS-ASYNC-003: All async entry points must return typed outputs
- TS-ASYNC-004: No `Promise<void>` - return structured outputs or `Result<T, E>`
- TS-ASYNC-005: All async methods must accept `AbortSignal` parameter
- TS-ASYNC-006: Declare timeout/cancellation semantics for all async operations

### AbortSignal Support
- TS-ASYNC-007: Support `AbortSignal` with timeouts for every async entry point
- TS-ASYNC-008: Propagate `AbortSignal` through entire async call chain
- TS-ASYNC-009: Check `signal.aborted` before expensive operations
- TS-ASYNC-010: Throw `AbortError` when signal is aborted
- TS-ASYNC-011: Clean up resources when aborted (listeners, timers, connections)
- TS-ASYNC-012: Expose `.abort()` or cancellation method on long-lived tasks

### Timeout Management
- TS-ASYNC-013: Set timeouts for all long-running operations
- TS-ASYNC-014: Use `AbortSignal.timeout(ms)` for automatic timeout handling
- TS-ASYNC-015: Configure reasonable default timeouts (no infinite waits)
- TS-ASYNC-016: Log timeout events with operation context

## Concurrency Control

### Parallelism Tools
- TS-ASYNC-017: Use `p-limit` for bounded concurrency
- TS-ASYNC-018: Use `p-queue` for task queuing with priority
- TS-ASYNC-019: Use `Promise.allSettled` instead of `Promise.all` to handle partial failures
- TS-ASYNC-020: Use `Promise.race` with timeout for fallback behavior
- TS-ASYNC-021: Ban unbounded `Promise.all` - always limit concurrency

### Structured Concurrency
- TS-ASYNC-022: No shared top-level promises - wrap in resettable factories
- TS-ASYNC-023: All shared state must be wrapped in functions, not global promises
- TS-ASYNC-024: Preallocate promise arrays where size is known
- TS-ASYNC-025: Use structured concurrency patterns (spawn/join)
- TS-ASYNC-026: Ensure child tasks are canceled when parent is aborted

## Error Handling

### Async Error Patterns
- TS-ASYNC-027: Always handle promise rejections explicitly
- TS-ASYNC-028: Log all unhandled promise rejections
- TS-ASYNC-029: Use try/catch around all await statements in critical paths
- TS-ASYNC-030: Return `Result<T, E>` instead of throwing in async functions
- TS-ASYNC-031: Preserve error cause chain in async error handling
- TS-ASYNC-032: Tag async errors with trace context and correlation ID

## Iteration Patterns

### Async Loops
- TS-ASYNC-033: No `async forEach` - use `for await` or `Promise.all` instead
- TS-ASYNC-034: Use `for await...of` for async iterables
- TS-ASYNC-035: Use `Promise.all(array.map(async ...))` for parallel processing
- TS-ASYNC-036: Use sequential `for...of` with `await` for ordered processing
- TS-ASYNC-037: No array mutation during async iteration

### Async Generators
- TS-ASYNC-038: Implement `async function*` for streaming data
- TS-ASYNC-039: Use `yield` for backpressure control in async generators
- TS-ASYNC-040: Properly cleanup resources in async generator finally blocks
- TS-ASYNC-041: Support cancellation in async generators via `AbortSignal`

## Retry Logic

### Retry Patterns
- TS-ASYNC-042: Guard retry loops with backoff strategy
- TS-ASYNC-043: Implement exponential backoff with jitter
- TS-ASYNC-044: Set maximum retry limits (no infinite retries)
- TS-ASYNC-045: Support abort conditions in retry loops
- TS-ASYNC-046: Log each retry attempt with attempt number and delay
- TS-ASYNC-047: Return `Result<T, E>` with failure details after max retries

### Circuit Breaker
- TS-ASYNC-048: Implement circuit breaker for external service calls
- TS-ASYNC-049: Track failure rates and open circuit after threshold
- TS-ASYNC-050: Use half-open state for recovery testing
- TS-ASYNC-051: Log circuit breaker state changes

## Async Context

### Context Propagation
- TS-ASYNC-052: Use AsyncLocalStorage for request context propagation
- TS-ASYNC-053: Store correlation ID, user ID, trace ID in async context
- TS-ASYNC-054: Propagate context through Promise chains automatically
- TS-ASYNC-055: Propagate context across event emitters and callbacks
- TS-ASYNC-056: Clean up async context on request completion to prevent leaks

## Performance Optimization

### Async Performance
- TS-ASYNC-057: No `new Promise()` in perf-critical loops - use object pools
- TS-ASYNC-058: Preallocate promise arrays where size is known
- TS-ASYNC-059: Use `Promise.allSettled` instead of individual try/catch per promise
- TS-ASYNC-060: Avoid promise chaining in hot paths - use async/await
- TS-ASYNC-061: Cache promise results where appropriate (memoization)

### Microtask Management
- TS-ASYNC-062: Use `queueMicrotask` for deferred non-critical work
- TS-ASYNC-063: Use `requestIdleCallback` (browser) for UI update deferral
- TS-ASYNC-064: Batch microtask operations to reduce overhead

## Forbidden Patterns

### Async Anti-Patterns
- TS-ASYNC-065: Never mix sync/async without clear delineation
- TS-ASYNC-066: No hidden awaits in seemingly synchronous code
- TS-ASYNC-067: No async constructors
- TS-ASYNC-068: No async property getters
- TS-ASYNC-069: No `async` function without at least one `await`
- TS-ASYNC-070: No promise constructor anti-pattern (wrapping async function in Promise)
- TS-ASYNC-071: No promise race conditions from shared mutable state
- TS-ASYNC-072: No event listeners without cleanup in async functions

## Memory Management

### Resource Cleanup
- TS-ASYNC-073: Clean up event listeners in async finally blocks
- TS-ASYNC-074: Close connections and file handles in finally blocks
- TS-ASYNC-075: Cancel timers and intervals when async operation completes
- TS-ASYNC-076: Use AbortController to clean up all related operations
- TS-ASYNC-077: Implement proper disposal pattern for async resources

## Testing

### Async Testing
- TS-ASYNC-078: Always await async assertions in tests
- TS-ASYNC-079: Set test timeouts for all async tests
- TS-ASYNC-080: Test abort/cancellation paths explicitly
- TS-ASYNC-081: Test retry logic with mock failures
- TS-ASYNC-082: Test concurrent execution scenarios

## Activation Criteria
Use these patterns when:
- Implementing async/await operations
- Managing concurrent operations
- Building retry and circuit breaker logic
- Implementing cancellation and timeout support
