---
name: typescript-architecture
description: TypeScript architecture patterns including feature-first organization, aliased imports, naming conventions, and strict layer boundaries.
allowed-tools: Read, Write, Edit
---

# TypeScript Architecture Patterns (Rules Only)

## Purpose
Enforce consistent project structure, module organization, naming conventions, and architectural boundaries in TypeScript projects.

## Folder Structure

### Feature-First Organization
- TS-ARCH-001: Organize by feature/domain, not by technical layer
- TS-ARCH-002: Each feature has its own folder with all related files
- TS-ARCH-003: Use canonical file suffixes (`.service.ts`, `.guard.ts`, `.schema.ts`, `.types.ts`)
- TS-ARCH-004: Co-locate tests with implementation files
- TS-ARCH-005: Group related features under domain folders

### Shared Code
- TS-ARCH-006: Shared logic must live in `@shared` or `@core`, not between features
- TS-ARCH-007: No direct imports between sibling features
- TS-ARCH-008: Extract common patterns to shared modules
- TS-ARCH-009: Clearly define public API of shared modules

## Import Management

### Aliased Imports
- TS-ARCH-010: Use path aliases (`@core/...`, `@features/...`) - no relative traversals
- TS-ARCH-011: No `../../../` paths - configure tsconfig paths
- TS-ARCH-012: One import statement per module (no multiple from same module)
- TS-ARCH-013: Group imports: external, internal, relative
- TS-ARCH-014: Sort imports alphabetically within groups

### Import/Export Patterns
- TS-ARCH-015: Named exports only - no default exports
- TS-ARCH-016: No default exports anywhere in codebase
- TS-ARCH-017: Explicit exports - no `export *` re-exports
- TS-ARCH-018: No circular imports (enforce acyclic import graph)
- TS-ARCH-019: No logic in `index.ts` or re-export barrels
- TS-ARCH-020: Index files for public API only

### Circular Dependencies
- TS-ARCH-021: Detect and eliminate circular imports
- TS-ARCH-022: Use dependency injection to break cycles
- TS-ARCH-023: Extract interfaces to separate files to break cycles
- TS-ARCH-024: Enforce acyclic dependency graph with tooling

## Layer Boundaries

### Strict Layering
- TS-ARCH-025: No upward import violations (lower layers can't import from higher)
- TS-ARCH-026: Define clear layer hierarchy (e.g., domain > application > infrastructure > presentation)
- TS-ARCH-027: Domain layer has no dependencies on infrastructure
- TS-ARCH-028: Dependency inversion at layer boundaries
- TS-ARCH-029: Use interfaces to decouple layers

### Module Boundaries
- TS-ARCH-030: Each module has single responsibility
- TS-ARCH-031: Clear public API per module (exported in index.ts)
- TS-ARCH-032: Private implementation details not exported
- TS-ARCH-033: No cross-cutting concerns in feature modules

## Naming Conventions

### File Naming
- TS-ARCH-034: Files use kebab-case: `user-service.ts`
- TS-ARCH-035: Test files use `.test.ts` or `.spec.ts` suffix
- TS-ARCH-036: Type files use `.types.ts` suffix
- TS-ARCH-037: Schema files use `.schema.ts` suffix
- TS-ARCH-038: One primary export per file

### Code Naming
- TS-ARCH-039: Types use PascalCase: `type UserProfile`
- TS-ARCH-040: Interfaces use PascalCase: `interface IUserService`
- TS-ARCH-041: Classes use PascalCase: `class UserService`
- TS-ARCH-042: Functions use camelCase: `function getUserById`
- TS-ARCH-043: Variables use camelCase: `const userId`
- TS-ARCH-044: Constants use SCREAMING_SNAKE_CASE: `const MAX_RETRY_COUNT`
- TS-ARCH-045: Private class members use underscore prefix: `private _internalState`
- TS-ARCH-046: Boolean variables use is/has/can prefix: `isValid`, `hasPermission`

### Module Naming
- TS-ARCH-047: Module folders use kebab-case
- TS-ARCH-048: Feature modules named after domain concept
- TS-ARCH-049: Shared modules have clear, descriptive names
- TS-ARCH-050: No generic names like `utils`, `helpers`, `common`

## File Organization

### File Structure
- TS-ARCH-051: One primary class/type per file
- TS-ARCH-052: Related types can coexist in same file
- TS-ARCH-053: File size limit: no files >500 lines (split if larger)
- TS-ARCH-054: Group related functionality in same directory
- TS-ARCH-055: Explicit boot order - no implicit initialization

### Code Organization Within Files
- TS-ARCH-056: Imports at top
- TS-ARCH-057: Types and interfaces before implementation
- TS-ARCH-058: Constants before variables
- TS-ARCH-059: Public members before private
- TS-ARCH-060: Constructor before methods
- TS-ARCH-061: Static members before instance members

## Dependency Management

### External Dependencies
- TS-ARCH-062: Lock dependency versions (package-lock.json, yarn.lock)
- TS-ARCH-063: Review dependencies before adding (security, size, maintenance)
- TS-ARCH-064: Remove unused dependencies regularly
- TS-ARCH-065: No >25 KB dead dependencies
- TS-ARCH-066: Prefer well-maintained, popular libraries
- TS-ARCH-067: Audit dependencies for vulnerabilities regularly

### Internal Dependencies
- TS-ARCH-068: Minimize coupling between modules
- TS-ARCH-069: Use dependency injection for flexibility
- TS-ARCH-070: Program to interfaces, not implementations
- TS-ARCH-071: Follow dependency inversion principle
- TS-ARCH-072: Use composition over inheritance

## Configuration Management

### Config Files
- TS-ARCH-073: Single source of truth for configuration
- TS-ARCH-074: Environment-specific config files
- TS-ARCH-075: Validate configuration at startup
- TS-ARCH-076: Type-safe configuration with schemas
- TS-ARCH-077: No magic numbers - use named constants

### tsconfig.json
- TS-ARCH-078: Enable strict mode
- TS-ARCH-079: Configure path aliases
- TS-ARCH-080: Set appropriate target and module
- TS-ARCH-081: Enable source maps for debugging
- TS-ARCH-082: Configure proper module resolution

## Documentation

### Code Documentation
- TS-ARCH-083: JSDoc on all exported functions and types
- TS-ARCH-084: Document public APIs thoroughly
- TS-ARCH-085: Include @example tags for exported functions
- TS-ARCH-086: Document complex algorithms and business logic
- TS-ARCH-087: Keep documentation close to code

### Architecture Documentation
- TS-ARCH-088: Maintain architecture decision records (ADRs)
- TS-ARCH-089: Document layer boundaries and dependencies
- TS-ARCH-090: Document module responsibilities
- TS-ARCH-091: Keep diagrams updated
- TS-ARCH-092: Document build and deployment process

## Testing Structure

### Test Organization
- TS-ARCH-093: Mirror source structure in test files
- TS-ARCH-094: Co-locate tests with source files or in parallel `__tests__` directory
- TS-ARCH-095: Unit tests in `.test.ts` files
- TS-ARCH-096: Integration tests in separate directory
- TS-ARCH-097: E2E tests in dedicated folder
- TS-ARCH-098: Test fixtures and mocks in dedicated folders

## Build & Deployment

### Build Configuration
- TS-ARCH-099: Separate build configs for dev/prod
- TS-ARCH-100: Tree shaking enabled for production builds
- TS-ARCH-101: Source maps for debugging
- TS-ARCH-102: Type checking in CI/CD pipeline
- TS-ARCH-103: Linting in CI/CD pipeline

### Code Quality
- TS-ARCH-104: Enforce with ESLint rules
- TS-ARCH-105: Format with Prettier
- TS-ARCH-106: Pre-commit hooks for quality checks
- TS-ARCH-107: Code coverage minimum thresholds
- TS-ARCH-108: No warnings in production builds

## Monorepo Patterns

### Workspace Organization (if applicable)
- TS-ARCH-109: Clear package boundaries
- TS-ARCH-110: Shared config at root
- TS-ARCH-111: Package-specific config in package folders
- TS-ARCH-112: Enforce dependency rules between packages
- TS-ARCH-113: Shared build scripts

## Anti-Patterns

### Forbidden Practices
- TS-ARCH-114: No God objects or God modules
- TS-ARCH-115: No circular dependencies
- TS-ARCH-116: No tight coupling between modules
- TS-ARCH-117: No hidden dependencies (globals)
- TS-ARCH-118: No business logic in infrastructure layer
- TS-ARCH-119: No infrastructure dependencies in domain layer
- TS-ARCH-120: No mutable global state
- TS-ARCH-121: No side effects in module initialization

## Activation Criteria
Use these patterns when:
- Setting up new TypeScript projects
- Refactoring existing codebases
- Defining module boundaries and dependencies
- Establishing naming and organization conventions
