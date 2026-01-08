# .NET 10 Platform Rules

## Purpose

Standards for .NET 10 platform features including runtime enhancements, NativeAOT, post-quantum cryptography, WebAuthN, and modern APIs.

## Authority

Governs all .NET 10 applications. Modern platform features are mandatory for new projects.

## Scope

Applies to runtime configuration, cryptography, authentication, networking, and platform APIs.

---

## CS-PLAT-001 — TimeProvider for Time Operations

**Severity: Critical**

**Rule**
All time operations MUST use injected `TimeProvider` instead of `DateTime.UtcNow` or `DateTime.Now`.

**Bad Pattern**
```csharp
public class TokenService
{
    public bool IsExpired(Token token)
    {
        return token.ExpiresAt < DateTime.UtcNow; // Untestable
    }
}
```

**Good Pattern**
```csharp
public class TokenService(TimeProvider timeProvider)
{
    public bool IsExpired(Token token)
    {
        return token.ExpiresAt < timeProvider.GetUtcNow();
    }
}
```

**Rationale**
TimeProvider enables deterministic testing of time-dependent logic without mocking static methods.

---

## CS-PLAT-002 — Source-Generated JSON Serialization

**Severity: Major**

**Rule**
All JSON serialization MUST use source-generated `JsonSerializerContext` for AOT compatibility and performance.

**Bad Pattern**
```csharp
var json = JsonSerializer.Serialize(user); // Reflection-based
var user = JsonSerializer.Deserialize<User>(json);
```

**Good Pattern**
```csharp
[JsonSerializable(typeof(User))]
[JsonSerializable(typeof(List<User>))]
public partial class AppJsonContext : JsonSerializerContext { }

var json = JsonSerializer.Serialize(user, AppJsonContext.Default.User);
var user = JsonSerializer.Deserialize(json, AppJsonContext.Default.User);
```

**Rationale**
Source generation eliminates reflection, enabling NativeAOT and improving startup/throughput.

---

## CS-PLAT-003 — IExceptionHandler for Global Errors

**Severity: Major**

**Rule**
All ASP.NET Core applications MUST implement `IExceptionHandler` for centralized exception handling.

**Bad Pattern**
```csharp
app.UseExceptionHandler(app => app.Run(async context =>
{
    context.Response.StatusCode = 500;
    await context.Response.WriteAsync("Error");
}));
```

**Good Pattern**
```csharp
public class GlobalExceptionHandler(ILogger<GlobalExceptionHandler> logger) : IExceptionHandler
{
    public async ValueTask<bool> TryHandleAsync(
        HttpContext context,
        Exception exception,
        CancellationToken ct)
    {
        logger.LogError(exception, "Unhandled exception");

        await Results.Problem(
            statusCode: 500,
            title: "Internal Server Error",
            extensions: new Dictionary<string, object?>
            {
                ["traceId"] = Activity.Current?.Id ?? context.TraceIdentifier
            }
        ).ExecuteAsync(context);

        return true;
    }
}

// Registration
builder.Services.AddExceptionHandler<GlobalExceptionHandler>();
```

**Rationale**
IExceptionHandler provides type-safe, testable exception handling with proper DI support.

---

## CS-PLAT-004 — Built-in Rate Limiting

**Severity: Major**

**Rule**
All public APIs MUST use built-in `RateLimiter` middleware with named policies.

**Bad Pattern**
```csharp
// No rate limiting or custom implementation
app.MapGet("/api/data", () => GetData());
```

**Good Pattern**
```csharp
builder.Services.AddRateLimiter(options =>
{
    options.AddTokenBucketLimiter("api", config =>
    {
        config.TokenLimit = 100;
        config.ReplenishmentPeriod = TimeSpan.FromMinutes(1);
        config.TokensPerPeriod = 100;
        config.QueueLimit = 10;
    });

    options.RejectionStatusCode = StatusCodes.Status429TooManyRequests;
});

app.UseRateLimiter();

app.MapGet("/api/data", () => GetData())
   .RequireRateLimiting("api");
```

**Rationale**
Built-in rate limiting provides consistent, configurable protection without third-party dependencies.

---

## CS-PLAT-005 — Frozen Collections for Lookups

**Severity: Major**

**Rule**
Read-only lookup collections MUST use `FrozenDictionary` or `FrozenSet` for optimal performance.

**Bad Pattern**
```csharp
private static readonly Dictionary<string, Handler> Handlers = new()
{
    ["create"] = new CreateHandler(),
    ["update"] = new UpdateHandler()
};
```

**Good Pattern**
```csharp
private static readonly FrozenDictionary<string, Handler> Handlers =
    new Dictionary<string, Handler>
    {
        ["create"] = new CreateHandler(),
        ["update"] = new UpdateHandler()
    }.ToFrozenDictionary();
```

**Rationale**
Frozen collections optimize for read performance with immutable, cache-friendly data structures.

---

## CS-PLAT-006 — SearchValues for Multi-Value Search

**Severity: Info**

**Rule**
Multi-character/value searches SHOULD use `SearchValues<T>` for vectorized performance.

**Bad Pattern**
```csharp
var index = text.IndexOfAny(new[] { '<', '>', '&', '"' });
```

**Good Pattern**
```csharp
private static readonly SearchValues<char> HtmlChars =
    SearchValues.Create("<>&\"");

var index = text.AsSpan().IndexOfAny(HtmlChars);
```

**Rationale**
SearchValues uses SIMD vectorization for significantly faster multi-value searches.

---

## CS-PLAT-007 — Channels for Producer-Consumer

**Severity: Major**

**Rule**
Producer-consumer patterns MUST use `System.Threading.Channels` with bounded capacity.

**Bad Pattern**
```csharp
private readonly Queue<WorkItem> _queue = new();
private readonly object _lock = new();

public void Enqueue(WorkItem item)
{
    lock (_lock) { _queue.Enqueue(item); }
}
```

**Good Pattern**
```csharp
private readonly Channel<WorkItem> _channel =
    Channel.CreateBounded<WorkItem>(new BoundedChannelOptions(1000)
    {
        FullMode = BoundedChannelFullMode.Wait,
        SingleReader = true,
        SingleWriter = false
    });

public async ValueTask EnqueueAsync(WorkItem item, CancellationToken ct)
{
    await _channel.Writer.WriteAsync(item, ct);
}

public IAsyncEnumerable<WorkItem> ReadAllAsync(CancellationToken ct)
{
    return _channel.Reader.ReadAllAsync(ct);
}
```

**Rationale**
Channels provide thread-safe, high-performance async producer-consumer with backpressure.

---

## CS-PLAT-008 — System.Diagnostics.Metrics

**Severity: Major**

**Rule**
Application metrics MUST use `System.Diagnostics.Metrics` with OpenTelemetry export.

**Bad Pattern**
```csharp
private static int _requestCount;
Interlocked.Increment(ref _requestCount);
```

**Good Pattern**
```csharp
public class OrderMetrics
{
    private readonly Counter<long> _ordersCreated;
    private readonly Histogram<double> _orderProcessingTime;

    public OrderMetrics(IMeterFactory meterFactory)
    {
        var meter = meterFactory.Create("MyApp.Orders");
        _ordersCreated = meter.CreateCounter<long>(
            "orders.created",
            unit: "{order}",
            description: "Number of orders created");
        _orderProcessingTime = meter.CreateHistogram<double>(
            "orders.processing_time",
            unit: "ms",
            description: "Order processing duration");
    }

    public void RecordOrderCreated() => _ordersCreated.Add(1);
    public void RecordProcessingTime(double ms) => _orderProcessingTime.Record(ms);
}
```

**Rationale**
System.Diagnostics.Metrics is the standard .NET metrics API with native OpenTelemetry integration.

---

## CS-PLAT-009 — NativeAOT Compatibility

**Severity: Major**

**Rule**
Libraries MUST be designed for NativeAOT compatibility - avoid reflection, use source generators.

**Bad Pattern**
```csharp
// Uses reflection - breaks NativeAOT
var props = typeof(User).GetProperties();
var value = Activator.CreateInstance(type);
```

**Good Pattern**
```csharp
// Use source generators
[JsonSerializable(typeof(User))]
public partial class UserJsonContext : JsonSerializerContext { }

// Use generic constraints instead of reflection
public T Create<T>() where T : new() => new T();

// Use compile-time types
public static User CreateUser() => new User();
```

**Rationale**
NativeAOT requires compile-time type information. Reflection is unavailable or limited.

---

## CS-PLAT-010 — Post-Quantum Cryptography

**Severity: Info**

**Rule**
Long-term data protection SHOULD use post-quantum algorithms (ML-DSA) on Windows with CNG.

**Bad Pattern**
```csharp
// Classical cryptography only
using var rsa = RSA.Create();
var signature = rsa.SignData(data, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
```

**Good Pattern**
```csharp
// Post-quantum digital signatures (Windows CNG)
using var mlDsa = MLDsa.Create(MLDsaParameterSet.ML_DSA_65);
var signature = mlDsa.SignData(data);
var isValid = mlDsa.VerifyData(data, signature);
```

**Rationale**
Post-quantum algorithms protect against future quantum computer attacks on current encrypted data.

---

## CS-PLAT-011 — WebAuthN and Passkeys

**Severity: Major**

**Rule**
New authentication systems SHOULD implement WebAuthN/passkey support for passwordless auth.

**Bad Pattern**
```csharp
// Password-only authentication
public async Task<bool> ValidateAsync(string username, string password)
{
    var user = await _users.FindAsync(username);
    return _hasher.Verify(password, user.PasswordHash);
}
```

**Good Pattern**
```csharp
// WebAuthN passkey authentication
builder.Services.AddAuthentication()
    .AddWebAuthn(options =>
    {
        options.RelyingPartyId = "example.com";
        options.RelyingPartyName = "Example App";
        options.AllowedCredentialTypes = new[] { PublicKeyCredentialType.PublicKey };
    });

// Registration endpoint
app.MapPost("/auth/register/begin", async (WebAuthnService webAuthn, User user) =>
{
    var options = await webAuthn.BeginRegistrationAsync(user);
    return Results.Ok(options);
});
```

**Rationale**
WebAuthN provides phishing-resistant, passwordless authentication using hardware keys or biometrics.

---

## CS-PLAT-012 — TLS 1.3 Enforcement

**Severity: Major**

**Rule**
All network connections MUST prefer TLS 1.3 and disable older versions where possible.

**Bad Pattern**
```csharp
// Allows insecure protocols
ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls | SecurityProtocolType.Tls11;
```

**Good Pattern**
```csharp
// TLS 1.3 preferred, 1.2 minimum
builder.WebHost.ConfigureKestrel(options =>
{
    options.ConfigureHttpsDefaults(https =>
    {
        https.SslProtocols = SslProtocols.Tls13 | SslProtocols.Tls12;
    });
});

// For HttpClient
var handler = new SocketsHttpHandler
{
    SslOptions = new SslClientAuthenticationOptions
    {
        EnabledSslProtocols = SslProtocols.Tls13 | SslProtocols.Tls12
    }
};
```

**Rationale**
TLS 1.3 provides improved security and performance. Older versions have known vulnerabilities.

---

## CS-PLAT-013 — OpenAPI 3.1 Documentation

**Severity: Info**

**Rule**
APIs SHOULD generate OpenAPI 3.1 documentation with comprehensive metadata.

**Bad Pattern**
```csharp
app.MapGet("/users/{id}", (int id) => GetUser(id));
// No documentation
```

**Good Pattern**
```csharp
app.MapGet("/users/{id}", [EndpointSummary("Get user by ID")]
    [EndpointDescription("Retrieves a single user by their unique identifier")]
    [ProducesResponseType<User>(200)]
    [ProducesResponseType<ProblemDetails>(404)]
    (int id) => GetUser(id))
    .WithName("GetUser")
    .WithTags("Users")
    .WithOpenApi();

// Enable OpenAPI 3.1
builder.Services.AddOpenApi(options =>
{
    options.OpenApiVersion = OpenApiSpecVersion.OpenApi3_1;
});
```

**Rationale**
OpenAPI 3.1 enables better tooling, client generation, and API documentation.

---

## CS-PLAT-014 — IOptions Validation

**Severity: Major**

**Rule**
All configuration options MUST use `ValidateOnStart()` with data annotations or custom validation.

**Bad Pattern**
```csharp
builder.Services.Configure<DatabaseOptions>(config.GetSection("Database"));
// No validation - bad config discovered at runtime
```

**Good Pattern**
```csharp
public class DatabaseOptions
{
    [Required]
    public required string ConnectionString { get; init; }

    [Range(1, 100)]
    public int MaxPoolSize { get; init; } = 10;
}

builder.Services.AddOptions<DatabaseOptions>()
    .Bind(config.GetSection("Database"))
    .ValidateDataAnnotations()
    .ValidateOnStart();
```

**Rationale**
Startup validation fails fast on misconfiguration instead of runtime failures.

---

## CS-PLAT-015 — Keyed Services

**Severity: Info**

**Rule**
Multiple implementations of the same interface SHOULD use keyed DI services.

**Bad Pattern**
```csharp
// Awkward factory pattern
public interface IStorageFactory
{
    IStorage Create(string type);
}
```

**Good Pattern**
```csharp
builder.Services.AddKeyedSingleton<IStorage, LocalStorage>("local");
builder.Services.AddKeyedSingleton<IStorage, S3Storage>("s3");
builder.Services.AddKeyedSingleton<IStorage, AzureStorage>("azure");

public class FileService([FromKeyedServices("s3")] IStorage storage)
{
    // Uses S3 storage specifically
}
```

**Rationale**
Keyed services provide clean, type-safe resolution of multiple implementations.

---

## CS-PLAT-016 — Minimal API Validation

**Severity: Major**

**Rule**
Minimal API endpoints MUST use endpoint filters for input validation.

**Bad Pattern**
```csharp
app.MapPost("/orders", (CreateOrderRequest request) =>
{
    if (string.IsNullOrEmpty(request.CustomerId))
        return Results.BadRequest("CustomerId required");
    // More manual validation...
});
```

**Good Pattern**
```csharp
public class ValidationFilter<T> : IEndpointFilter where T : class
{
    public async ValueTask<object?> InvokeAsync(
        EndpointFilterInvocationContext context,
        EndpointFilterDelegate next)
    {
        var validator = context.HttpContext.RequestServices
            .GetService<IValidator<T>>();

        var arg = context.Arguments.OfType<T>().FirstOrDefault();
        if (arg is not null && validator is not null)
        {
            var result = await validator.ValidateAsync(arg);
            if (!result.IsValid)
                return Results.ValidationProblem(result.ToDictionary());
        }

        return await next(context);
    }
}

app.MapPost("/orders", (CreateOrderRequest request) => CreateOrder(request))
   .AddEndpointFilter<ValidationFilter<CreateOrderRequest>>();
```

**Rationale**
Endpoint filters provide consistent, reusable validation across all endpoints.

---

## Forbidden Patterns

- CS-PLAT-FORBID-001: No `DateTime.Now` or `DateTime.UtcNow` (use TimeProvider)
- CS-PLAT-FORBID-002: No reflection-based JSON serialization (use source generators)
- CS-PLAT-FORBID-003: No `Task.Run()` in libraries (push threading decisions to caller)
- CS-PLAT-FORBID-004: No `.Result` or `.Wait()` on tasks (use await)
- CS-PLAT-FORBID-005: No `ConfigureAwait(true)` in libraries
- CS-PLAT-FORBID-006: No Newtonsoft.Json in new projects (use System.Text.Json)
- CS-PLAT-FORBID-007: No unvalidated IOptions<T> usage
- CS-PLAT-FORBID-008: No Queue<T> for async scenarios (use Channels)
- CS-PLAT-FORBID-009: No Dictionary for static lookups (use FrozenDictionary)
- CS-PLAT-FORBID-010: No TLS versions below 1.2
