# C# Observability Rules

## Purpose

This rulebook defines standards for logging, tracing, and metrics in C#. Observability enables understanding system behavior in production.

## Authority

These rules govern all observability instrumentation in .NET applications.

## Scope

Applies to logging, distributed tracing, metrics, and health monitoring.

## Constraints

- Observability must not impact performance significantly
- Sensitive data must not be logged
- Correlation must be maintained across services

## Rule Format

All rules use the CS-OBS prefix.

---

## CS-OBS-001 — Structured Logging

**Rule**
All logging must use structured logging with named parameters.

**Rationale**
Structured logs enable searching, filtering, and aggregation. They are machine-parseable and human-readable.

**Enforcement**
Code review must verify structured format. String interpolation in log messages must be rejected. Log templates must have named placeholders.

---

## CS-OBS-002 — Log Levels

**Rule**
Log levels must be used consistently: Debug for development, Information for flow, Warning for recoverable issues, Error for failures.

**Rationale**
Consistent levels enable filtering and alerting. Misused levels create noise or miss important events.

**Enforcement**
Code review must verify level appropriateness. Errors must not be logged as Information. Debug logs must not appear in production.

---

## CS-OBS-003 — Correlation IDs

**Rule**
All operations must have correlation IDs that propagate across service boundaries.

**Rationale**
Correlation enables tracing requests through distributed systems. Without correlation, debugging distributed issues is impractical.

**Enforcement**
Middleware must extract or generate correlation IDs. HTTP clients must propagate correlation headers. Logs must include correlation ID.

---

## CS-OBS-004 — OpenTelemetry Tracing

**Rule**
Services must implement distributed tracing using OpenTelemetry.

**Rationale**
OpenTelemetry is the standard for observability. It enables vendor-neutral tracing across services.

**Enforcement**
Services must configure OTLP exporters. Spans must be created for significant operations. Trace context must propagate correctly.

---

## CS-OBS-005 — Span Attributes

**Rule**
Trace spans must include relevant attributes for debugging: operation type, entity IDs, result status.

**Rationale**
Rich span attributes enable filtering and analysis. They provide context for understanding trace behavior.

**Enforcement**
Code review must verify span attributes. Key operations must have descriptive spans. Sensitive data must not be included.

---

## CS-OBS-006 — Metrics Instrumentation

**Rule**
Key operations must have metrics: counters for events, histograms for durations, gauges for state.

**Rationale**
Metrics enable alerting, capacity planning, and performance analysis. They provide quantitative system understanding.

**Enforcement**
Services must expose metrics endpoints. SLI-related operations must have metrics. Dashboards must use defined metrics.

---

## CS-OBS-007 — Exception Logging

**Rule**
Exceptions must be logged with full stack trace at Error level. Caught exceptions must be logged at Warning.

**Rationale**
Complete exception information is essential for debugging. The level indicates whether the exception was handled.

**Enforcement**
Code review must verify exception logging. Swallowed exceptions must log at minimum. Stack traces must be preserved.

---

## CS-OBS-008 — Performance Logging

**Rule**
Operations exceeding performance thresholds must be logged with timing information.

**Rationale**
Performance anomalies must be detectable from logs. Threshold-based logging highlights issues without overwhelming logs.

**Enforcement**
Slow operations must be logged with duration. Thresholds must be configurable. Performance logs must include context.

---

## CS-OBS-009 — Health Check Details

**Rule**
Health checks must report detailed status for each dependency.

**Rationale**
Aggregated health status is insufficient for debugging. Detailed checks identify the specific failing component.

**Enforcement**
Each dependency must have its health check. Health response must include individual statuses. Degraded states must be distinguishable.

---

## CS-OBS-010 — Log Context

**Rule**
Logs must include request context: user ID (if authenticated), request path, operation name.

**Rationale**
Context enables filtering logs by user or operation. It provides the information needed to reproduce issues.

**Enforcement**
Logging scope must be configured with context. Middleware must enrich log context. Sensitive user data must not be included.

---

## CS-OBS-011 — Baggage Propagation

**Rule**
OpenTelemetry Baggage MUST be used for cross-service context (tenant ID, feature flags).

**Rationale**
Baggage propagates context across service boundaries automatically. It enables consistent behavior in distributed systems.

**Enforcement**
Baggage must be set at entry points. Downstream services must read baggage. Sensitive data must not be in baggage.

---

## CS-OBS-012 — Metric Naming Convention

**Rule**
Metrics MUST follow naming convention: `{service}.{subsystem}.{metric}` with units.

**Rationale**
Consistent naming enables dashboard templates and alerting rules. Units in names prevent interpretation errors.

**Enforcement**
Metric names must follow pattern. Units must be included (e.g., `_seconds`, `_bytes`). Code review must verify conventions.

---

## CS-OBS-013 — HTTP Handler Correlation

**Rule**
All outgoing HTTP requests MUST include correlation headers via DelegatingHandler.

**Rationale**
Correlation headers enable distributed tracing across service boundaries.

**Enforcement**
HTTP clients must register RequestCorrelationHandler. Code review must verify handler registration.

**Good Pattern**
```csharp
public class RequestCorrelationHandler : DelegatingHandler
{
    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request,
        CancellationToken ct)
    {
        var activity = Activity.Current;
        if (activity != null)
        {
            request.Headers.TryAddWithoutValidation("X-Correlation-Id", activity.TraceId.ToString());
            request.Headers.TryAddWithoutValidation("X-Span-Id", activity.SpanId.ToString());
        }
        return await base.SendAsync(request, ct);
    }
}

// Registration
services.AddTransient<RequestCorrelationHandler>();
services.AddHttpClient<IMyClient, MyClient>()
    .AddHttpMessageHandler<RequestCorrelationHandler>();
```

---

## CS-OBS-014 — HTTP Request/Response Logging

**Rule**
HTTP clients SHOULD log requests and responses via a logging handler for debugging.

**Rationale**
HTTP logging aids debugging integration issues without requiring external tools.

**Enforcement**
HTTP clients should register HttpLoggingHandler. Log level should be configurable.

**Good Pattern**
```csharp
public class HttpLoggingHandler(ILogger<HttpLoggingHandler> logger) : DelegatingHandler
{
    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request,
        CancellationToken ct)
    {
        logger.LogDebug("HTTP {Method} {Uri}",
            request.Method, request.RequestUri);

        var stopwatch = Stopwatch.StartNew();
        var response = await base.SendAsync(request, ct);
        stopwatch.Stop();

        logger.LogDebug("HTTP {StatusCode} {Uri} ({ElapsedMs}ms)",
            (int)response.StatusCode, request.RequestUri, stopwatch.ElapsedMilliseconds);

        return response;
    }
}
```

---

## CS-OBS-015 — Liveness Health Check Per Service

**Rule**
Each service MUST have a dedicated liveness health check class.

**Rationale**
Liveness checks enable Kubernetes to detect hung processes. Each service should verify its critical dependencies.

**Enforcement**
Services must implement IHealthCheck. Health endpoints must be exposed at /health.

**Good Pattern**
```csharp
// HealthChecks/LivenessCheck.cs
public class LivenessCheck : IHealthCheck
{
    public Task<HealthCheckResult> CheckHealthAsync(
        HealthCheckContext context,
        CancellationToken ct = default)
    {
        // Add actual liveness verification logic
        return Task.FromResult(HealthCheckResult.Healthy("Service is alive"));
    }
}

// Registration
services.AddHealthChecks()
    .AddCheck<LivenessCheck>("liveness", tags: ["live"])
    .AddSqlServer(connectionString, tags: ["ready"])
    .AddRedis(redisConnection, tags: ["ready"]);

// Endpoints
app.MapHealthChecks("/health/live", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("live")
});

app.MapHealthChecks("/health/ready", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("ready")
});
```
