# Distributed Systems Rules

## Purpose

Standards for building resilient distributed systems including circuit breakers, retry policies, idempotency, and event-driven patterns.

## Authority

Governs all distributed system components. Resilience patterns are mandatory for external service calls.

## Scope

Applies to HTTP clients, message queues, distributed caching, and cross-service communication.

---

## CS-DIST-001 — Circuit Breaker Pattern

**Severity: Critical**

**Rule**
All external service calls MUST use circuit breaker pattern to prevent cascade failures.

**Bad Pattern**
```csharp
public async Task<Data> GetDataAsync()
{
    return await _httpClient.GetFromJsonAsync<Data>("/api/data");
    // No protection - failures cascade
}
```

**Good Pattern**
```csharp
builder.Services.AddHttpClient<IDataClient, DataClient>()
    .AddResilienceHandler("data-pipeline", builder =>
    {
        builder.AddCircuitBreaker(new CircuitBreakerStrategyOptions<HttpResponseMessage>
        {
            FailureRatio = 0.5,
            SamplingDuration = TimeSpan.FromSeconds(30),
            MinimumThroughput = 10,
            BreakDuration = TimeSpan.FromSeconds(30),
            ShouldHandle = new PredicateBuilder<HttpResponseMessage>()
                .Handle<HttpRequestException>()
                .HandleResult(r => r.StatusCode >= HttpStatusCode.InternalServerError)
        });
    });
```

**Rationale**
Circuit breakers prevent overwhelming failing services and allow recovery time.

---

## CS-DIST-002 — Retry with Exponential Backoff

**Severity: Critical**

**Rule**
Transient failures MUST use retry with exponential backoff and jitter.

**Bad Pattern**
```csharp
for (int i = 0; i < 3; i++)
{
    try { return await CallService(); }
    catch { await Task.Delay(1000); } // Fixed delay
}
```

**Good Pattern**
```csharp
builder.Services.AddHttpClient<IOrderClient, OrderClient>()
    .AddResilienceHandler("order-retry", builder =>
    {
        builder.AddRetry(new RetryStrategyOptions<HttpResponseMessage>
        {
            MaxRetryAttempts = 3,
            Delay = TimeSpan.FromMilliseconds(500),
            BackoffType = DelayBackoffType.Exponential,
            UseJitter = true,
            ShouldHandle = new PredicateBuilder<HttpResponseMessage>()
                .Handle<HttpRequestException>()
                .Handle<TimeoutException>()
                .HandleResult(r => r.StatusCode == HttpStatusCode.TooManyRequests)
        });
    });
```

**Rationale**
Exponential backoff with jitter prevents thundering herd and allows services to recover.

---

## CS-DIST-003 — Timeout Policies

**Severity: Critical**

**Rule**
All external calls MUST have explicit timeouts. Never wait indefinitely.

**Bad Pattern**
```csharp
var response = await _httpClient.GetAsync("/api/data");
// No timeout - can hang forever
```

**Good Pattern**
```csharp
builder.Services.AddHttpClient<IDataClient, DataClient>()
    .AddResilienceHandler("data-timeout", builder =>
    {
        builder.AddTimeout(new TimeoutStrategyOptions
        {
            Timeout = TimeSpan.FromSeconds(10),
            OnTimeout = args =>
            {
                _logger.LogWarning("Request timed out after {Timeout}s",
                    args.Timeout.TotalSeconds);
                return default;
            }
        });
    });

// Or per-request with CancellationToken
using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(10));
var response = await _httpClient.GetAsync("/api/data", cts.Token);
```

**Rationale**
Timeouts prevent resource exhaustion and provide predictable failure modes.

---

## CS-DIST-004 — Bulkhead Isolation

**Severity: Major**

**Rule**
Critical paths SHOULD use bulkhead isolation to prevent resource starvation.

**Bad Pattern**
```csharp
// All requests share same resources - one slow service affects all
public async Task<IEnumerable<Order>> GetOrdersAsync() => await _orderClient.GetAsync();
public async Task<IEnumerable<Product>> GetProductsAsync() => await _productClient.GetAsync();
```

**Good Pattern**
```csharp
builder.Services.AddHttpClient<IOrderClient, OrderClient>()
    .AddResilienceHandler("order-bulkhead", builder =>
    {
        builder.AddConcurrencyLimiter(new ConcurrencyLimiterOptions
        {
            PermitLimit = 10,
            QueueLimit = 20
        });
    });

builder.Services.AddHttpClient<IProductClient, ProductClient>()
    .AddResilienceHandler("product-bulkhead", builder =>
    {
        builder.AddConcurrencyLimiter(new ConcurrencyLimiterOptions
        {
            PermitLimit = 25,
            QueueLimit = 50
        });
    });
```

**Rationale**
Bulkheads isolate resources so failures in one component don't exhaust shared resources.

---

## CS-DIST-005 — Idempotency Keys

**Severity: Critical**

**Rule**
All mutating operations MUST support idempotency keys for safe retries.

**Bad Pattern**
```csharp
[HttpPost("orders")]
public async Task<IActionResult> CreateOrder([FromBody] CreateOrderRequest request)
{
    var order = await _orderService.CreateAsync(request);
    return Created($"/orders/{order.Id}", order);
    // Retry creates duplicate orders
}
```

**Good Pattern**
```csharp
[HttpPost("orders")]
public async Task<IActionResult> CreateOrder(
    [FromHeader(Name = "Idempotency-Key")] string idempotencyKey,
    [FromBody] CreateOrderRequest request)
{
    // Check for existing operation with this key
    var existing = await _idempotencyStore.GetAsync(idempotencyKey);
    if (existing is not null)
        return existing.ToActionResult();

    var order = await _orderService.CreateAsync(request);
    var result = Created($"/orders/{order.Id}", order);

    // Store result for future requests with same key
    await _idempotencyStore.SetAsync(idempotencyKey, result, TimeSpan.FromHours(24));

    return result;
}
```

**Rationale**
Idempotency keys enable safe retries without duplicate side effects.

---

## CS-DIST-006 — Correlation ID Propagation

**Severity: Critical**

**Rule**
All requests MUST propagate correlation IDs across service boundaries.

**Bad Pattern**
```csharp
public async Task<Order> ProcessOrderAsync(OrderRequest request)
{
    await _inventoryClient.ReserveAsync(request.Items);
    await _paymentClient.ChargeAsync(request.Amount);
    // No correlation - can't trace across services
}
```

**Good Pattern**
```csharp
public class CorrelationHandler : DelegatingHandler
{
    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request,
        CancellationToken ct)
    {
        var activity = Activity.Current;
        if (activity is not null)
        {
            request.Headers.TryAddWithoutValidation(
                "X-Correlation-Id", activity.TraceId.ToString());
            request.Headers.TryAddWithoutValidation(
                "X-Request-Id", activity.SpanId.ToString());
        }
        return await base.SendAsync(request, ct);
    }
}

// Middleware to extract/create correlation ID
app.Use(async (context, next) =>
{
    var correlationId = context.Request.Headers["X-Correlation-Id"].FirstOrDefault()
        ?? Activity.Current?.TraceId.ToString()
        ?? Guid.NewGuid().ToString();

    using (logger.BeginScope(new Dictionary<string, object>
    {
        ["CorrelationId"] = correlationId
    }))
    {
        context.Response.Headers["X-Correlation-Id"] = correlationId;
        await next();
    }
});
```

**Rationale**
Correlation IDs enable distributed tracing and debugging across service boundaries.

---

## CS-DIST-007 — Outbox Pattern

**Severity: Major**

**Rule**
Event publishing with database updates MUST use the outbox pattern for reliability.

**Bad Pattern**
```csharp
public async Task CreateOrderAsync(Order order)
{
    await _dbContext.Orders.AddAsync(order);
    await _dbContext.SaveChangesAsync();
    await _eventBus.PublishAsync(new OrderCreatedEvent(order.Id));
    // If publish fails, database has order but event is lost
}
```

**Good Pattern**
```csharp
public async Task CreateOrderAsync(Order order)
{
    await using var transaction = await _dbContext.Database.BeginTransactionAsync();

    await _dbContext.Orders.AddAsync(order);

    // Store event in outbox table (same transaction)
    await _dbContext.OutboxMessages.AddAsync(new OutboxMessage
    {
        Id = Guid.NewGuid(),
        Type = nameof(OrderCreatedEvent),
        Payload = JsonSerializer.Serialize(new OrderCreatedEvent(order.Id)),
        CreatedAt = _timeProvider.GetUtcNow()
    });

    await _dbContext.SaveChangesAsync();
    await transaction.CommitAsync();
}

// Background service processes outbox
public class OutboxProcessor(IDbContext db, IEventBus bus) : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken ct)
    {
        while (!ct.IsCancellationRequested)
        {
            var messages = await db.OutboxMessages
                .Where(m => m.ProcessedAt == null)
                .OrderBy(m => m.CreatedAt)
                .Take(100)
                .ToListAsync(ct);

            foreach (var message in messages)
            {
                await bus.PublishAsync(message.Type, message.Payload, ct);
                message.ProcessedAt = _timeProvider.GetUtcNow();
            }

            await db.SaveChangesAsync(ct);
            await Task.Delay(TimeSpan.FromSeconds(1), ct);
        }
    }
}
```

**Rationale**
Outbox pattern ensures atomic database + event publishing with guaranteed delivery.

---

## CS-DIST-008 — Distributed Locks

**Severity: Major**

**Rule**
Distributed operations requiring coordination MUST use distributed locks with TTL.

**Bad Pattern**
```csharp
// In-memory lock doesn't work across instances
private static readonly SemaphoreSlim _lock = new(1, 1);

public async Task ProcessAsync()
{
    await _lock.WaitAsync();
    try { /* process */ }
    finally { _lock.Release(); }
}
```

**Good Pattern**
```csharp
public interface IDistributedLock
{
    Task<IAsyncDisposable?> TryAcquireAsync(
        string resource,
        TimeSpan expiry,
        CancellationToken ct = default);
}

public class RedisDistributedLock(IDatabase redis) : IDistributedLock
{
    public async Task<IAsyncDisposable?> TryAcquireAsync(
        string resource,
        TimeSpan expiry,
        CancellationToken ct)
    {
        var lockId = Guid.NewGuid().ToString();
        var acquired = await redis.StringSetAsync(
            $"lock:{resource}",
            lockId,
            expiry,
            When.NotExists);

        return acquired
            ? new LockHandle(redis, resource, lockId)
            : null;
    }
}

// Usage
await using var lockHandle = await _lock.TryAcquireAsync(
    $"order:{orderId}",
    TimeSpan.FromSeconds(30),
    ct);

if (lockHandle is null)
    return Results.Conflict("Order is being processed");

await ProcessOrderAsync(orderId);
```

**Rationale**
Distributed locks prevent concurrent modifications across multiple service instances.

---

## CS-DIST-009 — Event-Driven Architecture

**Severity: Major**

**Rule**
Cross-service communication SHOULD prefer events over synchronous calls.

**Bad Pattern**
```csharp
// Synchronous chain - tight coupling, cascade failures
public async Task CreateOrderAsync(Order order)
{
    await _inventoryService.ReserveAsync(order.Items);
    await _paymentService.ChargeAsync(order.Amount);
    await _shippingService.ScheduleAsync(order.Address);
    await _notificationService.SendAsync(order.Customer);
}
```

**Good Pattern**
```csharp
public async Task CreateOrderAsync(Order order)
{
    order.Status = OrderStatus.Created;
    await _dbContext.SaveChangesAsync();

    // Publish event - other services react asynchronously
    await _eventBus.PublishAsync(new OrderCreatedEvent
    {
        OrderId = order.Id,
        Items = order.Items,
        CustomerId = order.CustomerId,
        Amount = order.Amount
    });
}

// Inventory service handles event
public class InventoryEventHandler : IEventHandler<OrderCreatedEvent>
{
    public async Task HandleAsync(OrderCreatedEvent @event)
    {
        await _inventoryService.ReserveAsync(@event.Items);
        await _eventBus.PublishAsync(new InventoryReservedEvent(@event.OrderId));
    }
}
```

**Rationale**
Event-driven architecture provides loose coupling, better resilience, and scalability.

---

## CS-DIST-010 — Saga Pattern

**Severity: Major**

**Rule**
Multi-step distributed transactions SHOULD use saga pattern with compensation.

**Bad Pattern**
```csharp
// No compensation - partial failures leave inconsistent state
public async Task ProcessOrderAsync(Order order)
{
    await _inventoryService.ReserveAsync(order.Items);
    await _paymentService.ChargeAsync(order.Amount); // If this fails...
    await _shippingService.ScheduleAsync(order.Address);
    // Inventory is reserved but payment failed
}
```

**Good Pattern**
```csharp
public class OrderSaga : ISaga<OrderSagaData>
{
    public void ConfigureSteps(ISagaBuilder<OrderSagaData> builder)
    {
        builder
            .Step("Reserve Inventory")
            .Execute(async (data, ctx) =>
            {
                data.ReservationId = await _inventory.ReserveAsync(data.Items, ctx.Token);
            })
            .Compensate(async (data, ctx) =>
            {
                await _inventory.ReleaseAsync(data.ReservationId, ctx.Token);
            });

        builder
            .Step("Charge Payment")
            .Execute(async (data, ctx) =>
            {
                data.PaymentId = await _payment.ChargeAsync(data.Amount, ctx.Token);
            })
            .Compensate(async (data, ctx) =>
            {
                await _payment.RefundAsync(data.PaymentId, ctx.Token);
            });

        builder
            .Step("Schedule Shipping")
            .Execute(async (data, ctx) =>
            {
                data.ShipmentId = await _shipping.ScheduleAsync(data.Address, ctx.Token);
            })
            .Compensate(async (data, ctx) =>
            {
                await _shipping.CancelAsync(data.ShipmentId, ctx.Token);
            });
    }
}
```

**Rationale**
Saga pattern maintains consistency across distributed transactions with automatic rollback.

---

## CS-DIST-011 — Health Checks for Dependencies

**Severity: Critical**

**Rule**
All external dependencies MUST have health checks exposed via /health endpoints.

**Bad Pattern**
```csharp
app.MapHealthChecks("/health");
// Only checks if app is running, not dependencies
```

**Good Pattern**
```csharp
builder.Services.AddHealthChecks()
    .AddCheck("self", () => HealthCheckResult.Healthy(), tags: ["live"])
    .AddSqlServer(connectionString, name: "database", tags: ["ready"])
    .AddRedis(redisConnection, name: "cache", tags: ["ready"])
    .AddRabbitMQ(rabbitConnection, name: "messaging", tags: ["ready"])
    .AddUrlGroup(new Uri("https://api.payment.com/health"),
        name: "payment-api", tags: ["ready"]);

app.MapHealthChecks("/health/live", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("live")
});

app.MapHealthChecks("/health/ready", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("ready"),
    ResponseWriter = UIResponseWriter.WriteHealthCheckUIResponse
});
```

**Rationale**
Dependency health checks enable proper orchestration and traffic management.

---

## CS-DIST-012 — Service Discovery

**Severity: Info**

**Rule**
Microservices SHOULD use service discovery instead of hardcoded URLs.

**Bad Pattern**
```csharp
builder.Services.AddHttpClient<IOrderClient>(client =>
{
    client.BaseAddress = new Uri("http://order-service:8080");
    // Hardcoded - doesn't adapt to scaling/deployment changes
});
```

**Good Pattern**
```csharp
// Using service discovery (e.g., Consul, Kubernetes DNS)
builder.Services.AddServiceDiscovery();

builder.Services.AddHttpClient<IOrderClient>()
    .AddServiceDiscovery();

// Configuration
{
    "Services": {
        "order-service": {
            "http": ["order-service.default.svc.cluster.local"]
        }
    }
}
```

**Rationale**
Service discovery enables dynamic scaling and failover without configuration changes.

---

## Forbidden Patterns

- CS-DIST-FORBID-001: No external calls without timeout
- CS-DIST-FORBID-002: No retry without backoff
- CS-DIST-FORBID-003: No mutating operations without idempotency support
- CS-DIST-FORBID-004: No cross-service calls without correlation ID
- CS-DIST-FORBID-005: No database + event publish without outbox/transactional outbox
- CS-DIST-FORBID-006: No in-memory locks in distributed systems
- CS-DIST-FORBID-007: No synchronous chains across more than 2 services
- CS-DIST-FORBID-008: No hardcoded service URLs in production
- CS-DIST-FORBID-009: No missing health checks for external dependencies
- CS-DIST-FORBID-010: No distributed transactions without compensation logic
