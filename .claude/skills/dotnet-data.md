---
name: dotnet-data
description: Data access patterns with EF Core, pagination, query optimization, Unit of Work, and repository patterns.
allowed-tools: Read, Write, Edit
---

# Data Access Patterns (Rules Only)

## EF Core Best Practices
- DATA-EF-001: Use EF Core 10 compiled models
- DATA-EF-002: Apply bulk operations for batch changes
- DATA-EF-003: Set explicit query timeouts
- DATA-EF-004: Use AsNoTracking() for read-only queries
- DATA-EF-005: Split context for read/write if beneficial

## Query Optimization
- DATA-QUERY-001: Detect and eliminate N+1 queries
- DATA-QUERY-002: Use projection (Select) to fetch only needed columns
- DATA-QUERY-003: Apply Include() judiciously, never unbounded
- DATA-QUERY-004: Implement query filters for soft deletes
- DATA-QUERY-005: Use compiled queries for repeated patterns

## Pagination
- DATA-PAGE-001: Implement continuation token pagination
- DATA-PAGE-002: Use keyset/cursor pagination for large datasets
- DATA-PAGE-003: Apply default page size (25-50 items)
- DATA-PAGE-004: Never use offset pagination for large tables
- DATA-PAGE-005: Return total count separately if needed

## Indexes
- DATA-IDX-001: Create indexes based on query patterns
- DATA-IDX-002: Include columns in index for covering
- DATA-IDX-003: Avoid over-indexing
- DATA-IDX-004: Monitor index usage and remove unused
- DATA-IDX-005: Use filtered indexes where appropriate

## Transactions
- DATA-TX-001: Keep transactions short
- DATA-TX-002: Use Unit of Work for boundary management
- DATA-TX-003: Apply optimistic concurrency where possible
- DATA-TX-004: Implement retry logic for transient failures
- DATA-TX-005: Never nest transactions

## Unit of Work Pattern
- DATA-UOW-001: Register as scoped service
- DATA-UOW-002: Manage transaction boundaries explicitly
- DATA-UOW-003: Implement SaveChanges separately from Commit
- DATA-UOW-004: Integrate outbox pattern for events
- DATA-UOW-005: Apply validation before persisting

## Repository Pattern
- DATA-REPO-001: Use for complex query encapsulation
- DATA-REPO-002: Keep generic where beneficial
- DATA-REPO-003: Avoid leaking EF Core abstractions
- DATA-REPO-004: Implement specification pattern for complex queries
- DATA-REPO-005: Return domain entities, not EF models

## Connection Management
- DATA-CONN-001: Use connection pooling (default)
- DATA-CONN-002: Configure max pool size based on load
- DATA-CONN-003: Monitor connection pool exhaustion
- DATA-CONN-004: Set connection timeouts
- DATA-CONN-005: Use connection resiliency for cloud databases

## Migrations
- DATA-MIG-001: Generate migrations for all schema changes
- DATA-MIG-002: Review generated SQL before applying
- DATA-MIG-003: Use idempotent migration scripts
- DATA-MIG-004: Test migrations on copy of production
- DATA-MIG-005: Plan for rollback scenarios

## Data Seeding
- DATA-SEED-001: Use ModelBuilder for reference data
- DATA-SEED-002: Keep seed data in migrations
- DATA-SEED-003: Make seeding idempotent
- DATA-SEED-004: Version seed data with schema

## Concurrency Control
- DATA-CONC-001: Use row version/timestamp for optimistic concurrency
- DATA-CONC-002: Handle DbUpdateConcurrencyException appropriately
- DATA-CONC-003: Implement last-write-wins or merge strategies
- DATA-CONC-004: Validate concurrency tokens

## Soft Deletes
- DATA-SOFT-001: Implement via query filters
- DATA-SOFT-002: Never hard delete without explicit reason
- DATA-SOFT-003: Include IsDeleted in indexes
- DATA-SOFT-004: Apply DeletedAt timestamp

## Auditing
- DATA-AUDIT-001: Track CreatedAt, CreatedBy, ModifiedAt, ModifiedBy
- DATA-AUDIT-002: Use interceptors for automatic auditing
- DATA-AUDIT-003: Store audit trail separately if detailed
- DATA-AUDIT-004: Include correlation IDs in audit logs

## Performance
- DATA-PERF-001: Avoid Select N+1 queries
- DATA-PERF-002: Use compiled queries for hot paths
- DATA-PERF-003: Apply database-generated values where possible
- DATA-PERF-004: Batch operations when feasible
- DATA-PERF-005: Monitor query performance

## Forbidden Patterns
- DATA-FORBID-001: No .ToList() on unfiltered queries
- DATA-FORBID-002: No Include() without limits
- DATA-FORBID-003: No missing indexes on foreign keys
- DATA-FORBID-004: No long-running transactions
- DATA-FORBID-005: No DbContext as singleton
- DATA-FORBID-006: No raw SQL without parameterization
- DATA-FORBID-007: No missing pagination on collections
- DATA-FORBID-008: No offset pagination for large tables
