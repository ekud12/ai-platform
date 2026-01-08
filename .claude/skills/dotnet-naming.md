---
name: dotnet-naming
description: Naming conventions for namespaces, classes, methods, properties, fields, and parameters following .NET standards.
allowed-tools: Read, Write, Edit
---

# .NET Naming Conventions (Rules Only)

## Namespaces
- NAME-NS-001: Use PascalCase: `Company.Product.Feature`
- NAME-NS-002: Reflect solution architecture
- NAME-NS-003: Follow `Company.Core.Area.Feature` pattern
- NAME-NS-004: Match folder structure
- NAME-NS-005: No abbreviations unless well-known
- NAME-NS-006: Singular nouns preferred

## Classes and Structs
- NAME-CLASS-001: Use PascalCase noun phrases
- NAME-CLASS-002: Descriptive names: `OrderProcessor`, `UserValidator`
- NAME-CLASS-003: Suffix with purpose when ambiguous: `UserService`, `OrderRepository`
- NAME-CLASS-004: No prefixes like `C` or `Cls`
- NAME-CLASS-005: Interfaces prefix with `I`: `IPaymentProcessor`

## Interfaces
- NAME-IFACE-001: Always prefix with `I`: `IRepository`, `IService`
- NAME-IFACE-002: Focus on capabilities: `IPaymentProcessor` not `IStripePaymentService`
- NAME-IFACE-003: Use adjectives for contracts: `IDisposable`, `IComparable`
- NAME-IFACE-004: Behavioral interfaces describe what, not how

## Methods
- NAME-METH-001: Use PascalCase verb phrases
- NAME-METH-002: Action-oriented: `ProcessPayment`, `ValidateUser`, `GetOrders`
- NAME-METH-003: Async methods suffix with `Async`: `ProcessPaymentAsync`
- NAME-METH-004: Boolean methods prefix with `Is`, `Has`, `Can`, `Should`: `IsValid`, `HasPermission`
- NAME-METH-005: Factory methods: `Create`, `Build`, `From`

## Properties
- NAME-PROP-001: Use PascalCase nouns or adjectives
- NAME-PROP-002: Descriptive: `FirstName`, `IsActive`, `TotalAmount`
- NAME-PROP-003: Boolean properties: `IsValid`, `HasChildren`, `CanExecute`
- NAME-PROP-004: Collection properties: plural `Orders`, `Users`
- NAME-PROP-005: No `Get` or `Set` prefixes

## Fields
- NAME-FIELD-001: Private fields: `_camelCase` with underscore prefix: `_userId`, `_dbContext`
- NAME-FIELD-002: Const and readonly fields (public): PascalCase: `MaxRetries`, `DefaultTimeout`
- NAME-FIELD-003: Const fields (private): `_UPPER_SNAKE_CASE`: `_MAX_RETRY_COUNT`
- NAME-FIELD-004: No Hungarian notation
- NAME-FIELD-005: Static readonly fields: PascalCase

## Parameters and Local Variables
- NAME-PARAM-001: Use camelCase: `userId`, `orderTotal`, `isValid`
- NAME-PARAM-002: Descriptive, no abbreviations: `customerId` not `custId`
- NAME-PARAM-003: No single-letter except loop counters (`i`, `j`, `k`)
- NAME-PARAM-004: Lambda parameters can be short if obvious: `x => x.Id`

## Constants
- NAME-CONST-001: Public constants: PascalCase: `MaxRetries`, `DefaultPageSize`
- NAME-CONST-002: Private constants: `_UPPER_SNAKE_CASE`: `_DEFAULT_TIMEOUT`
- NAME-CONST-003: Group related constants in static class
- NAME-CONST-004: Use `const` for compile-time values, `static readonly` for runtime

## Generic Type Parameters
- NAME-GEN-001: Single letter for simple: `T`, `TKey`, `TValue`
- NAME-GEN-002: Descriptive for complex: `TEntity`, `TResponse`, `TRequest`
- NAME-GEN-003: Prefix with `T`: `TRepository`, `TService`

## Async Methods
- NAME-ASYNC-001: Always suffix with `Async`: `GetUserAsync`, `ProcessOrderAsync`
- NAME-ASYNC-002: No exceptions to this rule
- NAME-ASYNC-003: Apply even for internal/private methods
- NAME-ASYNC-004: Maintains consistency across codebase

## Boolean Names
- NAME-BOOL-001: Prefix with `Is`, `Has`, `Can`, `Should`: `IsActive`, `HasPermission`, `CanExecute`, `ShouldRetry`
- NAME-BOOL-002: Avoid negative names: `IsEnabled` not `IsDisabled`
- NAME-BOOL-003: Clear intent: `IsValid` not `CheckValidity`

## Enums
- NAME-ENUM-001: Use PascalCase for enum name: `OrderStatus`, `PaymentMethod`
- NAME-ENUM-002: Use PascalCase for values: `Pending`, `Completed`
- NAME-ENUM-003: Plural for flags: `FilePermissions`
- NAME-ENUM-004: Singular for non-flags: `OrderStatus`

## Events
- NAME-EVT-001: Use PascalCase: `OrderPlaced`, `PaymentProcessed`
- NAME-EVT-002: Past tense for completed: `OrderPlaced`
- NAME-EVT-003: Present progressive for in-process: `OrderPlacing`
- NAME-EVT-004: Event handlers suffix: `OnOrderPlaced`, `HandlePaymentProcessed`

## Extension Methods
- NAME-EXT-001: Place in static classes with `Extensions` suffix: `StringExtensions`
- NAME-EXT-002: First parameter: `this` modified type
- NAME-EXT-003: Descriptive names matching intent

## Test Methods
- NAME-TEST-001: Pattern: `Method_Scenario_ExpectedResult`
- NAME-TEST-002: Example: `ProcessPayment_InvalidCard_ThrowsException`
- NAME-TEST-003: Or use complete sentences: `Should_Throw_When_Card_Invalid`
- NAME-TEST-004: Consistent pattern within project

## Forbidden Patterns
- NAME-FORBID-001: No Hungarian notation: no `strName`, `intCount`
- NAME-FORBID-002: No abbreviations unless universal: `Id`, `Url`, `Http`
- NAME-FORBID-003: No underscores except private fields
- NAME-FORBID-004: No single-letter variables except loop counters
- NAME-FORBID-005: No `Get` prefix on properties
- NAME-FORBID-006: No inconsistent casing
- NAME-FORBID-007: No generic names: `Manager`, `Helper`, `Utility` without context
- NAME-FORBID-008: No async methods without `Async` suffix
