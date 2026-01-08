# .NET Data Access Rules

## Purpose
Standards for database interaction in .NET (EF Core, Dapper, SQL).

## Authority
Governs all data access layers and repositories.

---

## CS-DATA-001 — Repository Pattern
**Severity: Major**

**Rule**
Business logic MUST use repository/data interfaces, NOT `DbContext` directly.

**Bad Pattern**
```csharp
// In Service
_dbContext.Users.Add(user);
```

**Good Pattern**
```csharp
// In Service
await _userRepository.AddAsync(user);
```

---

## CS-DATA-002 — Async Data Access
**Severity: Critical**

**Rule**
All data I/O MUST be `async`.

**Bad Pattern**
```csharp
var users = _context.Users.ToList(); // Blocking
```

**Good Pattern**
```csharp
var users = await _context.Users.ToListAsync(ct);
```

---

## CS-DATA-003 — No Tracking for Read-Only
**Severity: Major**

**Rule**
Read-only queries MUST use `AsNoTracking()`.

**Bad Pattern**
```csharp
var users = await _context.Users.ToListAsync(); // Tracks changes overhead
```

**Good Pattern**
```csharp
var users = await _context.Users.AsNoTracking().ToListAsync();
```

---

## CS-DATA-004 — Explicit Loading
**Severity: Critical**

**Rule**
Lazy loading is FORBIDDEN. Use explicit `.Include()`.

**Bad Pattern**
```csharp
// Lazy loading enabled globally
var orders = user.Orders; // N+1 Risk
```

**Good Pattern**
```csharp
var user = await _context.Users.Include(u => u.Orders).FirstAsync();
```

---

## CS-DATA-005 — Projection Queries
**Severity: Major**

**Rule**
Fetch only needed columns using `.Select()`, NOT full entities.

**Scope**
This rule applies to EF Core LINQ queries (LINQ-to-Entities) which translate to SQL. Database-side projection reduces network transfer and memory allocation.

**Related Rules**
- CS-PERF-009 restricts in-memory LINQ in hot paths (different context)

**Bad Pattern**
```csharp
var user = await _context.Users.FirstAsync(u => u.Id == 1);
return user.Name; // Loaded all columns uselessly
```

**Good Pattern**
```csharp
var name = await _context.Users
    .Where(u => u.Id == 1)
    .Select(u => u.Name)
    .FirstOrDefaultAsync();
```

---

## CS-DATA-006 — Transaction Scope
**Severity: Critical**

**Rule**
Multi-step mutations MUST use explicit transactions.

**Bad Pattern**
```csharp
await _repo.Debit(100);
// If crash here, money is lost
await _repo.Credit(100);
```

**Good Pattern**
```csharp
using var transaction = await _context.Database.BeginTransactionAsync();
try {
    await _repo.Debit(100);
    await _repo.Credit(100);
    await transaction.CommitAsync();
} catch {
    await transaction.RollbackAsync();
}
```

---

## CS-DATA-007 — Optimistic Concurrency
**Severity: Major**

**Rule**
Entities with concurrent access MUST have concurrency tokens (e.g., `RowVersion`).

**Bad Pattern**
```csharp
// Last writer wins (Silent overwrite)
_context.Update(user); 
```

**Good Pattern**
```csharp
// Throws DbUpdateConcurrencyException if changed
_context.Entry(user).Property(p => p.RowVersion).OriginalValue = version;
```

---

## CS-DATA-008 — Query Timeout
**Severity: Critical**

**Rule**
All database queries MUST have timeouts configured.

**Related Rules**
- CS-ASYNC-009 covers HTTP client timeouts specifically

**Bad Pattern**
```csharp
// Default timeout might be infinite
await cmd.ExecuteNonQueryAsync();
```

**Good Pattern**
```csharp
cmd.CommandTimeout = 30; // Seconds
await cmd.ExecuteNonQueryAsync();
```

---

## CS-DATA-009 — Connection Resilience
**Severity: Major**

**Rule**
Enable Retry Policies (Resiliency) for transient failures.

**Bad Pattern**
```csharp
services.AddDbContext<AppDbContext>();
```

**Good Pattern**
```csharp
services.AddDbContext<AppDbContext>(options =>
    options.UseSqlServer(conn, o => o.EnableRetryOnFailure()));
```

---

## CS-DATA-010 — Index Awareness
**Severity: Warning**

**Rule**
Queries on large tables MUST use indexed columns.

**Bad Pattern**
```csharp
// 'Bio' is nvarchar(max) and unindexed
var u = await _users.FirstAsync(u => u.Bio.Contains("Admin"));
```

**Good Pattern**
```csharp
// 'Email' is indexed
var u = await _users.FirstAsync(u => u.Email == "admin@corp.com");
```

---

## CS-DATA-011 — Bulk Operations
**Severity: Major**

**Rule**
Batch inserts/updates MUST use bulk methods for operations exceeding 100 records.

**Bad Pattern**
```csharp
foreach (var item in items) {
    _context.Items.Add(item);
    await _context.SaveChangesAsync(); // N round trips!
}
```

**Good Pattern**
```csharp
// Option 1: Batch with single SaveChanges
_context.Items.AddRange(items);
await _context.SaveChangesAsync();

// Option 2: Use bulk extensions for very large sets
await _context.BulkInsertAsync(items); // EFCore.BulkExtensions
```

---

## CS-DATA-012 — Soft Delete Pattern
**Severity: Major**

**Rule**
Soft deletes MUST use global query filters. Direct deletion of soft-delete entities is forbidden.

**Bad Pattern**
```csharp
// Manual filtering everywhere - easy to forget
var users = await _context.Users.Where(u => !u.IsDeleted).ToListAsync();

// Hard delete on soft-delete entity
_context.Users.Remove(user);
```

**Good Pattern**
```csharp
// In DbContext configuration
modelBuilder.Entity<User>().HasQueryFilter(u => !u.IsDeleted);

// Soft delete implementation
public async Task DeleteAsync(User user) {
    user.IsDeleted = true;
    user.DeletedAt = DateTime.UtcNow;
    await _context.SaveChangesAsync();
}

// To include deleted: _context.Users.IgnoreQueryFilters()
```

---

## CS-DATA-013 — Audit Columns
**Severity: Major**

**Rule**
Entities MUST have audit columns (CreatedAt, UpdatedAt, CreatedBy) populated automatically.

**Bad Pattern**
```csharp
// Manual audit - inconsistent and easy to forget
user.CreatedAt = DateTime.UtcNow;
user.CreatedBy = currentUser;
_context.Users.Add(user);
```

**Good Pattern**
```csharp
// SaveChanges interceptor
public override Task<int> SaveChangesAsync(CancellationToken ct = default) {
    foreach (var entry in ChangeTracker.Entries<IAuditable>()) {
        if (entry.State == EntityState.Added) {
            entry.Entity.CreatedAt = DateTime.UtcNow;
            entry.Entity.CreatedBy = _currentUser.Id;
        }
        entry.Entity.UpdatedAt = DateTime.UtcNow;
    }
    return base.SaveChangesAsync(ct);
}
```

---

## CS-DATA-014 — Connection Pool Sizing
**Severity: Major**

**Rule**
Connection pool size MUST be explicitly configured based on expected concurrency.

**Bad Pattern**
```csharp
// Default pool size may be too small for high-traffic apps
var conn = "Server=db;Database=app;";
```

**Good Pattern**
```csharp
// Explicitly size pool based on workload
var conn = "Server=db;Database=app;Max Pool Size=100;Min Pool Size=10;";

// Monitor pool exhaustion
builder.Services.AddHealthChecks()
    .AddSqlServer(conn, name: "database");
```

---

## CS-DATA-015 — DTO Record Types
**Severity: Major**

**Rule**
DTOs MUST be immutable records with `required` properties or primary constructors.

**Rationale**
Records provide value equality, immutability, and concise syntax. Required properties ensure complete initialization.

**Bad Pattern**
```csharp
public class UserDto
{
    public int Id { get; set; }
    public string Name { get; set; }  // Nullable warning, mutable
}
```

**Good Pattern**
```csharp
public record UserDto
{
    public required int Id { get; init; }
    public required string Name { get; init; }
}

// Or with primary constructor
public record UserDto(int Id, string Name);

// Or with optional properties
public record UserDto
{
    public required int Id { get; init; }
    public required string Name { get; init; }
    public string? Email { get; init; }  // Explicitly optional
}
```

---

## CS-DATA-016 — DTO Organization in Contracts
**Severity: Major**

**Rule**
DTOs MUST be organized in `Dto/` folder with subdirectories by category.

**Bad Pattern**
```
Domain.Contracts/
├── UserDto.cs
├── OrderDto.cs
├── PageDto.cs
├── MediaDto.cs
├── UserValidator.cs
└── OrderValidator.cs
```

**Good Pattern**
```
Domain.Contracts/
├── Dto/
│   ├── Core/
│   │   └── BaseDto.cs
│   ├── Users/
│   │   ├── UserDto.cs
│   │   └── UserProfileDto.cs
│   ├── Orders/
│   │   ├── OrderDto.cs
│   │   └── OrderLineDto.cs
│   ├── Content/
│   │   ├── PageDto.cs
│   │   └── MediaDto.cs
│   └── Enums/
│       └── OrderStatus.cs
└── Validators/
    ├── UserDtoValidator.cs
    └── OrderDtoValidator.cs
```

---

## CS-DATA-017 — Generic Response Wrapper
**Severity: Info**

**Rule**
List endpoints SHOULD use a generic response wrapper with items and total count.

**Rationale**
Consistent response structure enables client-side pagination handling and generic UI components.

**Bad Pattern**
```csharp
// Inconsistent return types
public async Task<List<UserDto>> GetUsersAsync() => ...
public async Task<UserDto[]> GetOrdersAsync() => ...
public async Task<IEnumerable<PageDto>> GetPagesAsync() => ...
```

**Good Pattern**
```csharp
public record QueryResponse<T>
{
    public required IReadOnlyList<T> Items { get; init; }
    public required int Total { get; init; }
}

// Usage
public async Task<QueryResponse<UserDto>> GetUsersAsync(int page, int size, CancellationToken ct)
{
    var items = await _db.Users
        .Skip((page - 1) * size)
        .Take(size)
        .Select(u => u.ToDto())
        .ToListAsync(ct);

    var total = await _db.Users.CountAsync(ct);

    return new QueryResponse<UserDto> { Items = items, Total = total };
}
```