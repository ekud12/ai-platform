# .NET Messaging Rules

## Purpose

Standards for message-based communication using NATS, Service Bus, or other message brokers.

## Authority

Governs all async messaging and job systems.

## Scope

Applies to all message queue, pub/sub, and background job implementations.

## Constraints

- Messaging must be abstracted from broker implementations
- Handlers must be idempotent
- Messages must be traceable

## Rule Format

All rules use the CS-MSG prefix.

---

## CS-MSG-001 — Messaging Abstraction Layer
**Severity: Critical**

**Rule**
Messaging MUST use abstractions (`IMessageSender`, `IMessageHandler`) not direct broker clients.

**Rationale**
Abstraction enables switching between NATS, Service Bus, RabbitMQ without changing business logic.

**Bad Pattern**
```csharp
public class OrderService
{
    private readonly NatsConnection _nats;

    public async Task PlaceOrder(Order order)
    {
        await _nats.PublishAsync("orders.placed", order);
    }
}
```

**Good Pattern**
```csharp
public interface IMessageSender
{
    Task SendToQueueAsync<T>(string queue, T message, CancellationToken ct);
    Task PublishToTopicAsync<T>(string topic, T message, CancellationToken ct);
}

public class OrderService(IMessageSender sender)
{
    public async Task PlaceOrder(Order order, CancellationToken ct)
    {
        await sender.PublishToTopicAsync("orders.placed", order, ct);
    }
}
```

---

## CS-MSG-002 — Message Handler Interface
**Severity: Major**

**Rule**
Message handlers MUST implement `IMessageHandler<T>` for automatic discovery and registration.

**Bad Pattern**
```csharp
public class OrderHandler
{
    public void Handle(OrderEvent e) { ... } // No interface, not discoverable
}
```

**Good Pattern**
```csharp
public interface IMessageHandler<T> where T : class
{
    Task HandleAsync(T message, CancellationToken ct);
}

public class OrderPlacedHandler : IMessageHandler<OrderPlacedEvent>
{
    public async Task HandleAsync(OrderPlacedEvent message, CancellationToken ct)
    {
        // Handle the message
    }
}

// Registration via assembly scanning
services.AddMessageHandlers(typeof(OrderPlacedHandler).Assembly);
```

---

## CS-MSG-003 — Dual Messaging Support
**Severity: Info**

**Rule**
Enterprise solutions SHOULD support multiple messaging backends via configuration.

**Rationale**
Enables local development with NATS while using Azure Service Bus in production.

**Good Pattern**
```json
// appsettings.json
{
  "Messaging": {
    "Provider": "Nats"
  }
}

// appsettings.Production.json
{
  "Messaging": {
    "Provider": "ServiceBus"
  }
}
```

```csharp
// Registration chooses implementation based on config
services.AddMessaging(config);
```

---

## CS-MSG-004 — Job SDK Abstraction
**Severity: Major**

**Rule**
Background jobs MUST use a job SDK with `IJob`, `IJobHandler`, `IJobResult` abstractions.

**Bad Pattern**
```csharp
// Direct NATS job handling mixed with business logic
await _nats.SubscribeAsync("jobs.sync", async msg =>
{
    var data = JsonSerializer.Deserialize<SyncData>(msg.Data);
    await SyncAsync(data);
    await msg.AckAsync();
});
```

**Good Pattern**
```csharp
public interface IJob
{
    string JobId { get; }
    string JobType { get; }
}

public interface IJobHandler<T> where T : IJob
{
    Task<IJobResult> HandleAsync(T job, CancellationToken ct);
}

public interface IJobResult
{
    bool Success { get; }
    string? Error { get; }
}

public class SyncJob : IJob
{
    public required string JobId { get; init; }
    public string JobType => "sync";
    public required string EntityId { get; init; }
}

public class SyncJobHandler : IJobHandler<SyncJob>
{
    public async Task<IJobResult> HandleAsync(SyncJob job, CancellationToken ct)
    {
        // Handle job
        return JobResult.Success();
    }
}
```

---

## CS-MSG-005 — Message Idempotency
**Severity: Critical**

**Rule**
Message handlers MUST be idempotent. Use message ID for deduplication.

**Rationale**
Messages can be delivered multiple times (at-least-once delivery). Handlers must handle duplicates gracefully.

**Bad Pattern**
```csharp
public class PaymentHandler : IMessageHandler<PaymentEvent>
{
    public async Task HandleAsync(PaymentEvent msg, CancellationToken ct)
    {
        await _payments.ChargeAsync(msg.Amount); // Charged multiple times!
    }
}
```

**Good Pattern**
```csharp
public class PaymentHandler : IMessageHandler<PaymentEvent>
{
    private readonly IIdempotencyStore _store;

    public async Task HandleAsync(PaymentEvent msg, CancellationToken ct)
    {
        if (await _store.HasProcessedAsync(msg.MessageId, ct))
            return; // Already processed - skip

        await _payments.ChargeAsync(msg.Amount);
        await _store.MarkProcessedAsync(msg.MessageId, ct);
    }
}
```
