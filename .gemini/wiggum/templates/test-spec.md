# Test Specification: Hello World Service

## Overview

Create a simple "Hello World" service to test the Wiggum autonomous loop.

## Requirements

### 1. Create a Greeting Service

Create a simple C# class that returns greeting messages.

**File:** `project/src/Test/GreetingService.cs`

```csharp
namespace Test;

public class GreetingService
{
    public string GetGreeting(string name)
    {
        if (string.IsNullOrWhiteSpace(name))
            return "Hello, World!";

        return $"Hello, {name}!";
    }
}
```

### 2. Create a Unit Test

Create a test for the greeting service.

**File:** `project/src/Test/GreetingServiceTests.cs`

```csharp
namespace Test;

public class GreetingServiceTests
{
    [Fact]
    public void GetGreeting_WithName_ReturnsPersonalizedGreeting()
    {
        var service = new GreetingService();
        var result = service.GetGreeting("Wiggum");
        Assert.Equal("Hello, Wiggum!", result);
    }

    [Fact]
    public void GetGreeting_WithoutName_ReturnsDefaultGreeting()
    {
        var service = new GreetingService();
        var result = service.GetGreeting("");
        Assert.Equal("Hello, World!", result);
    }
}
```

## Acceptance Criteria

- [ ] GreetingService.cs exists and compiles
- [ ] GreetingServiceTests.cs exists
- [ ] Tests follow xUnit conventions

## Constraints

- Keep it simple - this is just a test
- No external dependencies
- .NET only
