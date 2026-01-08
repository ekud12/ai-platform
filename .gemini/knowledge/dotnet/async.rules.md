# C# Async Rules

## Purpose
Definitions for asynchronous programming standards in C#.

## Authority
Governs all `.cs` files using `async`/`await`.

---

## CS-ASYNC-001 — CancellationToken Required
**Severity: Critical**

**Rule**
All async methods performing I/O or long-running operations MUST accept a `CancellationToken`.

**Bad Pattern**
```csharp
public async Task<User> GetUserAsync(int id) {
    return await _db.Users.Find(id);
}
```

**Good Pattern**
```csharp
public async Task<User> GetUserAsync(int id, CancellationToken ct) {
    return await _db.Users.Find(id, ct);
}
```

---

## CS-ASYNC-002 — CancellationToken Last Parameter
**Severity: Warning**

**Rule**
`CancellationToken` MUST be the last parameter in the method signature.

**Bad Pattern**
```csharp
public async Task Do(CancellationToken ct, int data) { ... }
```

**Good Pattern**
```csharp
public async Task Do(int data, CancellationToken ct = default) { ... }
```

---

## CS-ASYNC-003 — Async Suffix
**Severity: Info**

**Rule**
Async methods MUST have the `Async` suffix (except controllers/event handlers).

**Bad Pattern**
```csharp
public async Task GetData() { ... }
```

**Good Pattern**
```csharp
public async Task GetDataAsync() { ... }
```

---

## CS-ASYNC-004 — No Async Void
**Severity: Critical**

**Rule**
`async void` is STRICTLY FORBIDDEN (except for top-level event handlers). It crashes the process on exception.

**Bad Pattern**
```csharp
public async void SaveData() { // CRASH RISK
    await _repo.Save();
}
```

**Good Pattern**
```csharp
public async Task SaveDataAsync() {
    await _repo.Save();
}
```

---

## CS-ASYNC-005 — ConfigureAwait(false) in Libraries
**Severity: Major**

**Rule**
Library code MUST use `ConfigureAwait(false)` to prevent context blocking.

**Bad Pattern**
```csharp
// In a Class Library
await _file.ReadAsync();
```

**Good Pattern**
```csharp
// In a Class Library
await _file.ReadAsync().ConfigureAwait(false);
```

---

## CS-ASYNC-006 — No Sync Over Async
**Severity: Critical**

**Rule**
NEVER block on async code using `.Result` or `.Wait()`. It causes deadlocks.

**Bad Pattern**
```csharp
var data = GetDataAsync().Result; // DEADLOCK
```

**Good Pattern**
```csharp
var data = await GetDataAsync();
```

---

## CS-ASYNC-007 — ValueTask Usage
**Severity: Major**

**Rule**
Use `ValueTask<T>` for hot path methods that often complete synchronously to reduce allocations.

**Bad Pattern**
```csharp
// In a cache lookup that usually hits
public async Task<User?> GetCachedUserAsync(int id) {
    if (_cache.TryGetValue(id, out var user))
        return user; // Allocates Task even for sync completion
    return await _db.GetUserAsync(id);
}
```

**Good Pattern**
```csharp
public ValueTask<User?> GetCachedUserAsync(int id) {
    if (_cache.TryGetValue(id, out var user))
        return ValueTask.FromResult(user); // No allocation
    return new ValueTask<User?>(GetFromDbAsync(id));
}
```

---

## CS-ASYNC-008 — Async Disposal
**Severity: Major**

**Rule**
Classes with async cleanup MUST implement `IAsyncDisposable` and consumers MUST use `await using`.

**Bad Pattern**
```csharp
public class DbConnection : IDisposable {
    public void Dispose() {
        _connection.CloseAsync().Wait(); // Blocking!
    }
}
```

**Good Pattern**
```csharp
public class DbConnection : IAsyncDisposable {
    public async ValueTask DisposeAsync() {
        await _connection.CloseAsync();
    }
}

// Usage
await using var conn = new DbConnection();
```

---

## CS-ASYNC-009 — Timeout All HTTP Calls
**Severity: Major**

**Rule**
HTTP client calls MUST have a timeout configured.

**Related Rules**
- CS-DATA-008 covers database query timeouts specifically

**Bad Pattern**
```csharp
var http = new HttpClient();
await http.GetAsync(url); // May hang forever
```

**Good Pattern**
```csharp
var http = new HttpClient { Timeout = TimeSpan.FromSeconds(30) };
await http.GetAsync(url, ct);
```

---

## CS-ASYNC-010 — Async Streams
**Severity: Major**

**Rule**
Use `IAsyncEnumerable<T>` for streaming data instead of returning `Task<List<T>>`.

**Bad Pattern**
```csharp
public async Task<List<Order>> GetAllOrdersAsync() {
    var orders = new List<Order>();
    await foreach (var order in _db.Orders.AsAsyncEnumerable()) {
        orders.Add(order); // Buffers everything in memory
    }
    return orders;
}
```

**Good Pattern**
```csharp
public async IAsyncEnumerable<Order> GetAllOrdersAsync(
    [EnumeratorCancellation] CancellationToken ct = default) {
    await foreach (var order in _db.Orders.AsAsyncEnumerable().WithCancellation(ct)) {
        yield return order; // Streams one at a time
    }
}
```