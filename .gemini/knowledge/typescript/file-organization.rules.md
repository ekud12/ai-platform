# TypeScript File Organization Rules

## Purpose

Standards for file and folder organization in TypeScript projects including module structure, barrel exports, and project layouts.

## Authority

Governs all TypeScript project structures. Consistent organization is mandatory.

## Scope

Applies to folder structure, file naming, import organization, and module boundaries.

---

## TS-FILE-001 — Project Root Structure

**Severity: Major**

**Rule**
Projects MUST follow standard folder layout at root level.

**Bad Pattern**
```
app.ts
utils.ts
order.ts
package.json
```

**Good Pattern**
```
src/
  features/
  shared/
  main.ts
tests/
  unit/
  integration/
dist/
package.json
tsconfig.json
```

**Rationale**
Standard structure enables quick navigation and tooling configuration.

---

## TS-FILE-002 — Source Organization

**Severity: Major**

**Rule**
Source code MUST be in `src/` with clear separation of features and shared code.

**Good Pattern**
```
src/
  features/
    orders/
    users/
    payments/
  shared/
    utils/
    logger/
    config/
  main.ts
  app.ts
```

**Rationale**
Feature/shared separation enforces proper module boundaries.

---

## TS-FILE-003 — File Naming with Suffix

**Severity: Major**

**Rule**
Files MUST use kebab-case with purpose suffix indicating type.

**Standard Suffixes**
- `.service.ts` - Business logic services
- `.controller.ts` - HTTP controllers/handlers
- `.repository.ts` - Data access layer
- `.types.ts` - Type definitions
- `.schema.ts` - Validation schemas (zod, etc.)
- `.guard.ts` - Auth/validation guards
- `.middleware.ts` - Express/Fastify middleware
- `.test.ts` or `.spec.ts` - Test files
- `.mock.ts` - Mock implementations
- `.constants.ts` - Constant values

**Bad Pattern**
```
OrderService.ts
orders.ts
orderHelpers.ts
```

**Good Pattern**
```
order.service.ts
order.controller.ts
order.types.ts
order.schema.ts
order.service.test.ts
```

**Rationale**
Suffixes immediately communicate file purpose without opening it.

---

## TS-FILE-004 — Type File Organization

**Severity: Major**

**Rule**
Types MUST be organized by scope: local types co-located, shared types in `types/` folder.

**Bad Pattern**
```
types/
  everything.ts  // All types in one file
```

**Good Pattern**
```
src/
  features/orders/
    order.types.ts          // Order-specific types
    order.service.ts        // Uses local types
  shared/
    types/
      common.types.ts       // Shared types (Result, Pagination)
      api.types.ts          // API response types
      index.ts              // Re-exports public types
```

**Rationale**
Co-located types reduce navigation; shared types prevent duplication.

---

## TS-FILE-005 — Barrel Export Files

**Severity: Major**

**Rule**
Use `index.ts` only for explicit public API exports. No `export *` patterns.

**Bad Pattern**
```typescript
// features/orders/index.ts
export * from './order.service';
export * from './order.repository';
export * from './internal-utils'; // Leaks internals
```

**Good Pattern**
```typescript
// features/orders/index.ts
export { OrderService } from './order.service';
export { OrderController } from './order.controller';
export type { Order, OrderDto, CreateOrderRequest } from './order.types';
```

**Rationale**
Explicit exports define clear module boundaries and prevent accidental exposure.

---

## TS-FILE-006 — Test File Co-location

**Severity: Info**

**Rule**
Unit tests SHOULD be co-located with source or in parallel `__tests__` directory.

**Pattern A - Co-located**
```
src/features/orders/
  order.service.ts
  order.service.test.ts
  order.controller.ts
  order.controller.test.ts
```

**Pattern B - Parallel Directory**
```
src/features/orders/
  order.service.ts
  __tests__/
    order.service.test.ts
```

**Rationale**
Co-located tests are easier to find and maintain alongside source code.

---

## TS-FILE-007 — Integration Test Separation

**Severity: Major**

**Rule**
Integration and E2E tests MUST be in separate top-level folders.

**Good Pattern**
```
tests/
  unit/              # Or co-located with source
  integration/
    database.test.ts
    api.test.ts
  e2e/
    user-journey.test.ts
  fixtures/
    test-data.json
  helpers/
    test-utils.ts
```

**Rationale**
Separation enables different test configurations and run strategies.

---

## TS-FILE-008 — Import Organization

**Severity: Major**

**Rule**
Imports MUST be organized in groups: external, internal, relative.

**Bad Pattern**
```typescript
import { OrderService } from './order.service';
import express from 'express';
import { logger } from '@/shared/logger';
import type { Request } from 'express';
import { z } from 'zod';
```

**Good Pattern**
```typescript
// External packages
import express from 'express';
import type { Request, Response } from 'express';
import { z } from 'zod';

// Internal absolute imports
import { logger } from '@/shared/logger';
import { config } from '@/shared/config';

// Relative imports
import { OrderService } from './order.service';
import type { Order } from './order.types';
```

**Rationale**
Organized imports are easier to scan and maintain.

---

## TS-FILE-009 — Type-Only Imports

**Severity: Major**

**Rule**
Use `import type` for type-only imports to enable better tree-shaking.

**Bad Pattern**
```typescript
import { Order, OrderService } from './order';
// If Order is only used as type, OrderService gets imported unnecessarily
```

**Good Pattern**
```typescript
import type { Order } from './order.types';
import { OrderService } from './order.service';
```

**Rationale**
Type-only imports are erased at compile time and don't affect bundle.

---

## TS-FILE-010 — Entry Point Files

**Severity: Major**

**Rule**
Entry points (`index.ts`, `main.ts`, `app.ts`) MUST only contain orchestration, not logic.

**Bad Pattern**
```typescript
// main.ts - too much logic
import express from 'express';

const app = express();

app.get('/orders', async (req, res) => {
  // 50 lines of order logic here
});

app.listen(3000);
```

**Good Pattern**
```typescript
// main.ts - orchestration only
import { createApp } from './app';
import { config } from './config';
import { logger } from './shared/logger';

async function bootstrap(): Promise<void> {
  const app = await createApp();

  app.listen(config.port, () => {
    logger.info('Server started', { port: config.port });
  });
}

bootstrap().catch(console.error);
```

**Rationale**
Clean entry points are testable and clearly show application structure.

---

## TS-FILE-011 — Shared Folder Structure

**Severity: Major**

**Rule**
Shared code MUST be organized by concern, not dumped in generic folders.

**Bad Pattern**
```
shared/
  utils.ts       // Everything dumped here
  helpers.ts     // Vague naming
  common.ts      // Catch-all
```

**Good Pattern**
```
shared/
  config/
    index.ts
    env.schema.ts
  logger/
    index.ts
    logger.service.ts
  http/
    http.client.ts
    http.types.ts
  validation/
    validators.ts
  errors/
    app.error.ts
    error.types.ts
```

**Rationale**
Organized shared code is discoverable and maintainable.

---

## TS-FILE-012 — Package.json Configuration

**Severity: Critical**

**Rule**
All `package.json` files MUST be explicit with complete metadata.

**Bad Pattern**
```json
{
  "name": "app",
  "scripts": {
    "start": "node dist/main.js"
  }
}
```

**Good Pattern**
```json
{
  "name": "@company/order-service",
  "version": "1.0.0",
  "description": "Order management service",
  "type": "module",
  "main": "dist/main.js",
  "types": "dist/main.d.ts",
  "engines": {
    "node": ">=20.0.0"
  },
  "scripts": {
    "build": "tsc",
    "start": "node dist/main.js",
    "dev": "tsx watch src/main.ts",
    "test": "vitest run",
    "test:watch": "vitest",
    "lint": "eslint src/",
    "format": "prettier --write src/"
  },
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.js"
    }
  },
  "files": ["dist"],
  "author": "Company",
  "license": "MIT"
}
```

**Rationale**
Complete package.json enables proper publishing, tooling, and documentation.

---

## TS-FILE-013 — Monorepo Package Structure

**Severity: Major**

**Rule**
Monorepos MUST have clear package boundaries with `apps/` and `packages/` separation.

**Good Pattern**
```
apps/
  web/
    package.json
    src/
  api/
    package.json
    src/
packages/
  shared/
    package.json
    src/
  ui/
    package.json
    src/
package.json
turbo.json
```

**Rationale**
Clear separation enables independent versioning and deployment.

---

## TS-FILE-014 — Declaration Files

**Severity: Info**

**Rule**
Custom type declarations MUST be in `@types/` or `types/` folder with `.d.ts` extension.

**Good Pattern**
```
src/
  @types/
    global.d.ts           // Global type extensions
    env.d.ts              // Environment type declarations
    express.d.ts          // Module augmentations
  types/
    api.types.ts          // Application types (not declarations)
```

**Rationale**
Separate declaration files from runtime type definitions.

---

## Forbidden Patterns

- TS-FILE-FORBID-001: No mixed case file names (use kebab-case only)
- TS-FILE-FORBID-002: No default exports
- TS-FILE-FORBID-003: No `export *` barrel exports
- TS-FILE-FORBID-004: No deeply nested folders (max 4 levels in src)
- TS-FILE-FORBID-005: No `utils.ts` or `helpers.ts` as catch-all
- TS-FILE-FORBID-006: No logic in index.ts files
- TS-FILE-FORBID-007: No circular imports between modules
- TS-FILE-FORBID-008: No relative imports crossing feature boundaries
- TS-FILE-FORBID-009: No minimal package.json without required fields
- TS-FILE-FORBID-010: No business logic in entry point files
