---
name: typescript-file-organization
description: File and folder organization patterns for TypeScript projects including module structure, barrel exports, and project layouts.
allowed-tools: Read, Write, Edit
---

# TypeScript File Organization (Rules Only)

## Project Structure
- TS-FILE-001: Source code in `src/` folder
- TS-FILE-002: Tests in `__tests__/` or `tests/` folder
- TS-FILE-003: Types/declarations in `types/` or `@types/` folder
- TS-FILE-004: Build output in `dist/` or `build/` folder
- TS-FILE-005: Configuration files at project root

## Module Organization
- TS-MOD-001: Organize by feature, not by type
- TS-MOD-002: Structure: `src/features/orders/`, `src/features/users/`
- TS-MOD-003: Each feature self-contained with own types, utils, tests
- TS-MOD-004: Shared code in `src/shared/` or `src/common/`
- TS-MOD-005: Prefer vertical slices over horizontal layers

## File Naming
- TS-NAME-001: Use kebab-case for files: `order-processor.ts`
- TS-NAME-002: Match primary export: `order-processor.ts` exports `OrderProcessor`
- TS-NAME-003: Type files: `order.types.ts` or `order.d.ts`
- TS-NAME-004: Test files: `order-processor.test.ts` or `order-processor.spec.ts`
- TS-NAME-005: Index files: `index.ts` for barrel exports

## Barrel Exports
- TS-BARREL-001: Use `index.ts` to re-export module public API
- TS-BARREL-002: Keep barrel exports flat and explicit
- TS-BARREL-003: Avoid deep re-exports (causes bundling issues)
- TS-BARREL-004: Export types separately: `export type { OrderDto }`
- TS-BARREL-005: One barrel per feature/module boundary

## Type Files
- TS-TYPE-FILE-001: Co-locate types with implementation when small
- TS-TYPE-FILE-002: Separate `.types.ts` file for complex/shared types
- TS-TYPE-FILE-003: Global types in `src/types/` or `src/@types/`
- TS-TYPE-FILE-004: Declaration files (`.d.ts`) for external types
- TS-TYPE-FILE-005: Schema types adjacent to schemas: `order.schema.ts`

## Component Organization (React/Vue)
- TS-COMP-001: Component folder: `Button/index.tsx`, `Button/Button.tsx`
- TS-COMP-002: Styles co-located: `Button/Button.styles.ts`
- TS-COMP-003: Tests co-located: `Button/Button.test.tsx`
- TS-COMP-004: Types co-located: `Button/Button.types.ts`
- TS-COMP-005: Hooks in `hooks/` folder or co-located with component

## API/Backend Structure
- TS-API-001: Routes in `routes/` or `api/` folder
- TS-API-002: Controllers/handlers in `controllers/` or `handlers/`
- TS-API-003: Services in `services/` folder
- TS-API-004: Middleware in `middleware/` folder
- TS-API-005: Validators in `validators/` or co-located with routes

## Shared/Common Files
- TS-SHARED-001: `src/shared/utils/` for utility functions
- TS-SHARED-002: `src/shared/constants/` for constants
- TS-SHARED-003: `src/shared/hooks/` for shared hooks
- TS-SHARED-004: `src/shared/components/` for shared components
- TS-SHARED-005: Keep shared folder flat, avoid deep nesting

## Configuration Files
- TS-CFG-001: `tsconfig.json` at project root
- TS-CFG-002: Path aliases in tsconfig: `@/` for `src/`
- TS-CFG-003: Environment config in `src/config/` folder
- TS-CFG-004: Separate configs: `tsconfig.build.json`, `tsconfig.test.json`

## Test Organization
- TS-TEST-001: Co-locate tests with source: `order.ts`, `order.test.ts`
- TS-TEST-002: Or mirror structure in `__tests__/` folder
- TS-TEST-003: Test fixtures in `__fixtures__/` or `fixtures/`
- TS-TEST-004: Test utilities in `test-utils/` or `testing/`
- TS-TEST-005: E2E tests in `e2e/` or `tests/e2e/`

## Import Organization
- TS-IMPORT-001: External imports first (node_modules)
- TS-IMPORT-002: Internal absolute imports second (`@/features/...`)
- TS-IMPORT-003: Relative imports last (`./utils`)
- TS-IMPORT-004: Type imports separate: `import type { ... }`
- TS-IMPORT-005: Sort imports alphabetically within groups

## Entry Points
- TS-ENTRY-001: `src/index.ts` as main entry for libraries
- TS-ENTRY-002: `src/main.ts` or `src/app.ts` for applications
- TS-ENTRY-003: Export public API from entry point
- TS-ENTRY-004: Keep entry point minimal - orchestration only

## Monorepo Structure
- TS-MONO-001: Packages in `packages/` folder
- TS-MONO-002: Apps in `apps/` folder
- TS-MONO-003: Shared packages: `packages/shared/`, `packages/ui/`
- TS-MONO-004: Workspace root for shared tooling
- TS-MONO-005: Package-specific tsconfig extending root

## Declaration Files
- TS-DECL-001: Ambient declarations in `src/types/` or `@types/`
- TS-DECL-002: Module augmentations co-located or in types folder
- TS-DECL-003: Generated types in `src/generated/` folder
- TS-DECL-004: API types from codegen separate from hand-written

## Package Configuration (package.json)
- TS-PKG-001: ALWAYS write explicit, fully-configured `package.json` files
- TS-PKG-002: Include ALL relevant fields with complete metadata
- TS-PKG-003: Required fields: name, version, description, type, main, types, scripts
- TS-PKG-004: Include author, license, repository, keywords, engines
- TS-PKG-005: Define exports map for modern module resolution
- TS-PKG-006: Version all dependencies explicitly (no `*` or `latest`)
- TS-PKG-007: Separate dependencies, devDependencies, peerDependencies correctly
- TS-PKG-008: Include comprehensive scripts for build, test, lint, format
- TS-PKG-009: Add files array to control published content

## Forbidden Patterns
- TS-FILE-FORBID-001: No circular imports between modules
- TS-FILE-FORBID-002: No default exports (prefer named exports)
- TS-FILE-FORBID-003: No barrel files re-exporting everything (`export *`)
- TS-FILE-FORBID-004: No deeply nested folders (max 4 levels in src)
- TS-FILE-FORBID-005: No mixing concerns in single file
- TS-FILE-FORBID-006: No `any` in type files
- TS-FILE-FORBID-007: No relative imports crossing feature boundaries
- TS-FILE-FORBID-008: No `utils.ts` as catch-all dumping ground
- TS-FILE-FORBID-009: No minimal `package.json` - always explicit configuration
