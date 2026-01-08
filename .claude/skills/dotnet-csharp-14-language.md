---
name: csharp-14-language
description: C# 14 language features and patterns for .NET 10. Enforce modern C# syntax, file-based apps, extension members, field keyword, and latest pattern matching.
allowed-tools: Read, Write, Edit
---

# C# 14 Language Features (Rules Only)

## File-Based Apps (NEW in C# 14)
- CS-FILE-001: Support single-file applications with .cs extension
- CS-FILE-002: Application can run with `dotnet run` without .sln or .csproj
- CS-FILE-003: Use for scripts, tools, and lightweight applications
- CS-FILE-004: Top-level statements already supported

## Extension Members (NEW in C# 14)
- CS-EXT-001: Use extension blocks for static extension methods
- CS-EXT-002: Support static and instance extension properties
- CS-EXT-003: Extension properties must be read-only
- CS-EXT-004: Organize extensions in dedicated extension blocks
- CS-EXT-005: Apply extension member pattern for cleaner syntax

## Field Keyword (NEW in C# 14)
- CS-FIELD-001: Use `field` contextual keyword in property accessors
- CS-FIELD-002: Access compiler-generated backing field directly
- CS-FIELD-003: Smooth path from auto-properties to custom accessors
- CS-FIELD-004: Replace manual backing fields in simple scenarios
- CS-FIELD-005: Mandatory for field-backed property pattern

## Nameof Enhancements (C# 14)
- CS-NAMEOF-001: Support unbound generic types in nameof expressions
- CS-NAMEOF-002: Use `nameof(List<>)` without type arguments
- CS-NAMEOF-003: Apply for generic type validation and error messages
- CS-NAMEOF-004: Replace string literals with compile-time safe references

## Implicit Span Conversions (C# 14)
- CS-SPAN-001: First-class support for implicit Span<T> conversions
- CS-SPAN-002: Implicit conversion for ReadOnlySpan<T>
- CS-SPAN-003: Prefer Span over arrays in method signatures
- CS-SPAN-004: Apply for zero-allocation scenarios

## Partial Enhancements (C# 14)
- CS-PARTIAL-001: Partial instance constructors now supported
- CS-PARTIAL-002: Partial events across partial type definitions
- CS-PARTIAL-003: Use for generated code scenarios
- CS-PARTIAL-004: Split complex types across files logically

## Null-Conditional Assignment (C# 14)
- CS-NULL-001: Use `??=` with null-conditional operator
- CS-NULL-002: Simplify conditional assignment patterns
- CS-NULL-003: Reduce null-check boilerplate

## Collection Expression Extensions (C# 14)
- CS-COLL-001: Enhanced spread operator support
- CS-COLL-002: Dictionary expression patterns
- CS-COLL-003: Apply collection expressions everywhere arrays/lists used
- CS-COLL-004: Mandatory over `new[]` or `new List<>`

## Params Collections (C# 13 - Still Mandatory)
- CS-PARAMS-001: Support Span<T>, ReadOnlySpan<T> for params
- CS-PARAMS-002: Use IEnumerable<T>, IReadOnlyCollection<T>, IReadOnlyList<T>
- CS-PARAMS-003: Prefer params with ReadOnlySpan<T> for zero-allocation
- CS-PARAMS-004: Mandatory over traditional params arrays

## Primary Constructors (C# 12 - Still Mandatory)
- CS-CTOR-001: Declare constructor parameters in class/struct definition
- CS-CTOR-002: Mandatory for dependency injection scenarios
- CS-CTOR-003: Capture parameters as fields automatically
- CS-CTOR-004: Applies to classes, structs, and records

## Required Members (C# 11 - Still Mandatory)
- CS-REQ-001: Use `required` modifier on properties
- CS-REQ-002: Apply `SetsRequiredMembers` attribute on constructors
- CS-REQ-003: Enforce complete object initialization at compile-time
- CS-REQ-004: Mandatory for all DTOs and request models

## File-Scoped Namespaces (C# 10 - Still Mandatory)
- CS-NS-001: Use file-scoped namespace declaration
- CS-NS-002: Reduces one level of indentation
- CS-NS-003: Mandatory for all new files
- CS-NS-004: One namespace per file only

## Collection Expressions (C# 12 - Still Mandatory)
- CS-COLLEXP-001: Use `[...]` syntax for all collections
- CS-COLLEXP-002: Apply spread operator `..` for combining collections
- CS-COLLEXP-003: Mandatory replacement for `new[]`, `new List<>`, `new Dictionary<>`
- CS-COLLEXP-004: Index operators `^` for end-relative indexing

## Pattern Matching (Mandatory)
- CS-PAT-001: Relational patterns: `is > 0 and < 100`
- CS-PAT-002: List patterns: `[> 0, ..]`, `[.., _]`
- CS-PAT-003: Property patterns: `{ Length: > 0 }`
- CS-PAT-004: Switch expressions with exhaustiveness
- CS-PAT-005: Never use if-else chains when patterns applicable

## Record Types (Mandatory)
- CS-REC-001: Use `record` for DTOs, responses, value objects
- CS-REC-002: Use `record struct` for lightweight value types
- CS-REC-003: Apply `sealed` to prevent inheritance
- CS-REC-004: Use positional syntax for simple records
- CS-REC-005: With-expressions for non-destructive mutations

## Ref Readonly (C# 12 - Still Mandatory)
- CS-REF-001: Use `ref readonly` for large struct parameters
- CS-REF-002: Avoid struct copying overhead
- CS-REF-003: Apply in performance-critical paths
- CS-REF-004: Mandatory for structs >16 bytes

## Inline Arrays (C# 12 - Still Mandatory)
- CS-INLINE-001: Fixed-length arrays on stack
- CS-INLINE-002: Zero-allocation scenarios
- CS-INLINE-003: Use for embedded buffers in structs

## UTF-8 String Literals (C# 11 - Still Mandatory)
- CS-UTF8-001: Use `u8"..."` for pre-encoded UTF-8 strings
- CS-UTF8-002: Zero runtime encoding cost
- CS-UTF8-003: Apply for HTTP headers, protocols, byte operations

## Generic Math (C# 11 - Still Mandatory)
- CS-MATH-001: Static abstract members in interfaces
- CS-MATH-002: Use `INumber<T>`, `IAdditionOperators<T>` interfaces
- CS-MATH-003: Generic algorithms without boxing

## Type Alias (C# 12 - Still Mandatory)
- CS-ALIAS-001: Use `using` for type aliases
- CS-ALIAS-002: Alias complex generic types
- CS-ALIAS-003: Improves readability for nested generics

## File-Scoped Types (C# 11 - Mandatory)
- CS-FILETYPE-001: Use `file` modifier for implementation details
- CS-FILETYPE-002: Restricts visibility to single file
- CS-FILETYPE-003: Apply for helper types not meant for assembly-wide use

## Forbidden Patterns
- CS-FORBID-001: Never use `any` or `dynamic`
- CS-FORBID-002: No implicit interface implementations without explicit modifier
- CS-FORBID-003: No mutable public fields
- CS-FORBID-004: No `var` when type isn't obvious
- CS-FORBID-005: No regional directives
- CS-FORBID-006: No suppression of nullable warnings without justification
- CS-FORBID-007: No raw string interpolations without proper escaping

## Exhaustiveness Requirements
- CS-EXHAUST-001: All switch expressions must handle all cases
- CS-EXHAUST-002: Use `default` with `throw` or `never` type
- CS-EXHAUST-003: Pattern matching must be exhaustive
- CS-EXHAUST-004: No missing cases in discriminated unions
