---
name: dotnet-library-first
description: Check for existing .NET/C# libraries before writing boilerplate. Always ask user permission before adding new packages.
allowed-tools: Read, Write, Edit, WebSearch
---

# .NET Library-First Approach (Rules Only)

## Core Principle

Before writing boilerplate in C#/.NET, search for existing well-maintained NuGet packages. **Always ask user permission before adding any library.**

## When to Search for Libraries

Check for packages when implementing:

- Error handling patterns (Result/Either types)
- Authentication/Authorization (OAuth, JWT, RBAC)
- Validation (FluentValidation)
- HTTP resilience (Polly)
- Serialization (beyond System.Text.Json)
- Testing utilities (Moq, FluentAssertions)
- Data mapping (Mapster, AutoMapper)
- Caching (beyond Microsoft.Extensions.Caching)
- Configuration management
- Rate limiting
- Background jobs
- Message queuing
- Email/SMS sending

## Search Process

### Step 1: Use WebSearch

Query format: `"best C# library for [functionality] .NET 10 2025"`

### Step 2: Evaluate Top Results

Check:

- **NuGet stats**: Downloads, last updated
- **GitHub**: Stars, commits, issues
- **Compatibility**: .NET 10 support
- **Security**: No known vulnerabilities
- **License**: MIT, Apache 2.0, etc.

### Step 3: Ask User Permission

**Required format:**

```
Found: [PackageName] v[version]
- Downloads: [count/month]
- Last updated: [date]
- GitHub stars: [count]
- License: [type]
- Docs: [url]

This would replace [X] lines of custom code.

May I add this package? (yes/no)
```

## Preferred .NET Libraries

### Official/Microsoft (Usually Pre-approved)

- `System.Text.Json` - JSON serialization
- `Microsoft.Extensions.*` - DI, Configuration, Caching, Logging
- `Microsoft.AspNetCore.*` - Web framework

### Well-Established Third-Party

- `FluentValidation` - Input validation
- `Polly` - Resilience and transient fault handling
- `Serilog` - Structured logging
- `Mapster` or `AutoMapper` - Object mapping
- `Moq` or `NSubstitute` - Mocking for tests
- `FluentAssertions` - Test assertions
- `Refit` - Type-safe HTTP clients
- `MediatR` - Mediator pattern
- `Dapper` - Micro-ORM
- `Hangfire` or `Quartz.NET` - Background jobs

## Decision Framework

### ✅ Recommend Library When:

- Well-maintained (commits within 6 months)
- Popular (>1M downloads or >5K stars)
- Stable (v1.0+)
- .NET 10 compatible
- Reduces >50 lines of boilerplate
- **After user approval**

### ✅ Write Custom When:

- No suitable package exists
- Simple functionality (<20 lines)
- User declines package addition
- Package is unmaintained (>1 year)
- Security vulnerabilities present

## Installation Command

After approval:

```bash
dotnet add package [PackageName]
```

## Anti-Patterns

- ❌ Adding packages without user permission
- ❌ Using deprecated packages
- ❌ Writing custom Result/Either types (search for libraries first and only if not write your own)
- ❌ Writing custom validation (use FluentValidation)
- ❌ Writing custom retry logic (use Polly)
- ❌ Using packages with security issues
