# .NET API Rules

## Purpose
Standards for HTTP API design in ASP.NET Core.

## Authority
Governs all REST endpoints and Controllers.

---

## CS-API-001 — Minimal API Pattern
**Severity: Info**

**Rule**
New endpoints SHOULD use Minimal APIs (`app.MapGet`) over Controllers.

**Bad Pattern**
```csharp
public class UserController : ControllerBase { ... }
```

**Good Pattern**
```csharp
app.MapGet("/users", async (UserDb db) => ...);
```

---

## CS-API-002 — ProblemDetails for Errors
**Severity: Critical**

**Rule**
Errors MUST return RFC 9457 `ProblemDetails`.

**Bad Pattern**
```csharp
return BadRequest("Something went wrong");
```

**Good Pattern**
```csharp
return Results.Problem(detail: "User not found", statusCode: 404);
```

---

## CS-API-003 — OpenAPI Documentation
**Severity: Major**

**Rule**
All endpoints MUST produce OpenAPI/Swagger documentation.

**Bad Pattern**
```csharp
app.MapGet("/data", () => "data"); // No metadata
```

**Good Pattern**
```csharp
app.MapGet("/data", () => "data")
   .WithOpenApi()
   .Produces<string>(200);
```

---

## CS-API-004 — Request Validation
**Severity: Critical**

**Rule**
Inputs MUST be validated (FluentValidation or DataAnnotations).

**Bad Pattern**
```csharp
app.MapPost("/users", (UserDto u) => db.Save(u));
```

**Good Pattern**
```csharp
app.MapPost("/users", async (IValidator<UserDto> v, UserDto u) => {
    var result = await v.ValidateAsync(u);
    if(!result.IsValid) return Results.ValidationProblem(result.ToDictionary());
    ...
});
```

---

## CS-API-005 — Response Typing
**Severity: Major**

**Rule**
Endpoints MUST use explicit `TypedResults` or return types.

**Bad Pattern**
```csharp
public async Task<IActionResult> Get() { ... } // Unknown return shape
```

**Good Pattern**
```csharp
public async Task<Results<Ok<User>, NotFound>> Get() { ... }
```

---

## CS-API-006 — Versioning Strategy
**Severity: Critical**

**Rule**
APIs MUST be versioned (URL or Header).

**Bad Pattern**
```csharp
app.MapGet("/api/users", ...);
```

**Good Pattern**
```csharp
var v1 = app.NewVersionedApi("1.0");
v1.MapGet("/api/v1/users", ...);
```

---

## CS-API-007 — Idempotency
**Severity: Warning**

**Rule**
Critical mutations (POST/PUT) SHOULD support Idempotency Keys.

**Bad Pattern**
```csharp
// Charge logic that runs twice if network fails
```

**Good Pattern**
```csharp
// Middleware checks "Idempotency-Key" header before executing
```

---

## CS-API-008 — Rate Limiting
**Severity: Critical**

**Rule**
Public APIs MUST have Rate Limiting enabled.

**Bad Pattern**
```csharp
app.MapGet("/heavy-calculation", ...); // Abusable
```

**Good Pattern**
```csharp
app.MapGet("/heavy-calculation", ...).RequireRateLimiting("fixed");
```

---

## CS-API-009 — Pagination
**Severity: Critical**

**Rule**
List endpoints MUST support pagination.

**Bad Pattern**
```csharp
return await db.Users.ToListAsync(); // Could return 1M rows
```

**Good Pattern**
```csharp
return await db.Users.Skip((page-1)*size).Take(size).ToListAsync();
```

---

## CS-API-010 — Health Endpoints
**Severity: Critical**

**Rule**
Services MUST expose `/health` or `/healthz`.

**Bad Pattern**
```csharp
// No health check configured
```

**Good Pattern**
```csharp
app.MapHealthChecks("/health");
```

---

## CS-API-011 — Response Compression
**Severity: Major**

**Rule**
Large responses MUST enable compression (Brotli/Gzip).

**Bad Pattern**
```csharp
// No compression configured - large JSON responses sent uncompressed
app.MapGet("/data", () => GetLargeDataset());
```

**Good Pattern**
```csharp
builder.Services.AddResponseCompression(options => {
    options.EnableForHttps = true;
    options.Providers.Add<BrotliCompressionProvider>();
    options.Providers.Add<GzipCompressionProvider>();
});

app.UseResponseCompression();
```

---

## CS-API-012 — Request Size Limits
**Severity: Critical**

**Rule**
Endpoints MUST configure max request body size to prevent DoS attacks.

**Bad Pattern**
```csharp
// Default allows very large uploads
app.MapPost("/upload", async (HttpRequest req) => {
    var body = await req.ReadFromJsonAsync<object>();
});
```

**Good Pattern**
```csharp
app.MapPost("/upload", async (HttpRequest req) => { ... })
   .WithMetadata(new RequestSizeLimitAttribute(10 * 1024 * 1024)); // 10MB max

// Or globally
builder.WebHost.ConfigureKestrel(o => o.Limits.MaxRequestBodySize = 10_000_000);
```

---

## CS-API-013 — Cache Headers
**Severity: Major**

**Rule**
Cacheable responses MUST have appropriate Cache-Control headers.

**Bad Pattern**
```csharp
app.MapGet("/static-data", () => GetRarelyChangingData());
// No cache headers - browsers/CDNs can't cache
```

**Good Pattern**
```csharp
app.MapGet("/static-data", () => GetRarelyChangingData())
   .CacheOutput(p => p.Expire(TimeSpan.FromHours(1)));

// Or manually
app.MapGet("/static-data", (HttpContext ctx) => {
    ctx.Response.Headers.CacheControl = "public, max-age=3600";
    return GetRarelyChangingData();
});
```

---

## CS-API-014 — Correlation Header Propagation
**Severity: Major**

**Rule**
APIs MUST propagate correlation/trace headers to downstream services.

**Related Rules**
- CS-OBS-003 covers correlation ID generation and logging

**Bad Pattern**
```csharp
// Calling downstream service without propagating trace context
var result = await _httpClient.GetAsync("https://other-service/api");
```

**Good Pattern**
```csharp
// Configure HttpClient to propagate headers
builder.Services.AddHttpClient("downstream")
    .AddHeaderPropagation();

builder.Services.AddHeaderPropagation(options => {
    options.Headers.Add("X-Correlation-Id");
    options.Headers.Add("traceparent");
});

app.UseHeaderPropagation();
```

---

## CS-API-015 — Endpoint Extension Methods
**Severity: Major**

**Rule**
API endpoints MUST be defined as extension methods on `IEndpointRouteBuilder` in dedicated `{Resource}Endpoints.cs` files.

**Bad Pattern**
```csharp
// Everything in Program.cs
app.MapGet("/api/users/{id}", async (int id, IUserService svc) => ...);
app.MapPost("/api/users", async (UserDto dto, IUserService svc) => ...);
app.MapGet("/api/orders/{id}", async (int id, IOrderService svc) => ...);
```

**Good Pattern**
```csharp
// Endpoints/UserEndpoints.cs
public static class UserEndpoints
{
    public static IEndpointRouteBuilder MapUserEndpoints(this IEndpointRouteBuilder endpoints)
    {
        var group = endpoints.MapGroup("/api/users");
        group.MapGet("/{id}", GetById);
        group.MapPost("/", Create);
        return endpoints;
    }

    private static async Task<IResult> GetById(int id, IUserOrchestrator svc, CancellationToken ct) => ...
}

// Program.cs - clean and organized
app.MapUserEndpoints();
app.MapOrderEndpoints();
```

---

## CS-API-016 — Static Routes Class
**Severity: Major**

**Rule**
Route paths and names MUST be defined in a static `Routes` class, not inline strings.

**Bad Pattern**
```csharp
group.MapGet("/api/v1/media/{id}", GetById)
    .WithName("GetMediaById");
```

**Good Pattern**
```csharp
public static class Routes
{
    public static class Groups
    {
        public const string V1 = "/api/v1";
        public const string Media = "/media";
    }

    public static class Media
    {
        public const string ById = "/{id}";
        public const string Search = "/search";

        public static class Names
        {
            public const string GetById = nameof(GetById);
            public const string Search = nameof(Search);
        }
    }
}

// Usage
endpoints.MapGroup(Routes.Groups.V1)
    .MapGroup(Routes.Groups.Media)
    .MapGet(Routes.Media.ById, GetById)
    .WithName(Routes.Media.Names.GetById);
```

---

## CS-API-017 — Endpoint Metadata Chain
**Severity: Major**

**Rule**
Endpoints MUST declare complete metadata: name, produces, validation filter.

**Bad Pattern**
```csharp
group.MapGet("/{id}", GetById);
// No metadata - poor OpenAPI docs, no validation
```

**Good Pattern**
```csharp
group.MapGet("/{id}", GetById)
    .WithName(Routes.Media.Names.GetById)
    .WithSummary("Get media by ID")
    .WithDescription("Returns media metadata and download URLs")
    .Produces<MediaDto>(200)
    .Produces(404)
    .ProducesValidationProblem()
    .AddEndpointFilter<ValidationFilter>();
```

---

## CS-API-018 — Orchestrator Pattern for Business Logic
**Severity: Major**

**Rule**
Endpoints MUST NOT contain business logic. Use an `I{Domain}Orchestrator` service.

**Related Rules**
- CS-CACHE-002 covers caching in orchestrator layer

**Bad Pattern**
```csharp
private static async Task<IResult> GetUser(int id, IDbContext db, IFusionCache cache)
{
    var cached = await cache.GetOrDefaultAsync<User>($"user:{id}");
    if (cached != null) return Results.Ok(cached);

    var user = await db.Users.FindAsync(id);
    if (user == null) return Results.NotFound();

    await cache.SetAsync($"user:{id}", user);
    return Results.Ok(user);
}
```

**Good Pattern**
```csharp
private static async Task<IResult> GetUser(
    int id,
    IUserOrchestrator orchestrator,
    CancellationToken ct)
{
    var user = await orchestrator.GetByIdAsync(id, ct);
    return user is null ? Results.NotFound() : Results.Ok(user);
}

// Business logic, caching, validation in orchestrator
public class UserOrchestrator(IFusionCache cache, IUserClient client) : IUserOrchestrator
{
    public async Task<UserDto?> GetByIdAsync(int id, CancellationToken ct) => ...
}
```

---

## CS-API-019 — HTTP Client Handler Pipeline
**Severity: Major**

**Rule**
HTTP clients MUST use a handler pipeline with correlation, logging, and retry policies.

**Related Rules**
- CS-OBS-013 covers HTTP correlation handler
- CS-OBS-014 covers HTTP logging handler

**Bad Pattern**
```csharp
services.AddHttpClient<IExternalApi, ExternalApiClient>();
// No handlers - no correlation, no logging, no retry
```

**Good Pattern**
```csharp
services.AddHttpClient<IExternalApi, ExternalApiClient>()
    .AddHttpMessageHandler<RequestCorrelationHandler>()
    .AddHttpMessageHandler<HttpLoggingHandler>()
    .AddPolicyHandler(GetRetryPolicy())
    .AddPolicyHandler(GetCircuitBreakerPolicy());

private static IAsyncPolicy<HttpResponseMessage> GetRetryPolicy() =>
    HttpPolicyExtensions
        .HandleTransientHttpError()
        .WaitAndRetryAsync(3, retryAttempt =>
            TimeSpan.FromSeconds(Math.Pow(2, retryAttempt)));
```

---

## CS-API-020 — Service Registration Extension Pattern
**Severity: Major**

**Rule**
Service registration MUST use extension methods on `IServiceCollection` with `IConfiguration` parameter.

**Bad Pattern**
```csharp
// Program.cs - registration logic scattered
builder.Services.AddScoped<IUserService, UserService>();
builder.Services.AddScoped<IOrderService, OrderService>();
builder.Services.Configure<CacheOptions>(builder.Configuration.GetSection("Cache"));
```

**Good Pattern**
```csharp
// Extensions/ServiceCollectionExtensions.cs
public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddDomainServices(
        this IServiceCollection services,
        IConfiguration config)
    {
        services.AddOptions<CacheOptions>()
            .Bind(config.GetSection("Cache"))
            .ValidateDataAnnotations()
            .ValidateOnStart();

        services.AddScoped<IUserOrchestrator, UserOrchestrator>();
        services.AddScoped<IOrderOrchestrator, OrderOrchestrator>();

        return services;
    }
}

// Program.cs - clean
builder.Services.AddDomainServices(builder.Configuration);
```