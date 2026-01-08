---
name: dotnet-distributed
description: Distributed systems patterns including circuit breakers, retry policies, idempotency, outbox pattern, and resilience.
allowed-tools: Read, Write, Edit
---

# Distributed Systems Patterns (Rules Only)

## Circuit Breakers
- DIST-CB-001: Use Polly for all external service calls
- DIST-CB-002: Apply circuit breaker pattern mandatory
- DIST-CB-003: Configure thresholds based on SLOs
- DIST-CB-004: Implement fallback strategies
- DIST-CB-005: Monitor circuit state

## Retry Policies
- DIST-RETRY-001: Apply exponential backoff with jitter
- DIST-RETRY-002: Limit retry attempts (3-5 typical)
- DIST-RETRY-003: Use Polly retry policies
- DIST-RETRY-004: Include idempotency checks
- DIST-RETRY-005: Never retry non-idempotent operations without safeguards

## Bulkhead Isolation
- DIST-BULK-001: Separate thread pools for different concerns
- DIST-BULK-002: Prevent cascading failures
- DIST-BULK-003: Limit concurrent operations
- DIST-BULK-004: Apply resource quotas

## Timeout Policies
- DIST-TIMEOUT-001: Set explicit timeouts on all I/O operations
- DIST-TIMEOUT-002: Use CancellationToken propagation
- DIST-TIMEOUT-003: Apply timeout policies with Polly
- DIST-TIMEOUT-004: Fail fast on timeouts

## Idempotency
- DIST-IDEMP-001: Design all operations as idempotent
- DIST-IDEMP-002: Use correlation IDs for deduplication
- DIST-IDEMP-003: Implement idempotency keys
- DIST-IDEMP-004: Store operation results for replay

## Outbox Pattern
- DIST-OUTBOX-001: Use for reliable message publishing
- DIST-OUTBOX-002: Implement within Unit of Work
- DIST-OUTBOX-003: Process outbox in background
- DIST-OUTBOX-004: Ensure at-least-once delivery

## Distributed Locks
- DIST-LOCK-001: Use Redis or Postgres advisory locks
- DIST-LOCK-002: Apply for cross-node coordination
- DIST-LOCK-003: Set lock timeouts mandatory
- DIST-LOCK-004: Implement lock renewal for long operations

## Correlation IDs
- DIST-CORR-001: Propagate across all service boundaries
- DIST-CORR-002: Use for distributed tracing
- DIST-CORR-003: Include in all log entries
- DIST-CORR-004: Generate at entry point

## Saga Pattern
- DIST-SAGA-001: Use for distributed transactions
- DIST-SAGA-002: Implement compensation logic
- DIST-SAGA-003: Track saga state persistently
- DIST-SAGA-004: Handle partial failures explicitly

## Event Sourcing
- DIST-ES-001: Store all state changes as events
- DIST-ES-002: Implement event store properly
- DIST-ES-003: Support replay for recovery
- DIST-ES-004: Version events for evolution

## CQRS
- DIST-CQRS-001: Separate read and write models
- DIST-CQRS-002: Optimize reads independently
- DIST-CQRS-003: Use eventual consistency where appropriate
- DIST-CQRS-004: Apply for complex domains

## Service Discovery
- DIST-SD-001: Use for dynamic service location
- DIST-SD-002: Implement health checks
- DIST-SD-003: Support multiple instances
- DIST-SD-004: Handle service failures gracefully

## Load Balancing
- DIST-LB-001: Apply client-side load balancing where possible
- DIST-LB-002: Use health-aware routing
- DIST-LB-003: Implement retry across instances

## Forbidden Patterns
- DIST-FORBID-001: No distributed transactions without compensation
- DIST-FORBID-002: No missing idempotency on retries
- DIST-FORBID-003: No unbounded retries
- DIST-FORBID-004: No missing correlation IDs
- DIST-FORBID-005: No synchronous coupling where async possible
- DIST-FORBID-006: No missing circuit breakers on external calls
