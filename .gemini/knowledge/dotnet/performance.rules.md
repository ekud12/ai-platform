# .NET Performance Rules

## Purpose
Defines performance standards for hot paths and high-frequency code in C#.

## Authority
Applies to all code marked as "Hot Path" or latency-sensitive.

---

## CS-PERF-001 — Hot Path Allocation Budget
**Severity: Major**

**Rule**
Hot paths MUST NOT allocate more than 100 bytes per operation.

**Bad Pattern**
```csharp
// Inside a loop
var data = new List<int> { 1, 2, 3 }; // Allocates on heap
```

**Good Pattern**
```csharp
// Inside a loop
Span<int> data = stackalloc int[] { 1, 2, 3 }; // No heap allocation
```

---

## CS-PERF-002 — Struct for Small Value Types
**Severity: Info**

**Rule**
Types smaller than 16 bytes with value semantics MUST be `struct`.

**Bad Pattern**
```csharp
public class Point { public int X; public int Y; } // Heap allocation
```

**Good Pattern**
```csharp
public readonly struct Point { public int X { get; init; } public int Y { get; init; } }
```

---

## CS-PERF-003 — ArrayPool for Temporary Arrays
**Severity: Major**

**Rule**
Temporary arrays in hot paths MUST use `ArrayPool`.

**Bad Pattern**
```csharp
byte[] buffer = new byte[1024]; // Allocation pressure
Process(buffer);
```

**Good Pattern**
```csharp
var buffer = ArrayPool<byte>.Shared.Rent(1024);
try {
    Process(buffer);
} finally {
    ArrayPool<byte>.Shared.Return(buffer);
}
```

---

## CS-PERF-004 — StringBuilder for Loop Concatenation
**Severity: Major**

**Rule**
String concatenation in loops MUST use `StringBuilder`.

**Bad Pattern**
```csharp
string s = "";
foreach (var item in items) s += item; // O(N^2) allocations
```

**Good Pattern**
```csharp
var sb = new StringBuilder();
foreach (var item in items) sb.Append(item);
string s = sb.ToString();
```

---

## CS-PERF-005 — Avoid Boxing
**Severity: Critical**

**Rule**
Value types MUST NOT be boxed in hot paths.

**Bad Pattern**
```csharp
object obj = 42; // Boxing
```

**Good Pattern**
```csharp
int val = 42; // No boxing
```

---

## CS-PERF-006 — Sealed Classes
**Severity: Info**

**Rule**
Non-inherited classes MUST be `sealed` for devirtualization.

**Bad Pattern**
```csharp
public class Service { ... }
```

**Good Pattern**
```csharp
public sealed class Service { ... }
```

---

## CS-PERF-007 — Readonly Structs
**Severity: Info**

**Rule**
Immutable structs MUST be marked `readonly`.

**Bad Pattern**
```csharp
public struct Vector3 { public float X; ... }
```

**Good Pattern**
```csharp
public readonly struct Vector3 { public float X { get; init; } ... }
```

---

## CS-PERF-008 — Span for Slicing
**Severity: Major**

**Rule**
String/Array slicing MUST use `Span<T>` or `Memory<T>`.

**Bad Pattern**
```csharp
string sub = text.Substring(0, 5); // New string allocation
```

**Good Pattern**
```csharp
ReadOnlySpan<char> sub = text.AsSpan().Slice(0, 5); // Zero allocation
```

---

## CS-PERF-009 — Avoid In-Memory LINQ in Hot Paths
**Severity: Warning**

**Rule**
In-memory LINQ (LINQ-to-Objects) MUST NOT be used in critical hot paths. Use explicit loops instead.

**Scope**
This rule applies to in-memory collections only. EF Core LINQ queries that translate to SQL are governed by CS-DATA-005 and are acceptable since execution happens on the database server.

**Related Rules**
- CS-DATA-005 covers EF/SQL projection queries (LINQ-to-Entities is allowed)

**Bad Pattern**
```csharp
// In tight loop over in-memory collection
return items.Where(x => x > 10).Sum(); // Allocates iterators
```

**Good Pattern**
```csharp
// In tight loop over in-memory collection
int sum = 0;
foreach(var x in items) { if(x > 10) sum += x; }
return sum;
```

---

## CS-PERF-010 — Cache Regex Instances
**Severity: Major**

**Rule**
`Regex` instances MUST be static and compiled.

**Bad Pattern**
```csharp
if (Regex.IsMatch(input, "pattern")) { ... } // Recompiles every time
```

**Good Pattern**
```csharp
[GeneratedRegex("pattern")]
private static partial Regex MyRegex();
// Or: private static readonly Regex _regex = new("pattern", RegexOptions.Compiled);
```

---

## CS-PERF-011 — Frozen Collections
**Severity: Major**

**Rule**
Use `FrozenDictionary` / `FrozenSet` for read-only lookup tables initialized at startup.

**Bad Pattern**
```csharp
// Dictionary has overhead for mutation support we don't need
private static readonly Dictionary<string, Handler> _handlers = new() {
    ["create"] = new CreateHandler(),
    ["delete"] = new DeleteHandler()
};
```

**Good Pattern**
```csharp
private static readonly FrozenDictionary<string, Handler> _handlers =
    new Dictionary<string, Handler> {
        ["create"] = new CreateHandler(),
        ["delete"] = new DeleteHandler()
    }.ToFrozenDictionary();
```

---

## CS-PERF-012 — SearchValues
**Severity: Major**

**Rule**
Use `SearchValues<T>` for repeated character/byte searches instead of Contains.

**Bad Pattern**
```csharp
// Allocates array and searches linearly each time
bool hasVowel = input.IndexOfAny(['a', 'e', 'i', 'o', 'u']) >= 0;
```

**Good Pattern**
```csharp
private static readonly SearchValues<char> Vowels =
    SearchValues.Create("aeiou");

bool hasVowel = input.AsSpan().IndexOfAny(Vowels) >= 0;
```

---

## CS-PERF-013 — Async State Machine Overhead
**Severity: Warning**

**Rule**
Avoid async in tight loops. Consider batching operations to reduce state machine allocations.

**Bad Pattern**
```csharp
foreach (var item in items) {
    await ProcessItemAsync(item); // State machine per iteration
}
```

**Good Pattern**
```csharp
// Option 1: Batch parallel execution
await Parallel.ForEachAsync(items, async (item, ct) => {
    await ProcessItemAsync(item);
});

// Option 2: If order matters, batch the I/O
var batches = items.Chunk(100);
foreach (var batch in batches) {
    await Task.WhenAll(batch.Select(ProcessItemAsync));
}
```