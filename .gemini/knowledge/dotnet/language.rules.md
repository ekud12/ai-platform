# C# Language Rules

## Purpose
Standards for Modern C# Syntax (C# 12+).

## Authority
Governs all `.cs` files. Modern syntax is mandatory.

---

## CS-LANG-001 — File-Scoped Namespaces
**Severity: Info**

**Rule**
MUST use File-Scoped Namespaces (reduce nesting).

**Bad Pattern**
```csharp
namespace MyApp {
    public class Class1 { ... }
}
```

**Good Pattern**
```csharp
namespace MyApp;

public class Class1 { ... }
```

---

## CS-LANG-002 — Record Types for Data Transfer
**Severity: Major**

**Rule**
DTOs and Messages MUST be `record`.

**Bad Pattern**
```csharp
public class UserDto {
    public string Name { get; set; }
}
```

**Good Pattern**
```csharp
public record UserDto(string Name);
```

---

## CS-LANG-003 — Primary Constructors
**Severity: Info**

**Rule**
Use Primary Constructors for dependency injection and simple initialization.

**Bad Pattern**
```csharp
public class Service {
    private readonly ILogger _logger;
    public Service(ILogger logger) { _logger = logger; }
}
```

**Good Pattern**
```csharp
public class Service(ILogger logger) { ... }
```

---

## CS-LANG-004 — Pattern Matching
**Severity: Major**

**Rule**
Prefer Pattern Matching (`is`, `switch`) over `as` casting.

**Bad Pattern**
```csharp
var btn = sender as Button;
if (btn != null) { ... }
```

**Good Pattern**
```csharp
if (sender is Button btn) { ... }
```

---

## CS-LANG-005 — Nullable Reference Types
**Severity: Critical**

**Rule**
Nullable Reference Types MUST be enabled. No implicit nulls.

**Bad Pattern**
```csharp
string name = null; // Warning!
```

**Good Pattern**
```csharp
string? name = null; // OK
```

---

## CS-LANG-006 — Collection Expressions
**Severity: Info**

**Rule**
Use Collection Expressions `[]` for initialization.

**Bad Pattern**
```csharp
var list = new List<int> { 1, 2, 3 };
```

**Good Pattern**
```csharp
List<int> list = [1, 2, 3];
```

---

## CS-LANG-007 — Raw String Literals
**Severity: Info**

**Rule**
Use Raw String Literals `"""` for JSON/SQL/Regex.

**Bad Pattern**
```csharp
var json = "{\"prop\": \"val\"}";
```

**Good Pattern**
```csharp
var json = """{"prop": "val"}"""
```

---

## CS-LANG-008 — Required Properties
**Severity: Major**

**Rule**
Use `required` for properties that MUST be set during object init.

**Bad Pattern**
```csharp
public class Config { public string Url { get; set; } }
var c = new Config(); // Url is null!
```

**Good Pattern**
```csharp
public class Config { public required string Url { get; set; } }
var c = new Config { Url = "..." }; // Compiler enforced
```

---

## CS-LANG-009 — Static Abstract Interface Members
**Severity: Info**

**Rule**
Use `static abstract` in interfaces for factories/operators.

**Bad Pattern**
```csharp
public interface IFactory<T> { T Create(); } // Instance method
```

**Good Pattern**
```csharp
public interface IFactory<T> { static abstract T Create(); }
```

---

## CS-LANG-010 — Implicit Usings
**Severity: Info**

**Rule**
Enable Implicit Usings. Remove explicit `using System;`.

**Bad Pattern**
```csharp
using System;
using System.Collections.Generic;
// ...
```

**Good Pattern**
```csharp
// (No usings needed for standard types)
```

---

## CS-LANG-011 — Global Usings
**Severity: Info**

**Rule**
Common namespaces MUST be in GlobalUsings.cs, not repeated per file.

**Bad Pattern**
```csharp
// In every file
using Microsoft.Extensions.Logging;
using MyApp.Common;
using MyApp.Models;
```

**Good Pattern**
```csharp
// In GlobalUsings.cs
global using Microsoft.Extensions.Logging;
global using MyApp.Common;
global using MyApp.Models;
```

---

## CS-LANG-012 — Target-Typed New
**Severity: Info**

**Rule**
Use `new()` when type is evident from declaration.

**Bad Pattern**
```csharp
Dictionary<string, List<int>> map = new Dictionary<string, List<int>>();
```

**Good Pattern**
```csharp
Dictionary<string, List<int>> map = new();
```

---

## CS-LANG-013 — List Patterns
**Severity: Info**

**Rule**
Use list patterns for array/list deconstruction and pattern matching.

**Bad Pattern**
```csharp
if (args.Length >= 2) {
    var first = args[0];
    var last = args[args.Length - 1];
}
```

**Good Pattern**
```csharp
if (args is [var first, .., var last]) {
    // Use first and last
}

// Or for exact matching
if (args is [var cmd, var file]) {
    // Exactly 2 elements
}
```

---

## CS-LANG-014 — XML Documentation Comments
**Severity: Major**

**Rule**
All public and internal members MUST have XML documentation comments. 

**Modern Syntax Addendum**
When using **Primary Constructors**, parameters MUST be documented in the class-level `<summary>` or using `<param name="...">` tags at the class level, as there is no traditional constructor block to attach them to.

**Bad Pattern**
```csharp
public class Service(ILogger logger); // No documentation for logger
```

**Good Pattern**
```csharp
/// <summary>
/// Initializes a new instance of the Service class.
/// </summary>
/// <param name="logger">The logger instance.</param>
public class Service(ILogger logger);
```

**Rationale**
XML documentation enables IntelliSense, generates API documentation, and ensures code is self-documenting for team members.