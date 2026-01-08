# TypeScript Monorepo Rules

## Purpose

Standards for pnpm/Turbo monorepo organization.

## Authority

Governs TypeScript monorepos with multiple packages.

## Scope

Applies to workspace configuration, package organization, and build orchestration.

## Constraints

- Packages must be independently versioned
- Dependencies must be explicit
- Builds must be cacheable

## Rule Format

All rules use the TS-MONO prefix.

---

## TS-MONO-001 — Workspace Package Naming
**Severity: Major**

**Rule**
Workspace packages MUST use scoped names: `@apps/{name}` for applications, `@packages/{name}` for shared libraries.

**Rationale**
Scoped names prevent conflicts with npm packages and clearly distinguish internal packages.

**Bad Pattern**
```json
{ "name": "my-logger" }
{ "name": "utils" }
{ "name": "mcp-appointments" }
```

**Good Pattern**
```json
{ "name": "@packages/logger" }
{ "name": "@packages/utils" }
{ "name": "@apps/mcp-appointments" }
```

---

## TS-MONO-002 — Path Aliases for Internal Packages
**Severity: Major**

**Rule**
tsconfig MUST define path aliases for internal packages.

**Rationale**
Path aliases enable clean imports without relative path gymnastics.

**Bad Pattern**
```typescript
import { logger } from "../../../packages/logger/src";
import { utils } from "../../packages/utils/src/index";
```

**Good Pattern**
```json
// tsconfig.json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@packages/*": ["packages/*/src"],
      "@apps/*": ["apps/*/src"]
    }
  }
}
```

```typescript
import { logger } from "@packages/logger";
import { utils } from "@packages/utils";
```

---

## TS-MONO-003 — Turbo Task Definition
**Severity: Major**

**Rule**
Monorepos using Turbo MUST define task dependencies and outputs in `turbo.json`.

**Rationale**
Proper task configuration enables caching and parallel execution.

**Bad Pattern**
```json
// No turbo.json or empty config
{
  "tasks": {}
}
```

**Good Pattern**
```json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**"]
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"]
    },
    "lint": {
      "outputs": []
    },
    "typecheck": {
      "dependsOn": ["^build"],
      "outputs": []
    }
  }
}
```

---

## TS-MONO-004 — Shared Package Structure
**Severity: Major**

**Rule**
Shared packages MUST have consistent structure with src/, dist/, and proper exports.

**Bad Pattern**
```
packages/logger/
├── index.ts        # Source at root
├── logger.ts
└── package.json    # No exports field
```

**Good Pattern**
```
packages/logger/
├── src/
│   ├── index.ts
│   └── logger.ts
├── dist/           # Build output (gitignored)
├── package.json
├── tsconfig.json
└── README.md
```

```json
// package.json
{
  "name": "@packages/logger",
  "version": "1.0.0",
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "import": "./dist/index.js",
      "types": "./dist/index.d.ts"
    }
  },
  "files": ["dist"],
  "scripts": {
    "build": "tsc",
    "typecheck": "tsc --noEmit"
  }
}
```

---

## TS-MONO-005 — Engine Constraints
**Severity: Critical**

**Rule**
Monorepos MUST specify Node and package manager version constraints.

**Rationale**
Prevents "works on my machine" issues and ensures consistent builds.

**Bad Pattern**
```json
// No engine constraints
{
  "name": "@apps/my-app",
  "version": "1.0.0"
}
```

**Good Pattern**
```json
// Root package.json
{
  "name": "my-monorepo",
  "private": true,
  "engines": {
    "node": ">=20.0.0",
    "pnpm": ">=10.0.0"
  },
  "packageManager": "pnpm@10.0.0"
}
```

```
// .npmrc
engine-strict=true
```
