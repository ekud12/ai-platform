# .NET Memory Rules

## Purpose
Standards for memory allocation, disposal, and resource management in C#.

## Authority
Governs all memory-sensitive operations and `IDisposable` usage.

---

## CS-MEM-001 — Dispose Pattern
**Severity: Critical**

**Rule**
Classes with unmanaged resources MUST implement `IDisposable` correctly.

**Bad Pattern**
```csharp
public class Wrapper {
    private IntPtr _handle;
    // No Dispose method! Leak!
}
```

**Good Pattern**
```csharp
public class Wrapper : IDisposable {
    private bool _disposed;
    public void Dispose() { ... GC.SuppressFinalize(this); }
}
```

---

## CS-MEM-002 — Using Statement
**Severity: Critical**

**Rule**
Always use `using` statement/declaration for IDisposable.

**Bad Pattern**
```csharp
var stream = new FileStream("data.bin", FileMode.Open);
stream.Read(buffer); // If exception throws, stream is never closed
```

**Good Pattern**
```csharp
using var stream = new FileStream("data.bin", FileMode.Open);
stream.Read(buffer);
```

---

## CS-MEM-003 — Span for Buffer Operations
**Severity: Major**

**Rule**
Use `Span<T>` over array copies for buffers.

**Bad Pattern**
```csharp
byte[] slice = new byte[10];
Array.Copy(buffer, 0, slice, 0, 10); // Allocates
```

**Good Pattern**
```csharp
Span<byte> slice = buffer.AsSpan(0, 10); // No allocation
```

---

## CS-MEM-004 — MemoryPool for Large Buffers
**Severity: Major**

**Rule**
Buffers > 85kb MUST use `MemoryPool<T>` (avoid LOH).

**Bad Pattern**
```csharp
byte[] huge = new byte[100000]; // Goes to LOH (Slow GC)
```

**Good Pattern**
```csharp
using var owner = MemoryPool<byte>.Shared.Rent(100000);
var huge = owner.Memory;
```

---

## CS-MEM-005 — Stackalloc Limits
**Severity: Warning**

**Rule**
`stackalloc` MUST NOT exceed 1024 bytes (Stack Overflow risk).

**Bad Pattern**
```csharp
Span<byte> buffer = stackalloc byte[10000]; // Dangerous
```

**Good Pattern**
```csharp
Span<byte> buffer = stackalloc byte[512]; // Safe
```

---

## CS-MEM-006 — No Finalizers Without Necessity
**Severity: Info**

**Rule**
Do NOT add a destructor (`~Class()`) unless strictly wrapping unmanaged handles.

**Bad Pattern**
```csharp
public class Logger {
    ~Logger() { Flush(); } // Delays GC for no good reason
}
```

**Good Pattern**
```csharp
public class Logger : IDisposable {
    public void Dispose() { Flush(); }
}
```

---

## CS-MEM-007 — GC.SuppressFinalize
**Severity: Major**

**Rule**
If you have a finalizer, `Dispose()` MUST call `GC.SuppressFinalize(this)`.

**Bad Pattern**
```csharp
public void Dispose() { FreeNative(); } // GC still runs finalizer later
```

**Good Pattern**
```csharp
public void Dispose() { 
    FreeNative();
    GC.SuppressFinalize(this); 
}
```

---

## CS-MEM-008 — WeakReference for Caches
**Severity: Info**

**Rule**
Long-lived caches SHOULD use `WeakReference` to avoid memory leaks.

**Bad Pattern**
```csharp
static Dictionary<string, User> _cache; // Holds references forever
```

**Good Pattern**
```csharp
static Dictionary<string, WeakReference<User>> _cache;
```

---

## CS-MEM-009 — No Closure Allocations in Hot Paths
**Severity: Warning**

**Rule**
Lambdas in hot paths MUST NOT capture local variables (Allocates delegate + closure).

**Bad Pattern**
```csharp
int id = 5;
_cache.GetOrAdd(key, k => new Item(id)); // Captures 'id', allocates closure
```

**Good Pattern**
```csharp
int id = 5;
_cache.GetOrAdd(key, static (k, arg) => new Item(arg), id); // Static lambda, no allocation
```

---

## CS-MEM-010 — RecyclableMemoryStream
**Severity: Major**

**Rule**
High-throughput code MUST use `RecyclableMemoryStream` over `MemoryStream`.

**Bad Pattern**
```csharp
using var ms = new MemoryStream(); // Allocates buffer every request
```

**Good Pattern**
```csharp
using var ms = _manager.GetStream(); // Pools buffer
```

---

## CS-MEM-011 — Object Pooling
**Severity: Major**

**Rule**
Frequently allocated objects in hot paths SHOULD use `ObjectPool<T>`.

**Bad Pattern**
```csharp
// In request handler - allocates StringBuilder per request
var sb = new StringBuilder();
```

**Good Pattern**
```csharp
private readonly ObjectPool<StringBuilder> _pool =
    new DefaultObjectPoolProvider().CreateStringBuilderPool();

// In request handler
var sb = _pool.Get();
try {
    // use sb
} finally {
    _pool.Return(sb);
}
```

---

## CS-MEM-012 — Pinned Object Management
**Severity: Critical**

**Rule**
`GCHandle.Alloc` with Pinned MUST be released in finally block. Prefer `fixed` statement.

**Bad Pattern**
```csharp
var handle = GCHandle.Alloc(buffer, GCHandleType.Pinned);
NativeMethod(handle.AddrOfPinnedObject());
// If exception occurs, handle is never freed - memory leak!
```

**Good Pattern**
```csharp
// Option 1: fixed statement (preferred)
fixed (byte* ptr = buffer) {
    NativeMethod((IntPtr)ptr);
}

// Option 2: GCHandle with proper cleanup
var handle = GCHandle.Alloc(buffer, GCHandleType.Pinned);
try {
    NativeMethod(handle.AddrOfPinnedObject());
} finally {
    handle.Free();
}
```