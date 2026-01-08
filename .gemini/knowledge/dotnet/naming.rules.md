# .NET Naming Conventions Rules

## Purpose

Standards for consistent naming across namespaces, classes, methods, properties, fields, and all code elements.

## Authority

Governs all `.cs` files. Consistent naming is mandatory.

## Scope

Applies to all identifier naming in C# code.

---

## CS-NAME-001 — Namespace Naming

**Severity: Major**

**Rule**
Namespaces MUST use PascalCase and follow `Company.Product.Feature` pattern.

**Bad Pattern**
```csharp
namespace myApp.services.orders; // lowercase
namespace MyApp_Services_Orders; // underscores
```

**Good Pattern**
```csharp
namespace MyCompany.OrderSystem.Orders;
namespace MyCompany.OrderSystem.Orders.Handlers;
```

**Rationale**
Consistent namespace naming enables predictable code organization and discovery.

---

## CS-NAME-002 — Class and Struct Naming

**Severity: Major**

**Rule**
Classes and structs MUST use PascalCase noun phrases describing their responsibility.

**Bad Pattern**
```csharp
public class orderProcessor { } // camelCase
public class ProcessOrders { } // verb phrase
public class OrderHelper { } // vague
```

**Good Pattern**
```csharp
public class OrderProcessor { }
public class CustomerValidator { }
public class PaymentGateway { }
```

**Rationale**
Clear class names communicate purpose at a glance.

---

## CS-NAME-003 — Interface Naming

**Severity: Critical**

**Rule**
Interfaces MUST prefix with `I` and use capability-focused names.

**Bad Pattern**
```csharp
public interface PaymentProcessor { } // Missing I prefix
public interface IStripePaymentImplementation { } // Implementation detail
```

**Good Pattern**
```csharp
public interface IPaymentProcessor { }
public interface IOrderRepository { }
public interface INotificationService { }
```

**Rationale**
I-prefix instantly identifies interfaces. Capability focus enables multiple implementations.

---

## CS-NAME-004 — Method Naming

**Severity: Major**

**Rule**
Methods MUST use PascalCase verb phrases describing the action.

**Bad Pattern**
```csharp
public void orderProcess() { } // camelCase
public void Order() { } // noun only
public void DoIt() { } // vague
```

**Good Pattern**
```csharp
public void ProcessOrder() { }
public Order CreateOrder() { }
public bool ValidateCustomer() { }
public async Task<Order> GetOrderByIdAsync() { }
```

**Rationale**
Verb phrases clearly communicate method behavior.

---

## CS-NAME-005 — Async Method Suffix

**Severity: Critical**

**Rule**
All async methods MUST end with `Async` suffix. No exceptions.

**Bad Pattern**
```csharp
public async Task<Order> GetOrder(int id) { } // Missing Async
public async Task ProcessPayment() { } // Missing Async
```

**Good Pattern**
```csharp
public async Task<Order> GetOrderAsync(int id) { }
public async Task ProcessPaymentAsync() { }
public async ValueTask<bool> ValidateAsync() { }
```

**Rationale**
Async suffix prevents accidental blocking calls and signals async behavior.

---

## CS-NAME-006 — Property Naming

**Severity: Major**

**Rule**
Properties MUST use PascalCase nouns or adjectives. No `Get` prefix.

**Bad Pattern**
```csharp
public string firstName { get; set; } // camelCase
public string GetName { get; } // Get prefix
public List<Order> order { get; } // singular for collection
```

**Good Pattern**
```csharp
public string FirstName { get; set; }
public string Name { get; }
public List<Order> Orders { get; } // plural for collection
public bool IsActive { get; }
public int TotalAmount { get; }
```

**Rationale**
Property names should read naturally when accessed.

---

## CS-NAME-007 — Boolean Naming

**Severity: Major**

**Rule**
Boolean properties and variables MUST use `Is`, `Has`, `Can`, `Should`, or `Was` prefix.

**Bad Pattern**
```csharp
public bool Active { get; set; }
public bool Enabled { get; set; }
public bool Valid { get; set; }
```

**Good Pattern**
```csharp
public bool IsActive { get; set; }
public bool IsEnabled { get; set; }
public bool IsValid { get; set; }
public bool HasPermission { get; set; }
public bool CanExecute { get; set; }
public bool ShouldRetry { get; set; }
```

**Rationale**
Prefixes make boolean intent clear and code more readable.

---

## CS-NAME-008 — Private Field Naming

**Severity: Major**

**Rule**
Private fields MUST use `_camelCase` with underscore prefix.

**Bad Pattern**
```csharp
private readonly ILogger logger; // no prefix
private readonly ILogger _Logger; // PascalCase
private readonly ILogger m_logger; // Hungarian
```

**Good Pattern**
```csharp
private readonly ILogger _logger;
private readonly IDbContext _dbContext;
private int _retryCount;
```

**Rationale**
Underscore prefix distinguishes fields from parameters and locals.

---

## CS-NAME-009 — Constant Naming

**Severity: Major**

**Rule**
Public constants MUST use PascalCase. Private constants MAY use UPPER_SNAKE_CASE.

**Bad Pattern**
```csharp
public const int max_retries = 3; // snake_case
public const int MAXRETRIES = 3; // no separation
```

**Good Pattern**
```csharp
public const int MaxRetries = 3;
public const string DefaultConnectionString = "...";

private const int _MAX_BUFFER_SIZE = 4096;
private const string _DEFAULT_ENCODING = "UTF-8";
```

**Rationale**
Public constants follow .NET conventions. Private constants can use traditional constant style.

---

## CS-NAME-010 — Parameter and Local Variable Naming

**Severity: Major**

**Rule**
Parameters and locals MUST use camelCase. No abbreviations except universally known ones.

**Bad Pattern**
```csharp
public void Process(int OrderId, string CustName) { } // PascalCase
public void Process(int oid, string cn) { } // abbreviations
```

**Good Pattern**
```csharp
public void Process(int orderId, string customerName) { }
public void Calculate(decimal amount, int quantity) { }

// Acceptable abbreviations
public void Configure(int id, string url, HttpClient http) { }
```

**Rationale**
Descriptive names eliminate guesswork about parameter purpose.

---

## CS-NAME-011 — Generic Type Parameter Naming

**Severity: Info**

**Rule**
Generic type parameters MUST use `T` prefix with descriptive suffix for complex scenarios.

**Bad Pattern**
```csharp
public class Repository<Entity> { } // no T prefix
public class Cache<K, V> { } // single letters for multiple params
```

**Good Pattern**
```csharp
public class Repository<T> { }
public class Repository<TEntity> where TEntity : class { }
public class Cache<TKey, TValue> { }
public interface IHandler<TRequest, TResponse> { }
```

**Rationale**
T-prefix identifies type parameters. Descriptive names clarify purpose.

---

## CS-NAME-012 — Enum Naming

**Severity: Major**

**Rule**
Enums MUST use PascalCase singular names. Values MUST use PascalCase.

**Bad Pattern**
```csharp
public enum OrderStatuses { PENDING, IN_PROGRESS } // plural, UPPER_CASE
public enum orderStatus { pending, inProgress } // camelCase
```

**Good Pattern**
```csharp
public enum OrderStatus
{
    Pending,
    InProgress,
    Completed,
    Cancelled
}

[Flags]
public enum FilePermissions // Flags are plural
{
    None = 0,
    Read = 1,
    Write = 2,
    Execute = 4
}
```

**Rationale**
Singular enum names read naturally. Flags use plural to indicate combinability.

---

## CS-NAME-013 — Event Naming

**Severity: Major**

**Rule**
Events MUST use PascalCase past tense for completed actions, present for in-progress.

**Bad Pattern**
```csharp
public event EventHandler OrderCreate; // present tense for completed
public event EventHandler OnOrderCreated; // On prefix (old style)
```

**Good Pattern**
```csharp
public event EventHandler<OrderEventArgs> OrderCreated;
public event EventHandler<OrderEventArgs> OrderCreating;
public event EventHandler PaymentProcessed;
```

**Rationale**
Tense indicates whether event fires before or after action.

---

## CS-NAME-014 — Extension Method Class Naming

**Severity: Info**

**Rule**
Extension method classes MUST use `{Type}Extensions` naming pattern.

**Bad Pattern**
```csharp
public static class Helpers { } // vague
public static class StringUtils { } // Utils suffix
```

**Good Pattern**
```csharp
public static class StringExtensions { }
public static class EnumerableExtensions { }
public static class HttpClientExtensions { }
```

**Rationale**
Consistent naming makes extension methods discoverable.

---

## CS-NAME-015 — Test Method Naming

**Severity: Major**

**Rule**
Test methods MUST follow `Method_Scenario_ExpectedResult` pattern.

**Bad Pattern**
```csharp
[Fact]
public void Test1() { }

[Fact]
public void OrderTest() { }
```

**Good Pattern**
```csharp
[Fact]
public void CreateOrder_ValidInput_ReturnsOrder() { }

[Fact]
public void CreateOrder_NullCustomer_ThrowsArgumentNullException() { }

[Fact]
public void ProcessPayment_InsufficientFunds_ReturnsDeclined() { }
```

**Rationale**
Descriptive test names serve as documentation and failure context.

---

## CS-NAME-016 — Record Naming

**Severity: Major**

**Rule**
Records MUST use PascalCase with appropriate suffixes for purpose.

**Bad Pattern**
```csharp
public record orderDto(string Name); // camelCase
public record OrderData(string Name); // vague suffix
```

**Good Pattern**
```csharp
public record OrderDto(string Id, string CustomerName);
public record CreateOrderRequest(string CustomerId, List<OrderItem> Items);
public record OrderCreatedEvent(string OrderId, DateTime CreatedAt);
public record OrderSummary(string Id, decimal Total);
```

**Rationale**
Suffixes clarify record purpose (DTO, Request, Response, Event, Summary).

---

## Forbidden Patterns

- CS-NAME-FORBID-001: No Hungarian notation (strName, intCount)
- CS-NAME-FORBID-002: No single-letter names except loop counters and lambdas
- CS-NAME-FORBID-003: No abbreviations unless universally known (Id, Url, Http, Xml, Json)
- CS-NAME-FORBID-004: No `Get` prefix on properties
- CS-NAME-FORBID-005: No underscores in public identifiers
- CS-NAME-FORBID-006: No inconsistent casing within project
- CS-NAME-FORBID-007: No generic names without context (Manager, Handler, Helper, Utils)
- CS-NAME-FORBID-008: No async methods without Async suffix
- CS-NAME-FORBID-009: No bool properties without Is/Has/Can/Should prefix
- CS-NAME-FORBID-010: No numbered suffixes (Handler1, Handler2)
