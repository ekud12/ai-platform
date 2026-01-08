---
name: dotnet-file-organization
description: File and folder organization patterns for .NET projects including solution structure, feature folders, and project layouts.
allowed-tools: Read, Write, Edit
---

# .NET File Organization (Rules Only)

## Folder Naming Convention
- FILE-FOLDER-001: All folder names MUST start with PascalCase (capital letter)
- FILE-FOLDER-002: Examples: `Services/`, `Models/`, `Controllers/`, `Orders/`, `Users/`
- FILE-FOLDER-003: NEVER use lowercase folder names like `services/`, `models/`, `features/`
- FILE-FOLDER-004: FORBIDDEN: `Features/` folder - organize directly by domain: `Orders/`, `Users/`, `Products/`
- FILE-FOLDER-005: Use domain names directly, not meta-containers

## Solution Structure
- FILE-SOL-001: One solution file at repository root
- FILE-SOL-002: Group projects in `src/` folder
- FILE-SOL-003: Group tests in `tests/` folder
- FILE-SOL-004: Place shared tooling in `tools/` or `build/`
- FILE-SOL-005: Documentation in `docs/` folder
- FILE-SOL-006: Solution folders mirror physical folders

## Project Organization
- FILE-PROJ-001: One project per bounded context/domain area
- FILE-PROJ-002: Separate API, Domain, Infrastructure, Application projects
- FILE-PROJ-003: Name projects: `Company.Product.Layer` pattern
- FILE-PROJ-004: Keep projects focused and cohesive
- FILE-PROJ-005: Avoid circular project references

## Primitives Project
- FILE-PRIM-001: Create `Company.Product.Primitives` project for shared base models
- FILE-PRIM-002: Contains: base entities, value objects, common interfaces, shared enums
- FILE-PRIM-003: No dependencies on other domain projects (leaf dependency)
- FILE-PRIM-004: All projects reference Primitives for shared types
- FILE-PRIM-005: Examples: `EntityBase`, `AuditableEntity`, `IIdentifiable`, `Result<T>`

## Domain Folders (Recommended)
- FILE-DOMAIN-001: Organize by domain/feature, not by type
- FILE-DOMAIN-002: Structure: `Orders/`, `Users/`, `Products/` - NO `Features/` wrapper
- FILE-DOMAIN-003: Each domain contains its own Models, Services, Handlers subfolders
- FILE-DOMAIN-004: Shared code in `Common/` or `Shared/` folder
- FILE-DOMAIN-005: Prefer vertical slices over horizontal layers

## Services Folder
- FILE-SVC-001: All services in `Services/` folder - mandatory
- FILE-SVC-002: Organize by domain within Services: `Services/Orders/`, `Services/Users/`
- FILE-SVC-003: One service class per file
- FILE-SVC-004: Service implementations reference interfaces from `Interfaces/`

## Traditional Layer Folders
- FILE-LAYER-001: If using layers: `Models/`, `Services/`, `Controllers/`
- FILE-LAYER-002: Keep consistent across all projects
- FILE-LAYER-003: Domain: `Entities/`, `ValueObjects/`, `Aggregates/`
- FILE-LAYER-004: Infrastructure: `Persistence/`, `External/`, `Messaging/`
- FILE-LAYER-005: Application: `Commands/`, `Queries/`, `Handlers/`

## File Naming
- FILE-NAME-001: File name matches primary type name exactly
- FILE-NAME-002: `OrderProcessor.cs` contains `class OrderProcessor`
- FILE-NAME-003: One primary public type per file
- FILE-NAME-004: Nested/helper types can share file with parent
- FILE-NAME-005: Partial classes: `Order.cs`, `Order.Validation.cs`

## Interface Files
- FILE-IFACE-001: Interface in separate file: `IOrderService.cs`
- FILE-IFACE-002: Implementation in own file: `OrderService.cs`
- FILE-IFACE-003: All interfaces in `Interfaces/` folder - mandatory
- FILE-IFACE-004: Organize by domain within Interfaces: `Interfaces/Orders/`, `Interfaces/Users/`

## Record and DTO Files
- FILE-DTO-001: Related records can share file if small
- FILE-DTO-002: Group by feature: `OrderDtos.cs` for related DTOs
- FILE-DTO-003: Large/complex types get own file
- FILE-DTO-004: Request/Response pairs can share file

## Extension Files
- FILE-EXT-001: Group extensions by target type
- FILE-EXT-002: `StringExtensions.cs`, `EnumerableExtensions.cs`
- FILE-EXT-003: Place in `Extensions/` folder
- FILE-EXT-004: Keep focused - one concern per extension class

## Configuration Files
- FILE-CFG-001: `appsettings.json` at project root
- FILE-CFG-002: Environment-specific: `appsettings.Development.json`
- FILE-CFG-003: Options classes in `Configuration/` or `Options/` folder
- FILE-CFG-004: One options class per configuration section

## Startup and Entry
- FILE-START-001: `Program.cs` as single entry point
- FILE-START-002: Extension methods for service registration
- FILE-START-003: Group registration: `ServiceCollectionExtensions.cs`
- FILE-START-004: Middleware in `Middleware/` folder

## Test Organization
- FILE-TEST-001: Mirror source project structure in test project
- FILE-TEST-002: `OrderProcessorTests.cs` tests `OrderProcessor.cs`
- FILE-TEST-003: Group fixtures in `Fixtures/` folder
- FILE-TEST-004: Test helpers in `Helpers/` or `TestUtilities/`
- FILE-TEST-005: Integration tests in separate project

## Generated Files
- FILE-GEN-001: Place in `Generated/` folder
- FILE-GEN-002: Mark with `.g.cs` or `.Generated.cs` suffix
- FILE-GEN-003: Exclude from code coverage
- FILE-GEN-004: Add to `.gitignore` if regenerated on build

## Namespace Alignment
- FILE-NS-001: Namespace matches folder path
- FILE-NS-002: `Company.Product.Features.Orders` for `Features/Orders/`
- FILE-NS-003: Use file-scoped namespaces (one per file)
- FILE-NS-004: No namespace mismatches with folder structure

## Common Folders
- FILE-COMMON-001: `Common/` for cross-cutting utilities
- FILE-COMMON-002: `Exceptions/` for custom exception types
- FILE-COMMON-003: `Constants/` for application constants
- FILE-COMMON-004: `Validators/` for FluentValidation validators
- FILE-COMMON-005: `Mappings/` for AutoMapper profiles

## Project File Configuration (.csproj)
- FILE-CSPROJ-001: ALWAYS write explicit, fully-configured `.csproj` files
- FILE-CSPROJ-002: Include ALL relevant properties with XML comments explaining purpose
- FILE-CSPROJ-003: Required properties: TargetFramework, Nullable, ImplicitUsings, RootNamespace, AssemblyName
- FILE-CSPROJ-004: Include descriptions: `<Description>`, `<Authors>`, `<Company>`
- FILE-CSPROJ-005: Enable analyzers: `<EnableNETAnalyzers>true</EnableNETAnalyzers>`
- FILE-CSPROJ-006: Treat warnings as errors: `<TreatWarningsAsErrors>true</TreatWarningsAsErrors>`
- FILE-CSPROJ-007: Include XML documentation: `<GenerateDocumentationFile>true</GenerateDocumentationFile>`
- FILE-CSPROJ-008: Version all packages explicitly with version numbers
- FILE-CSPROJ-009: Group PackageReferences logically with comments

## Forbidden Patterns
- FILE-FORBID-001: No multiple public types in single file (except records/DTOs)
- FILE-FORBID-002: No namespace/folder mismatch
- FILE-FORBID-003: No `Helpers/` folder as dumping ground
- FILE-FORBID-004: No deeply nested folders (max 4-5 levels)
- FILE-FORBID-005: No mixed concerns in single folder
- FILE-FORBID-006: No `Misc/` or `Other/` folders
- FILE-FORBID-007: No business logic in `Utils/` folders
- FILE-FORBID-008: No `Features/` folder naming - use domain names directly
- FILE-FORBID-009: No lowercase folder names - always PascalCase
- FILE-FORBID-010: No minimal/implicit `.csproj` files - always explicit configuration
