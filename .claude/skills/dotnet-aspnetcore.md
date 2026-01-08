---
name: dotnet-aspnetcore
description: ASP.NET Core patterns including ProblemDetails, minimal APIs, WebAuthN, endpoint filters, and OpenAPI compliance.
allowed-tools: Read, Write, Edit
---

# ASP.NET Core Compliance (Rules Only)

## ProblemDetails (Mandatory)
- ASP-PROB-001: Inject and use IProblemDetailsService for all error responses
- ASP-PROB-002: RFC 9457 compliance mandatory
- ASP-PROB-003: Use ProblemDetailsContext for structured errors
- ASP-PROB-004: Include TraceId in all problem responses
- ASP-PROB-005: Never return raw exceptions to clients

## Global Exception Handling
- ASP-EXC-001: Implement IExceptionHandler for all unhandled exceptions
- ASP-EXC-002: Register with AddExceptionHandler<T>()
- ASP-EXC-003: Return application/problem+json for all errors
- ASP-EXC-004: Log with structured data before responding
- ASP-EXC-005: Mandatory for all applications

## Status Code Pages
- ASP-STATUS-001: Use UseStatusCodePages() for 4xx/5xx
- ASP-STATUS-002: Emit ProblemDetails for all status codes
- ASP-STATUS-003: Set SuppressMapClientErrors = false
- ASP-STATUS-004: Own every failure shape explicitly

## Validation
- ASP-VAL-001: Use FluentValidation for domain validation
- ASP-VAL-002: Translate to ValidationProblemDetails
- ASP-VAL-003: Never return BadRequest() directly
- ASP-VAL-004: Validate at endpoint entry point
- ASP-VAL-005: Use endpoint filters for cross-cutting validation

## Minimal APIs
- ASP-MIN-001: Cluster endpoints with MapGroup()
- ASP-MIN-002: Use endpoint filters for middleware-like logic
- ASP-MIN-003: Return Results<T> for type safety
- ASP-MIN-004: Apply [Tags], [ProducesResponseType], [EndpointSummary]
- ASP-MIN-005: No string-based route templates where typed possible

## WebAuthN and Passkeys (.NET 10)
- ASP-AUTH-001: Use built-in WebAuthN support for authentication
- ASP-AUTH-002: Implement passkey flows for passwordless auth
- ASP-AUTH-003: Store credentials securely
- ASP-AUTH-004: Validate authenticator assertions
- ASP-AUTH-005: Mandatory for new authentication systems

## OpenAPI
- ASP-API-001: Generate OpenAPI 3.1 specification
- ASP-API-002: Use XML comments for documentation
- ASP-API-003: Apply metadata attributes for rich docs
- ASP-API-004: Support YAML format output
- ASP-API-005: Include example values in schemas
- ASP-API-006: Version API endpoints explicitly

## Health Checks
- ASP-HEALTH-001: Implement IHealthCheck for all dependencies
- ASP-HEALTH-002: Return ProblemDetails for degraded/unhealthy states
- ASP-HEALTH-003: Include dependency status details
- ASP-HEALTH-004: Use liveness and readiness probes
- ASP-HEALTH-005: Mandatory for containerized applications

## Error Logging
- ASP-LOG-001: Log all 5xx errors with ILogger.BeginScope()
- ASP-LOG-002: Include TraceId, ExceptionType, caller context
- ASP-LOG-003: Use structured logging exclusively
- ASP-LOG-004: No string interpolation in log messages
- ASP-LOG-005: Log before returning error response

## Error Response Caching
- ASP-CACHE-001: Add Cache-Control: no-store to all errors
- ASP-CACHE-002: Prevent client/proxy caching of failures
- ASP-CACHE-003: Set appropriate headers in ProblemDetails responses

## Rate Limiting
- ASP-RATE-001: Apply per-endpoint or global rate limits
- ASP-RATE-002: Use named policies for tiering
- ASP-RATE-003: Return 429 Too Many Requests with Retry-After
- ASP-RATE-004: Include rate limit headers in responses

## CORS
- ASP-CORS-001: Configure CORS explicitly
- ASP-CORS-002: No AllowAnyOrigin in production
- ASP-CORS-003: Use named policies
- ASP-CORS-004: Validate origins against whitelist

## Request Validation
- ASP-REQ-001: Validate content-type headers
- ASP-REQ-002: Enforce request size limits
- ASP-REQ-003: Use antiforgery tokens for state-changing operations
- ASP-REQ-004: Apply HTTPS redirection mandatory

## Response Compression
- ASP-COMP-001: Enable response compression for APIs
- ASP-COMP-002: Use Brotli over GZip when supported
- ASP-COMP-003: Configure MIME types appropriately

## Forbidden Patterns
- ASP-FORBID-001: No Controller-based APIs for new projects (use minimal APIs)
- ASP-FORBID-002: No raw exception returns to clients
- ASP-FORBID-003: No missing TraceId in error responses
- ASP-FORBID-004: No hardcoded connection strings
- ASP-FORBID-005: No missing health checks
- ASP-FORBID-006: No AllowAnonymous without explicit reasoning
- ASP-FORBID-007: No missing rate limiting on public endpoints
