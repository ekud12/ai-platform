---
name: dotnet-10-platform
description: .NET 10 platform features including runtime enhancements, post-quantum cryptography, WebAuthN support, and ML-DSA. Enforce latest platform capabilities.
allowed-tools: Read, Write, Edit
---

# .NET 10 Platform Features (Rules Only)

## Runtime Enhancements (NEW in .NET 10)
- NET-RT-001: JIT compiler optimizations automatically applied
- NET-RT-002: Hardware acceleration paths (AVX10.2, Arm64 SVE) used where available
- NET-RT-003: No manual optimization needed for supported hardware
- NET-RT-004: Profile-guided optimization (PGO) enabled by default
- NET-RT-005: Tiered compilation improvements reduce startup time

## NativeAOT Improvements (.NET 10)
- NET-AOT-001: Reduced binary size automatically
- NET-AOT-002: Faster startup time with ahead-of-time compilation
- NET-AOT-003: Design all libraries for NativeAOT compatibility
- NET-AOT-004: Avoid reflection where possible
- NET-AOT-005: Use source generators for serialization
- NET-AOT-006: Apply trimming annotations where needed
- NET-AOT-007: Test both JIT and AOT builds

## Post-Quantum Cryptography (NEW in .NET 10)
- NET-PQC-001: Windows CNG support for quantum-resistant algorithms
- NET-PQC-002: ML-DSA (Module-Lattice-Based Digital Signature Algorithm) support
- NET-PQC-003: HashML-DSA with simplified APIs
- NET-PQC-004: Use post-quantum algorithms for forward security
- NET-PQC-005: Apply in high-security scenarios
- NET-PQC-006: Mandatory for long-term data protection

## WebAuthN and Passkey Support (NEW in .NET 10)
- NET-AUTH-001: Built-in WebAuthN support in ASP.NET Core
- NET-AUTH-002: Passkey authentication without third-party libraries
- NET-AUTH-003: Use for modern authentication flows
- NET-AUTH-004: Replace password-based auth where possible
- NET-AUTH-005: Mandatory for new authentication implementations

## Networking Enhancements (.NET 10)
- NET-NET-001: WebSocketStream for simplified WebSocket usage
- NET-NET-002: TLS 1.3 support on macOS clients
- NET-NET-003: Use WebSocketStream over legacy WebSocket APIs
- NET-NET-004: Mandatory TLS 1.3 for all new connections where supported
- NET-NET-005: HTTP/3 improvements and stabilization

## TimeProvider API (.NET 8 - Still Mandatory)
- NET-TIME-001: Inject TimeProvider for all time operations
- NET-TIME-002: Replace DateTime.UtcNow with TimeProvider.GetUtcNow()
- NET-TIME-003: Mandatory for testability
- NET-TIME-004: Apply in all time-sensitive logic
- NET-TIME-005: Use for scheduling, expiry, timestamps

## System.Text.Json Enhancements
- NET-JSON-001: Source-generated serialization mandatory
- NET-JSON-002: Use JsonSerializerContext for AOT compatibility
- NET-JSON-003: Required member support with `[JsonRequired]`
- NET-JSON-004: Polymorphic serialization with `[JsonPolymorphic]`
- NET-JSON-005: Span-based parsing for performance
- NET-JSON-006: Never use Newtonsoft.Json in new projects

## IExceptionHandler (.NET 8 - Still Mandatory)
- NET-EXC-001: Global exception handling via IExceptionHandler
- NET-EXC-002: Register with AddExceptionHandler<T>()
- NET-EXC-003: Return ProblemDetails for all errors
- NET-EXC-004: Structured logging with exception context
- NET-EXC-005: Mandatory for all ASP.NET Core applications

## RateLimiter Middleware (.NET 7 - Still Mandatory)
- NET-RATE-001: Built-in rate limiting with AddRateLimiter()
- NET-RATE-002: Token bucket, fixed window, sliding window algorithms
- NET-RATE-003: Apply per-endpoint or globally
- NET-RATE-004: Mandatory for all public APIs
- NET-RATE-005: Use named policies for different tiers

## Minimal API Validation (.NET 10)
- NET-VAL-001: Built-in validation support for minimal APIs
- NET-VAL-002: Automatic ProblemDetails for validation failures
- NET-VAL-003: Use with FluentValidation or Data Annotations
- NET-VAL-004: Apply endpoint filters for validation
- NET-VAL-005: Mandatory for all minimal API endpoints

## OpenAPI 3.1 and YAML Support (NEW in .NET 10)
- NET-API-001: OpenAPI 3.1 specification support
- NET-API-002: YAML format support for OpenAPI documents
- NET-API-003: Use for API documentation
- NET-API-004: Apply metadata attributes for rich documentation
- NET-API-005: Generate client SDKs from OpenAPI specs

## Channels and Pipelines
- NET-CHAN-001: System.Threading.Channels for producer-consumer
- NET-CHAN-002: System.IO.Pipelines for efficient I/O
- NET-CHAN-003: Use for high-throughput scenarios
- NET-CHAN-004: Apply backpressure patterns
- NET-CHAN-005: Mandatory over Queue<T> for async flows

## Metrics and Diagnostics
- NET-DIAG-001: System.Diagnostics.Metrics for instrumentation
- NET-DIAG-002: Use Meter, Counter, Histogram, ObservableGauge
- NET-DIAG-003: OpenTelemetry integration for distributed tracing
- NET-DIAG-004: ActivitySource for custom spans
- NET-DIAG-005: Mandatory instrumentation for all services

## Memory Management
- NET-MEM-001: ArrayPool<T> for temporary buffers
- NET-MEM-002: MemoryPool<T> for custom pooling
- NET-MEM-003: Memory<T> and ReadOnlyMemory<T> for slices
- NET-MEM-004: Span<T> for stack-allocated buffers
- NET-MEM-005: RecyclableMemoryStream for large buffers
- NET-MEM-006: Mandatory in performance-critical paths

## Frozen Collections (.NET 8 - Still Mandatory)
- NET-FROZEN-001: FrozenDictionary<TKey, TValue> for read-only lookups
- NET-FROZEN-002: FrozenSet<T> for read-only sets
- NET-FROZEN-003: Optimal lookup performance
- NET-FROZEN-004: Use for configuration, mappings, constants
- NET-FROZEN-005: Mandatory replacement for readonly dictionaries/sets

## SearchValues (.NET 8 - Still Mandatory)
- NET-SEARCH-001: SearchValues<T> for multi-value searches
- NET-SEARCH-002: Vectorized search operations
- NET-SEARCH-003: Use with IndexOfAny for performance
- NET-SEARCH-004: Apply in parsing and validation scenarios

## Generic Math (.NET 7 - Still Mandatory)
- NET-GMATH-001: INumber<T> and related interfaces
- NET-GMATH-002: Static abstract members for operators
- NET-GMATH-003: Generic algorithms without boxing
- NET-GMATH-004: Use for reusable numeric code

## Interop Enhancements
- NET-INTOP-001: LibraryImport source generator
- NET-INTOP-002: Improved performance over DllImport
- NET-INTOP-003: Marshalling customization
- NET-INTOP-004: Use for all P/Invoke scenarios

## Dependency Injection
- NET-DI-001: Keyed services support
- NET-DI-002: Service validation on startup
- NET-DI-003: Scope validation improvements
- NET-DI-004: Use ValidateOnStart() for IOptions<T>
- NET-DI-005: Mandatory scope validation in development

## Configuration
- NET-CFG-001: IConfiguration with validation
- NET-CFG-002: IOptions<T> with ValidateOnStart()
- NET-CFG-003: IOptionsSnapshot<T> for scoped config
- NET-CFG-004: IOptionsMonitor<T> for runtime changes
- NET-CFG-005: JSON source generation for config binding

## Forbidden Patterns
- NET-FORBID-001: No DateTime.Now or DateTime.UtcNow (use TimeProvider)
- NET-FORBID-002: No Task.Run() in libraries (push to caller)
- NET-FORBID-003: No .Result or .Wait() on Tasks (use await)
- NET-FORBID-004: No ConfigureAwait(true) in libraries
- NET-FORBID-005: No reflection in NativeAOT scenarios
- NET-FORBID-006: No Newtonsoft.Json (use System.Text.Json)
- NET-FORBID-007: No unvalidated IOptions<T> usage

## Version Compatibility
- NET-VER-001: Target .NET 10 LTS for new projects
- NET-VER-002: Support .NET 10 through November 2028
- NET-VER-003: No multi-targeting unless necessary
- NET-VER-004: Use LTS versions for production
- NET-VER-005: Upgrade deprecated APIs immediately
