---
name: observability-typescript
description: TypeScript/Node.js observability patterns for structured logging (winston/pino), OpenTelemetry, and distributed tracing. No console.* in production, correlation IDs mandatory.
allowed-tools: Read, Write, Edit
---

# TypeScript Observability Patterns (Rules Only)

## Purpose
Ensure all TypeScript/Node.js systems are instrumented for production observability, debugging, and cost tracking using structured logging frameworks.

## Structured Logging (TypeScript)

### Logging Framework Usage
- OBS-TS-001: Use structured logging library (winston, pino, or bunyan) - never `console.*`
- OBS-TS-002: Ban all `console.log`, `console.error`, `console.warn` in production code
- OBS-TS-003: Log before every return statement (success and failure paths)
- OBS-TS-004: Use structured data with named properties, not string concatenation
- OBS-TS-005: Include correlation ID, request ID, and user ID in all log entries
- OBS-TS-006: Lazy evaluation for log parameters - no template construction unless needed
- OBS-TS-007: Use appropriate log levels (debug, info, warn, error, fatal)

### Configuration
- OBS-TS-008: Configure logging via environment-specific config files
- OBS-TS-009: Use JSON format for production logs (structured, parseable)
- OBS-TS-010: Configure different log levels per module/namespace
- OBS-TS-011: Set up log aggregation (Elasticsearch, Datadog, CloudWatch)
- OBS-TS-012: Configure retention policies based on compliance requirements

## Distributed Tracing (TypeScript)

### OpenTelemetry Integration
- OBS-TS-013: Use OpenTelemetry SDK for Node.js (@opentelemetry/sdk-node)
- OBS-TS-014: Configure automatic instrumentation for HTTP, Express, Fastify
- OBS-TS-015: Create custom spans for business-critical operations
- OBS-TS-016: Tag spans with operation-specific data (userId, orderId, etc.)
- OBS-TS-017: Propagate trace context across async boundaries (promises, callbacks)
- OBS-TS-018: Include TraceId and SpanId in all log entries for correlation
- OBS-TS-019: Configure OTLP exporters (Jaeger, Zipkin, or cloud providers)

### Correlation ID Management
- OBS-TS-020: Implement correlation ID middleware for all HTTP servers
- OBS-TS-021: Generate correlation ID at entry point if not provided
- OBS-TS-022: Propagate correlation ID through entire request lifecycle
- OBS-TS-023: Include correlation ID in all outbound HTTP requests
- OBS-TS-024: Log correlation ID in all log entries within request context
- OBS-TS-025: Use AsyncLocalStorage or continuation-local-storage for context propagation

## Metrics & Performance (TypeScript)

### Custom Metrics
- OBS-TS-026: Use OpenTelemetry metrics API for counters and histograms
- OBS-TS-027: Track request duration, error rates, and throughput
- OBS-TS-028: Create custom metrics for business KPIs beyond technical indicators
- OBS-TS-029: Monitor event loop lag and memory usage
- OBS-TS-030: Track database query execution times

### Performance Instrumentation
- OBS-TS-031: Instrument hot paths with timing measurements
- OBS-TS-032: Track garbage collection metrics and heap usage
- OBS-TS-033: Monitor Promise resolution times for async operations
- OBS-TS-034: Log external API call duration and status codes
- OBS-TS-035: Track token usage and cost for AI/LLM integrations

## HTTP Client Tracing (TypeScript)

### External API Calls
- OBS-TS-036: Log all external API calls with duration, status, and correlation ID
- OBS-TS-037: Include request and response sizes in metrics
- OBS-TS-038: Track retry attempts and circuit breaker state
- OBS-TS-039: Propagate trace context headers (W3C TraceContext standard)
- OBS-TS-040: Log request/response payloads at debug level (sanitize PII)
- OBS-TS-041: Set timeouts for all HTTP calls and log timeout events

## Error Handling (TypeScript)

### Error Logging
- OBS-TS-042: Log all errors with structured data (error type, message, stack trace)
- OBS-TS-043: Include error cause chain in logs (error.cause)
- OBS-TS-044: Tag errors with correlation ID and user context
- OBS-TS-045: Track error patterns and failure modes in metrics
- OBS-TS-046: Identify blame radius (one user, region, everything) in logs
- OBS-TS-047: Ensure postmortem support with sufficient log context
- OBS-TS-048: Never swallow errors silently - always log or propagate

### Error Boundaries (Frontend)
- OBS-TS-049: Implement error boundary logging for React/Vue applications
- OBS-TS-050: Log unhandled promise rejections with context
- OBS-TS-051: Track client-side errors separately from server errors
- OBS-TS-052: Send critical frontend errors to backend logging service

## Health Checks (TypeScript)

### Endpoint Implementation
- OBS-TS-053: Expose `/health/live` for liveness checks (basic app availability)
- OBS-TS-054: Expose `/health/ready` for readiness checks (dependency validation)
- OBS-TS-055: Check database, cache, queue, and external service connectivity
- OBS-TS-056: Configure health check timeouts to prevent cascading failures
- OBS-TS-057: Return proper HTTP status codes (200 healthy, 503 unhealthy, 429 degraded)
- OBS-TS-058: Include degradation detection (warn before failure)

## Startup & Configuration (TypeScript)

### Application Startup
- OBS-TS-059: Log deployed metadata on startup (commit SHA, version, timestamp)
- OBS-TS-060: Log Node.js version, environment, and region on startup
- OBS-TS-061: Validate required environment variables at startup and log results
- OBS-TS-062: Validate external dependencies at startup (database, cache, APIs)
- OBS-TS-063: Fail fast if critical dependencies are unavailable
- OBS-TS-064: Log configuration validation results (redact secrets)

## Debugging & Diagnostics (TypeScript)

### Telemetry Coverage
- OBS-TS-065: Ensure full request lifecycle visibility from entry to exit
- OBS-TS-066: Log all key decision points with identifiers and timestamps
- OBS-TS-067: Differentiate user error, infra error, and system bug in telemetry
- OBS-TS-068: Implement reliable retry or recovery mechanism logging
- OBS-TS-069: Support runtime performance profiling via Node.js profiler
- OBS-TS-070: Enable diagnostic channels for framework events

## Anti-Patterns (TypeScript)

### Forbidden Practices
- OBS-TS-071: Never use `console.*` in production code (console.log, console.error, etc.)
- OBS-TS-072: Never log only errors - log success paths too
- OBS-TS-073: Never log sensitive data (passwords, tokens, PII) without redaction
- OBS-TS-074: Never skip logging in critical paths
- OBS-TS-075: Never use string concatenation or template literals for log messages
- OBS-TS-076: Never ignore correlation IDs or trace context
- OBS-TS-077: Never over-log in hot paths causing performance degradation
- OBS-TS-078: Never skip health checks for critical dependencies
- OBS-TS-079: Never let unhandled promise rejections go unlogged
- OBS-TS-080: Never skip logging event listener registration/cleanup

## Privacy & Security (TypeScript)

### Data Protection
- OBS-TS-081: Redact PII from logs using custom formatters or scrubbers
- OBS-TS-082: Sanitize authentication tokens and API keys from logs
- OBS-TS-083: Sanitize connection strings and credentials from diagnostic output
- OBS-TS-084: Configure log retention based on data classification
- OBS-TS-085: Encrypt logs in transit and at rest for sensitive environments
- OBS-TS-086: Use `Object.create(null)` for log metadata to avoid prototype pollution

## Async Context Tracking (TypeScript)

### Context Propagation
- OBS-TS-087: Use AsyncLocalStorage (Node.js 14+) for request context
- OBS-TS-088: Store correlation ID, user ID, trace ID in async context
- OBS-TS-089: Propagate context through Promise chains automatically
- OBS-TS-090: Propagate context across event emitters and callbacks
- OBS-TS-091: Use context for automatic correlation in all logs
- OBS-TS-092: Clean up async context on request completion to prevent leaks

## Cost Tracking (AI Integrations - TypeScript)

### LLM Cost Management
- OBS-TS-093: Log token counts for all prompt phases (input, output, total)
- OBS-TS-094: Track cost per operation, user, or feature
- OBS-TS-095: Implement spending limits and budget alerts
- OBS-TS-096: Log temperature, max_tokens, and model version with results
- OBS-TS-097: Include retry costs in total cost calculations
- OBS-TS-098: Trace prompt template file paths for debugging
