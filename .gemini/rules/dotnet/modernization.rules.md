# .NET Modernization & Best Practices (2025 Edition)

## Purpose
Enforce the use of modern C# features to reduce boilerplate and improve performance.

## 1. Top-Level Statements & Minimal APIs
**Rule:** Prefer Top-Level statements for `Program.cs`. Avoid legacy `Startup.cs`.

**❌ Legacy (Bad):**
```csharp
public class Program {
    public static void Main(string[] args) {
        CreateHostBuilder(args).Build().Run();
    }
}
```

**✅ Modern (Good):**
```csharp
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();
app.Run();
```

## 2. Records for DTOs
**Rule:** Use `record` or `record struct` for data transfer objects.

**❌ Legacy (Bad):**
```csharp
public class UserDto {
    public string Name { get; set; }
    public UserDto(string name) { Name = name; }
}
```

**✅ Modern (Good):**
```csharp
public record UserDto(string Name);
```

## 3. Primary Constructors
**Rule:** Use primary constructors for dependency injection in classes.

**❌ Legacy (Bad):**
```csharp
public class Service {
    private readonly IRepo _repo;
    public Service(IRepo repo) { _repo = repo; }
}
```

**✅ Modern (Good):**
```csharp
public class Service(IRepo repo) {
    // _repo is implied or can be assigned
}
```

## 4. Collection Expressions (C# 12)
**Rule:** Use `[]` syntax for collections.

**❌ Legacy (Bad):**
```csharp
var list = new List<int> { 1, 2, 3 };
var array = new int[] { 1, 2, 3 };
```

**✅ Modern (Good):**
```csharp
List<int> list = [1, 2, 3];
int[] array = [1, 2, 3];
```
