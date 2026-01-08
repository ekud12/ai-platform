# .NET Security Rules

## Purpose
Defines non-negotiable security standards for C#/.NET development.

## Authority
Governs all backend code. Violations are immediate build failures in CI/CD.

---

## CS-SEC-001 — SQL Injection Prevention
**Severity: Critical**

**Rule**
NEVER concatenate strings into SQL queries. MUST use parameterized queries or EF Core LINQ methods.

**Bad Pattern**
```csharp
var query = "SELECT * FROM Users WHERE Name = '" + name + "'";
// Attacker sends: "' OR '1'='1"
```

**Good Pattern**
```csharp
// EF Core
var user = await _context.Users.Where(u => u.Name == name).FirstOrDefaultAsync();

// Dapper
var user = await connection.QuerySingleAsync<User>(
    "SELECT * FROM Users WHERE Name = @Name", 
    new { Name = name }
);
```

---

## CS-SEC-002 — No Hardcoded Secrets
**Severity: Critical**

**Rule**
NEVER commit API keys, connection strings, or passwords to source control. Use `IConfiguration` or Key Vault.

**Bad Pattern**
```csharp
private const string ApiKey = "sk-1234567890abcdef";
```

**Good Pattern**
```csharp
var apiKey = _configuration["Integrations:Stripe:ApiKey"];
```

---

## CS-SEC-003 — Controller Input Validation
**Severity: Major**

**Rule**
Public API endpoints MUST validate all inputs. Prefer FluentValidation or DataAnnotations.

**Bad Pattern**
```csharp
[HttpPost]
public IActionResult CreateUser(UserDto dto) {
    _db.Save(dto); // No checks!
}
```

**Good Pattern**
```csharp
[HttpPost]
public async Task<IActionResult> CreateUser(UserDto dto) {
    if (!ModelState.IsValid) return BadRequest(ModelState);
    // or
    await _validator.ValidateAndThrowAsync(dto);
    
    await _service.CreateAsync(dto);
    return Ok();
}
```

---

## CS-SEC-004 — Secure Deserialization
**Severity: Critical**

**Rule**
Do not use `BinaryFormatter` or insecure serializers on untrusted data. Use `System.Text.Json`.

**Bad Pattern**
```csharp
var obj = new BinaryFormatter().Deserialize(stream);
```

**Good Pattern**
```csharp
var obj = await JsonSerializer.DeserializeAsync<MyType>(stream);
```

---

## CS-SEC-005 — CSRF Protection
**Severity: Critical**

**Rule**
Anti-forgery tokens MUST be validated on all state-changing endpoints.

**Bad Pattern**
```csharp
[HttpPost]
public IActionResult Transfer(TransferDto dto) {
    _service.Transfer(dto); // No CSRF protection
}
```

**Good Pattern**
```csharp
[HttpPost]
[ValidateAntiForgeryToken]
public IActionResult Transfer(TransferDto dto) {
    _service.Transfer(dto);
}

// Or for APIs, use SameSite cookies + custom header validation
```

---

## CS-SEC-006 — Path Traversal Prevention
**Severity: Critical**

**Rule**
File paths from user input MUST be sanitized. `Path.Combine` with user input is dangerous.

**Bad Pattern**
```csharp
var path = Path.Combine(_uploadDir, userFileName);
// User sends "../../../etc/passwd"
```

**Good Pattern**
```csharp
var safeName = Path.GetFileName(userFileName); // Strips directory components
var path = Path.Combine(_uploadDir, safeName);

// Verify the resolved path is within allowed directory
var fullPath = Path.GetFullPath(path);
if (!fullPath.StartsWith(_uploadDir)) throw new SecurityException();
```

---

## CS-SEC-007 — Cryptography Standards
**Severity: Critical**

**Rule**
Use secure cryptographic primitives. MD5/SHA1 are forbidden for security purposes. Use `RandomNumberGenerator` not `Random`.

**Bad Pattern**
```csharp
var random = new Random();
var token = random.Next().ToString(); // Predictable!

var hash = MD5.HashData(data); // Broken for security
```

**Good Pattern**
```csharp
var token = Convert.ToBase64String(RandomNumberGenerator.GetBytes(32));

var hash = SHA256.HashData(data); // Or SHA384/SHA512
```

---

## CS-SEC-008 — Authorization on Endpoints
**Severity: Critical**

**Rule**
All endpoints MUST have explicit authorization attributes. Implicit allow is forbidden.

**Bad Pattern**
```csharp
[ApiController]
public class AdminController : ControllerBase {
    [HttpGet] // No authorization - anyone can access!
    public IActionResult GetSecrets() { ... }
}
```

**Good Pattern**
```csharp
[ApiController]
[Authorize(Policy = "AdminOnly")]
public class AdminController : ControllerBase {
    [HttpGet]
    public IActionResult GetSecrets() { ... }

    [AllowAnonymous] // Explicit when public
    [HttpGet("health")]
    public IActionResult Health() { ... }
}
```

---

## CS-SEC-009 — Security Headers
**Severity: Major**

**Rule**
Responses MUST include security headers to prevent common attacks.

**Bad Pattern**
```csharp
// No security headers configured
app.MapGet("/", () => "Hello");
```

**Good Pattern**
```csharp
app.Use(async (context, next) => {
    context.Response.Headers.Add("X-Content-Type-Options", "nosniff");
    context.Response.Headers.Add("X-Frame-Options", "DENY");
    context.Response.Headers.Add("X-XSS-Protection", "1; mode=block");
    context.Response.Headers.Add("Referrer-Policy", "strict-origin-when-cross-origin");
    await next();
});

// Or use NWebsec middleware
```

---

## CS-SEC-010 — CORS Configuration
**Severity: Critical**

**Rule**
CORS policies MUST be explicit. `AllowAnyOrigin` with credentials is forbidden.

**Bad Pattern**
```csharp
builder.Services.AddCors(o => o.AddPolicy("Bad", p =>
    p.AllowAnyOrigin()
     .AllowAnyHeader()
     .AllowCredentials())); // Security vulnerability!
```

**Good Pattern**
```csharp
builder.Services.AddCors(o => o.AddPolicy("Strict", p =>
    p.WithOrigins("https://app.example.com")
     .WithMethods("GET", "POST")
     .WithHeaders("Content-Type", "Authorization")
     .AllowCredentials()));
```

---

## CS-SEC-011 — Options Pattern Validation
**Severity: Critical**

**Rule**
Configuration options MUST use `ValidateDataAnnotations()` and `ValidateOnStart()`.

**Rationale**
Fail-fast on startup prevents runtime errors from missing or invalid configuration.

**Bad Pattern**
```csharp
services.Configure<ApiOptions>(config.GetSection("Api"));
// Invalid config causes runtime errors
```

**Good Pattern**
```csharp
services.AddOptions<ApiOptions>()
    .Bind(config.GetSection("Api"))
    .ValidateDataAnnotations()
    .ValidateOnStart();

public class ApiOptions
{
    [Required]
    public required string BaseUrl { get; init; }

    [Range(1, 300)]
    public int TimeoutSeconds { get; init; } = 30;
}
```

---

## CS-SEC-012 — Environment Variables for Secrets
**Severity: Critical**

**Rule**
Secrets in Docker environments MUST use environment variables, NOT appsettings files.

**Rationale**
Environment variables are injected at runtime and don't persist in images or source control.

**Bad Pattern**
```dockerfile
COPY appsettings.Production.json /app/
# Secrets baked into image
```

```json
// appsettings.Production.json committed to repo
{
  "ConnectionStrings": {
    "Database": "Server=prod;Password=secret123"
  }
}
```

**Good Pattern**
```yaml
# docker-compose.yml
services:
  api:
    environment:
      - ConnectionStrings__Database=${DB_CONNECTION_STRING}
      - Api__ApiKey=${API_KEY}
```

```csharp
// Configuration automatically binds environment variables
builder.Configuration
    .AddEnvironmentVariables();
```

---

## CS-SEC-013 — Refit Client Security
**Severity: Major**

**Rule**
Refit clients MUST configure authentication headers via DelegatingHandler, NOT inline.

**Rationale**
Centralized auth handling ensures consistent security and enables token refresh logic.

**Bad Pattern**
```csharp
public interface IExternalApi
{
    [Headers("Authorization: Bearer hardcoded-token")]
    [Get("/data")]
    Task<Data> GetDataAsync();
}
```

**Good Pattern**
```csharp
public interface IExternalApi
{
    [Get("/data")]
    Task<Data> GetDataAsync(CancellationToken ct = default);
}

public class AuthHandler(ITokenProvider tokens) : DelegatingHandler
{
    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request,
        CancellationToken ct)
    {
        var token = await tokens.GetTokenAsync(ct);
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
        return await base.SendAsync(request, ct);
    }
}

// Registration
services.AddRefitClient<IExternalApi>()
    .ConfigureHttpClient(c => c.BaseAddress = new Uri(options.BaseUrl))
    .AddHttpMessageHandler<AuthHandler>();
```