---
name: observability-dotnet
description: .NET observability patterns for ILogger, OpenTelemetry, System.Diagnostics.Metrics, and Application Insights. Structured logging, distributed tracing, and health checks for production .NET systems.
allowed-tools: Read, Write, Edit
---

# .NET Observability Patterns (Rules Only)

## Purpose
Ensure all .NET systems are instrumented for production observability, debugging, and cost tracking using .NET-specific tooling.

## Structured Logging (.NET)

### ILogger<T> Usage
- OBS-NET-001: Use `ILogger<T>` with dependency injection consistently
- OBS-NET-002: Use `nameof(Method)` pattern for operation names
- OBS-NET-003: Log before every return statement (success and failure)
- OBS-NET-004: Use `ILogger.BeginScope()` to tag logs with logical operation scopes or correlation tags
- OBS-NET-005: Use structured logging with named parameters, not string interpolation
- OBS-NET-006: Use `[LoggerMessage]` attribute for high-frequency logging to eliminate boxing/parsing overhead
- OBS-NET-007: Lazy evaluation for all log parameters - no template construction on cold paths
- OBS-NET-008: Include TraceId in all log entries for correlation

### Configuration
- OBS-NET-009: Configure logging via `appsettings.json` with environment overrides
- OBS-NET-010: Use appropriate log levels: Debug, Info, Warning, Error, Critical
- OBS-NET-011: Configure different log levels per namespace/component
- OBS-NET-012: Set up log aggregation (seq, Elasticsearch, Application Insights)
- OBS-NET-013: Configure retention policies based on compliance requirements

## Distributed Tracing (.NET)

### OpenTelemetry Integration
- OBS-NET-014: Configure OpenTelemetry via `AddOpenTelemetry()` in `Program.cs`
- OBS-NET-015: Use `ActivitySource` for custom spans and traces
- OBS-NET-016: Tag activities with operation-specific data (userId, orderId, etc.)
- OBS-NET-017: Propagate `Activity.Current` properly across async boundaries
- OBS-NET-018: Include TraceId, SpanId, and Baggage in all log entries
- OBS-NET-019: Configure OTLP exporters (console, Jaeger, Application Insights)
- OBS-NET-020: Use `System.Diagnostics.SourceLink` for source mapping

### HttpClient Tracing
- OBS-NET-021: Enable automatic HttpClient tracing via System.Diagnostics
- OBS-NET-022: Log latency, status codes, and correlation IDs for all HTTP calls
- OBS-NET-023: Track retry attempts and circuit breaker state in traces
- OBS-NET-024: Propagate trace context headers (W3C TraceContext standard)

## Metrics & Performance (.NET)

### System.Diagnostics.Metrics
- OBS-NET-025: Use `Counter` for incrementing values (requests, errors)
- OBS-NET-026: Use `Histogram` for latency and duration measurements
- OBS-NET-027: Use `ObservableGauge` for point-in-time measurements (queue depth, memory)
- OBS-NET-028: Create custom metrics for business KPIs beyond technical indicators
- OBS-NET-029: Use `EventCounters` for runtime performance signals
- OBS-NET-030: Track connection pooling metrics for HTTP and database clients

### Performance Instrumentation
- OBS-NET-031: Instrument hot paths with Histogram for percentile tracking
- OBS-NET-032: Track GC metrics and allocation rates
- OBS-NET-033: Monitor thread pool utilization and queue lengths
- OBS-NET-034: Track database query execution times and connection pool metrics
- OBS-NET-035: Log token usage and cost for AI/LLM integrations

## Health Checks (.NET)

### IHealthCheck Implementation
- OBS-NET-036: Implement `IHealthCheck` interface for all critical dependencies
- OBS-NET-037: Return degraded/unhealthy status via ProblemDetails format
- OBS-NET-038: Expose `/health/live` for liveness probes (basic app availability)
- OBS-NET-039: Expose `/health/ready` for readiness probes (dependency checks)
- OBS-NET-040: Monitor database, cache, queue, and external service health
- OBS-NET-041: Configure health check timeouts to prevent cascading failures
- OBS-NET-042: Include degradation detection (warn before failure)

## Error Handling (.NET)

### IExceptionHandler
- OBS-NET-043: Implement custom `IExceptionHandler` for global error handling
- OBS-NET-044: Log all 5xx errors with structured logging (TraceId, ExceptionType, caller context)
- OBS-NET-045: Include exception cause chain (InnerException) in logs
- OBS-NET-046: Return ProblemDetails with TraceId for all errors
- OBS-NET-047: Track error patterns and failure modes in metrics
- OBS-NET-048: Identify blame radius (one user, region, everything) in logs
- OBS-NET-049: Ensure postmortem support with sufficient log context

## Startup & Configuration (.NET)

### Application Startup
- OBS-NET-050: Log deployed metadata on startup (commit SHA, version, timestamp)
- OBS-NET-051: Log environment, tier, and region on startup
- OBS-NET-052: Validate required configuration at startup and log results
- OBS-NET-053: Validate external dependencies at startup (database, cache, APIs)
- OBS-NET-054: Fail fast if critical dependencies are unavailable
- OBS-NET-055: Log configuration validation results (redact secrets)

## Application Insights (.NET)

### APM Integration
- OBS-NET-056: Configure Application Insights via `AddApplicationInsightsTelemetry()`
- OBS-NET-057: Use TelemetryClient for custom events and metrics
- OBS-NET-058: Track dependencies automatically (SQL, HTTP, Redis)
- OBS-NET-059: Configure sampling for high-volume applications
- OBS-NET-060: Set up custom dimensions for user context, tenant, region
- OBS-NET-061: Create custom availability tests for critical endpoints

## Debugging & Diagnostics (.NET)

### Telemetry Coverage
- OBS-NET-062: Ensure full request lifecycle visibility from entry to exit
- OBS-NET-063: Log all key decision points with identifiers and timestamps
- OBS-NET-064: Differentiate user error, infra error, and system bug in telemetry
- OBS-NET-065: Implement reliable retry or recovery mechanism logging
- OBS-NET-066: Support runtime performance profiling via dotnet-trace
- OBS-NET-067: Enable diagnostic listeners for framework events

## Anti-Patterns (.NET)

### Forbidden Practices
- OBS-NET-068: Never log only errors - log success paths too
- OBS-NET-069: Never use `Console.WriteLine` in production code
- OBS-NET-070: Never log sensitive data (passwords, tokens, PII) without redaction
- OBS-NET-071: Never skip logging in critical paths
- OBS-NET-072: Never use string interpolation in log messages (use structured params)
- OBS-NET-073: Never ignore correlation IDs or trace context
- OBS-NET-074: Never over-log in hot paths causing performance degradation
- OBS-NET-075: Never skip health checks for critical dependencies

## Privacy & Security (.NET)

### Data Protection
- OBS-NET-076: Redact PII from logs using custom formatters or scrubbers
- OBS-NET-077: Use `[LogProperties(SkipNulls = true)]` to avoid logging empty secrets
- OBS-NET-078: Sanitize connection strings and credentials from diagnostic output
- OBS-NET-079: Configure log retention based on data classification
- OBS-NET-080: Encrypt logs in transit and at rest for sensitive environments
