# .NET File Organization Rules

## Purpose

Standards for file and folder organization in .NET projects including solution structure, project layouts, and namespace alignment.

## Authority

Governs all .NET solution and project structures. Consistent organization is mandatory.

## Scope

Applies to solution files, project files, folder structures, and file naming.

---

## CS-FILE-001 — Folder Naming Convention

**Severity: Critical**

**Rule**
All folder names MUST use PascalCase (capital first letter). No lowercase folders.

**Bad Pattern**
```
src/
  services/
  models/
  features/orders/
```

**Good Pattern**
```
src/
  Services/
  Models/
  Orders/
  Users/
```

**Rationale**
PascalCase folders match .NET namespace conventions and maintain consistency.

---

## CS-FILE-002 — Solution Structure

**Severity: Major**

**Rule**
Solutions MUST organize projects in standard folders: `src/`, `tests/`, optionally `tools/`, `docs/`.

**Bad Pattern**
```
MyApp.sln
MyApp.Api/
MyApp.Core/
MyApp.Tests/
```

**Good Pattern**
```
MyApp.sln
src/
  MyApp.Api/
  MyApp.Core/
  MyApp.Infrastructure/
tests/
  MyApp.Api.Tests/
  MyApp.Core.Tests/
docs/
tools/
```

**Rationale**
Standard structure enables predictable navigation and build configurations.

---

## CS-FILE-003 — Project Naming

**Severity: Major**

**Rule**
Projects MUST follow `Company.Product.Layer` naming pattern.

**Bad Pattern**
```
Api.csproj
Core.csproj
Data.csproj
```

**Good Pattern**
```
MyCompany.OrderSystem.Api.csproj
MyCompany.OrderSystem.Core.csproj
MyCompany.OrderSystem.Infrastructure.csproj
MyCompany.OrderSystem.Contracts.csproj
```

**Rationale**
Qualified names prevent conflicts and clarify ownership.

---

## CS-FILE-004 — Domain-First Organization

**Severity: Major**

**Rule**
Organize by domain/feature, not by technical layer. No `Features/` wrapper folder.

**Bad Pattern**
```
Features/
  Orders/
  Users/
Controllers/
Services/
Repositories/
```

**Good Pattern**
```
Orders/
  OrderController.cs
  OrderService.cs
  OrderRepository.cs
  OrderDto.cs
Users/
  UserController.cs
  UserService.cs
```

**Rationale**
Domain-first organization keeps related code together and reduces navigation.

---

## CS-FILE-005 — Primitives Project

**Severity: Major**

**Rule**
Shared base types MUST live in a `*.Primitives` or `*.Contracts` project with no dependencies.

**Bad Pattern**
```
// Shared types scattered across projects
MyApp.Api/Models/EntityBase.cs
MyApp.Core/Common/Result.cs
MyApp.Infrastructure/Interfaces/IIdentifiable.cs
```

**Good Pattern**
```
MyCompany.OrderSystem.Primitives/
  Entities/EntityBase.cs
  ValueObjects/Money.cs
  Interfaces/IIdentifiable.cs
  Results/Result.cs
  Enums/OrderStatus.cs
```

**Rationale**
Leaf dependency project prevents circular references and centralizes shared types.

---

## CS-FILE-006 — File-Type Matching

**Severity: Critical**

**Rule**
File names MUST exactly match the primary type name.

**Bad Pattern**
```
OrderModels.cs       // Contains Order class
UserServiceImpl.cs   // Contains UserService class
Dtos.cs              // Contains multiple DTOs
```

**Good Pattern**
```
Order.cs             // Contains Order class
UserService.cs       // Contains UserService class
OrderDto.cs          // Contains OrderDto record
CreateOrderRequest.cs // Contains CreateOrderRequest record
```

**Rationale**
Predictable file names enable quick navigation and prevent confusion.

---

## CS-FILE-007 — One Primary Type Per File

**Severity: Major**

**Rule**
Each file MUST contain one primary public type. Related nested/helper types may coexist.

**Bad Pattern**
```csharp
// Models.cs
public class Order { }
public class Customer { }
public class Product { }
```

**Good Pattern**
```csharp
// Order.cs
public class Order
{
    public record OrderLine(int ProductId, int Quantity); // Nested is OK
}

// Customer.cs
public class Customer { }

// Product.cs
public class Product { }
```

**Rationale**
Single-type files are easier to navigate, review, and maintain.

---

## CS-FILE-008 — Interface File Separation

**Severity: Major**

**Rule**
Interfaces MUST be in separate files from implementations. All interfaces in `Interfaces/` folder.

**Bad Pattern**
```csharp
// OrderService.cs
public interface IOrderService { }
public class OrderService : IOrderService { }
```

**Good Pattern**
```
Interfaces/
  IOrderService.cs
  IOrderRepository.cs
Services/
  OrderService.cs
Repositories/
  OrderRepository.cs
```

**Rationale**
Separate interface files enable dependency inversion and clean architecture.

---

## CS-FILE-009 — Related Records in Single File

**Severity: Info**

**Rule**
Small related records (DTOs, requests, responses) MAY share a file if closely related.

**Bad Pattern**
```
// Too many unrelated types in one file
AllOrderDtos.cs // Contains 20 different DTOs
```

**Good Pattern**
```csharp
// OrderDtos.cs - Related DTOs together
public record OrderDto(string Id, decimal Total);
public record OrderSummaryDto(string Id, string Status);
public record OrderLineDto(string ProductId, int Quantity);

// OrderCommands.cs - Related commands together
public record CreateOrderCommand(string CustomerId, List<OrderLineDto> Lines);
public record CancelOrderCommand(string OrderId, string Reason);
```

**Rationale**
Grouping related records reduces file count while maintaining cohesion.

---

## CS-FILE-010 — Extension Files

**Severity: Info**

**Rule**
Extension methods MUST be in `Extensions/` folder with `{Type}Extensions.cs` naming.

**Bad Pattern**
```
Helpers/StringHelpers.cs
Utils/Extensions.cs
```

**Good Pattern**
```
Extensions/
  StringExtensions.cs
  EnumerableExtensions.cs
  HttpClientExtensions.cs
  ServiceCollectionExtensions.cs
```

**Rationale**
Consistent location and naming makes extensions discoverable.

---

## CS-FILE-011 — Configuration Files

**Severity: Major**

**Rule**
Configuration option classes MUST be in `Configuration/` or `Options/` folder.

**Bad Pattern**
```
// Scattered configuration classes
Services/DatabaseSettings.cs
Api/AppConfig.cs
```

**Good Pattern**
```
Configuration/
  DatabaseOptions.cs
  CacheOptions.cs
  AuthenticationOptions.cs
  FeatureFlags.cs
```

**Rationale**
Centralized configuration is easier to review and maintain.

---

## CS-FILE-012 — Namespace-Folder Alignment

**Severity: Critical**

**Rule**
Namespaces MUST match folder path. No namespace/folder mismatches.

**Bad Pattern**
```csharp
// File: src/Orders/Services/OrderService.cs
namespace MyApp.Services; // Doesn't match path
```

**Good Pattern**
```csharp
// File: src/Orders/Services/OrderService.cs
namespace MyApp.Orders.Services;
```

**Rationale**
Matching namespaces and folders prevents confusion and enables tooling.

---

## CS-FILE-013 — Test Project Structure

**Severity: Major**

**Rule**
Test projects MUST mirror source project structure.

**Bad Pattern**
```
MyApp.Tests/
  OrderTests.cs
  UserTests.cs
  AllIntegrationTests.cs
```

**Good Pattern**
```
MyApp.Core.Tests/
  Orders/
    OrderServiceTests.cs
    OrderValidatorTests.cs
  Users/
    UserServiceTests.cs
  Fixtures/
    DatabaseFixture.cs
  Helpers/
    TestDataBuilder.cs
```

**Rationale**
Parallel structure makes finding and maintaining tests intuitive.

---

## CS-FILE-014 — Project File Configuration

**Severity: Critical**

**Rule**
All `.csproj` files MUST be explicit with full configuration, not minimal/implicit.

**Bad Pattern**
```xml
<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
  </PropertyGroup>
</Project>
```

**Good Pattern**
```xml
<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <!-- Build Configuration -->
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <WarningsAsErrors />

    <!-- Assembly Information -->
    <RootNamespace>MyCompany.OrderSystem.Api</RootNamespace>
    <AssemblyName>MyCompany.OrderSystem.Api</AssemblyName>

    <!-- Documentation -->
    <GenerateDocumentationFile>true</GenerateDocumentationFile>
    <NoWarn>$(NoWarn);1591</NoWarn>

    <!-- Analyzers -->
    <EnableNETAnalyzers>true</EnableNETAnalyzers>
    <AnalysisLevel>latest</AnalysisLevel>
    <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>

    <!-- Package Metadata -->
    <Authors>MyCompany</Authors>
    <Company>MyCompany</Company>
    <Description>Order System API</Description>
  </PropertyGroup>

  <!-- Dependencies -->
  <ItemGroup>
    <PackageReference Include="Microsoft.AspNetCore.OpenApi" Version="10.0.0" />
  </ItemGroup>

  <!-- Project References -->
  <ItemGroup>
    <ProjectReference Include="..\MyCompany.OrderSystem.Core\MyCompany.OrderSystem.Core.csproj" />
  </ItemGroup>
</Project>
```

**Rationale**
Explicit configuration prevents surprises and documents project requirements.

---

## CS-FILE-015 — GlobalUsings File

**Severity: Major**

**Rule**
Common using statements MUST be in `GlobalUsings.cs` at project root.

**Bad Pattern**
```csharp
// Every file repeats common usings
using Microsoft.Extensions.Logging;
using System.Text.Json;
using MyApp.Common;
```

**Good Pattern**
```csharp
// GlobalUsings.cs
global using Microsoft.Extensions.Logging;
global using System.Text.Json;
global using MyApp.Common;
global using MyApp.Orders.Models;
```

**Rationale**
Global usings reduce repetition and ensure consistent imports.

---

## Forbidden Patterns

- CS-FILE-FORBID-001: No lowercase folder names
- CS-FILE-FORBID-002: No `Features/` wrapper folder - use domain names directly
- CS-FILE-FORBID-003: No multiple public types in single file (except records)
- CS-FILE-FORBID-004: No namespace/folder mismatches
- CS-FILE-FORBID-005: No `Helpers/` or `Utils/` as catch-all folders
- CS-FILE-FORBID-006: No `Misc/` or `Other/` folders
- CS-FILE-FORBID-007: No deeply nested folders (max 5 levels from project root)
- CS-FILE-FORBID-008: No minimal `.csproj` files without explicit configuration
- CS-FILE-FORBID-009: No business logic in `Common/` folders
- CS-FILE-FORBID-010: No mixed concerns in single folder
