# .NET Caching Rules

## Purpose

Standards for caching strategies and implementations.

## Authority

Governs all cache usage in .NET applications.

## Scope

Applies to in-memory caching, distributed caching, and hybrid caching strategies.

## Constraints

- Cache must not be the source of truth
- Cache invalidation must be explicit
- Cache keys must be predictable

## Rule Format

All rules use the CS-CACHE prefix.

---

## CS-CACHE-001 — Hybrid L1+L2 Cache
**Severity: Info**

**Rule**
High-traffic applications SHOULD use hybrid caching (L1 in-memory + L2 distributed) for optimal performance.

**Rationale**
L1 provides sub-millisecond access for hot data. L2 provides shared state across instances. Hybrid combines both benefits.

**Basic Pattern (L2 only)**
```csharp
services.AddStackExchangeRedisCache(options =>
{
    options.Configuration = "redis:6379";
});
```

**Recommended Pattern (L1+L2 Hybrid)**
```csharp
services.AddFusionCache()
    .WithDefaultEntryOptions(new FusionCacheEntryOptions
    {
        Duration = TimeSpan.FromMinutes(5),
        IsFailSafeEnabled = true,
        FailSafeMaxDuration = TimeSpan.FromHours(1)
    })
    .WithDistributedCache(
        new RedisCache(new RedisCacheOptions { Configuration = "redis:6379" })
    );
```

---

## CS-CACHE-002 — Cache in Orchestrator Layer
**Severity: Major**

**Rule**
Caching logic MUST be in the Orchestrator layer, not in API endpoints or repositories.

**Rationale**
Centralizing cache logic in orchestrators ensures consistent caching behavior and simplifies cache invalidation.

**Bad Pattern**
```csharp
// In endpoint - caching scattered everywhere
app.MapGet("/users/{id}", async (int id, IFusionCache cache, IDb db) =>
{
    var cached = await cache.GetOrDefaultAsync<User>($"user:{id}");
    if (cached != null) return Results.Ok(cached);

    var user = await db.Users.FindAsync(id);
    await cache.SetAsync($"user:{id}", user);
    return Results.Ok(user);
});
```

**Good Pattern**
```csharp
// In orchestrator - single responsibility for caching
public class UserOrchestrator(IFusionCache cache, IUserClient client) : IUserOrchestrator
{
    public async Task<UserDto?> GetByIdAsync(int id, CancellationToken ct)
    {
        return await cache.GetOrSetAsync(
            $"users:user:{id}",
            async _ => await client.GetByIdAsync(id, ct),
            ct);
    }
}

// Endpoint is clean
app.MapGet("/users/{id}", async (int id, IUserOrchestrator orchestrator, CancellationToken ct) =>
{
    var user = await orchestrator.GetByIdAsync(id, ct);
    return user is null ? Results.NotFound() : Results.Ok(user);
});
```

---

## CS-CACHE-003 — Cache Key Naming Convention
**Severity: Major**

**Rule**
Cache keys MUST follow `{domain}:{entity}:{identifier}` pattern.

**Rationale**
Consistent naming enables wildcard invalidation, debugging, and monitoring.

**Bad Pattern**
```csharp
await cache.GetAsync($"u_{id}");
await cache.GetAsync($"GetUserById_{id}");
await cache.GetAsync($"user-{id}-data");
```

**Good Pattern**
```csharp
await cache.GetAsync($"users:user:{id}");
await cache.GetAsync($"content:page:{slug}:{culture}");
await cache.GetAsync($"search:results:{queryHash}");

// With static class for consistency
public static class CacheKeys
{
    public static string User(int id) => $"users:user:{id}";
    public static string Page(string slug, string culture) => $"content:page:{slug}:{culture}";
}
```

---

## CS-CACHE-004 — Fail-Safe Caching
**Severity: Major**

**Rule**
Distributed cache MUST have fail-safe enabled to serve stale data on backend failures.

**Rationale**
When the data source is unavailable, serving stale cached data is better than returning errors.

**Bad Pattern**
```csharp
// No fail-safe - throws when Redis/backend is down
var data = await cache.GetOrSetAsync(key, async _ =>
{
    return await _api.GetDataAsync(); // If API is down, request fails
});
```

**Good Pattern**
```csharp
var options = new FusionCacheEntryOptions
{
    Duration = TimeSpan.FromMinutes(5),
    IsFailSafeEnabled = true,
    FailSafeMaxDuration = TimeSpan.FromHours(2),
    FailSafeThrottleDuration = TimeSpan.FromSeconds(30)
};

var data = await cache.GetOrSetAsync(key, async _ =>
{
    return await _api.GetDataAsync();
}, options);
// If API is down, returns stale cached data instead of failing
```
