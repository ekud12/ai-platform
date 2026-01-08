# TypeScript Architecture Rules

## Purpose

Standards for project structure, module organization, layer boundaries, naming conventions, and architectural patterns.

## Authority

Governs all TypeScript project architecture. Consistent organization is mandatory.

## Scope

Applies to folder structure, imports, exports, dependencies, and module boundaries.

---

## TS-ARCH-001 — Feature-First Organization

**Severity: Major**

**Rule**
Organize code by feature/domain, not by technical layer. Each feature is self-contained.

**Bad Pattern**
```
src/
  controllers/
    orderController.ts
    userController.ts
  services/
    orderService.ts
    userService.ts
  repositories/
    orderRepository.ts
    userRepository.ts
```

**Good Pattern**
```
src/
  features/
    orders/
      order.controller.ts
      order.service.ts
      order.repository.ts
      order.types.ts
      order.schema.ts
    users/
      user.controller.ts
      user.service.ts
```

**Rationale**
Feature-first keeps related code together and reduces navigation across the codebase.

---

## TS-ARCH-002 — Aliased Imports

**Severity: Critical**

**Rule**
Use path aliases for imports. No relative path traversals like `../../../`.

**Bad Pattern**
```typescript
import { UserService } from '../../../services/user.service';
import { OrderDto } from '../../types/order.types';
```

**Good Pattern**
```typescript
import { UserService } from '@/features/users/user.service';
import { OrderDto } from '@/features/orders/order.types';
import { logger } from '@/shared/logger';
```

**tsconfig.json**
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@/shared/*": ["src/shared/*"],
      "@/features/*": ["src/features/*"]
    }
  }
}
```

**Rationale**
Path aliases are readable, refactor-friendly, and eliminate path confusion.

---

## TS-ARCH-003 — Named Exports Only

**Severity: Critical**

**Rule**
Use named exports exclusively. Default exports are FORBIDDEN.

**Bad Pattern**
```typescript
// order.service.ts
export default class OrderService { }

// Usage
import OrderService from './order.service'; // Different names possible
import Order from './order.service'; // Inconsistent naming
```

**Good Pattern**
```typescript
// order.service.ts
export class OrderService { }

// Usage
import { OrderService } from './order.service'; // Always consistent
```

**Rationale**
Named exports ensure consistent naming, better tree-shaking, and cleaner refactoring.

---

## TS-ARCH-004 — No Circular Imports

**Severity: Critical**

**Rule**
The import graph MUST be acyclic. Circular dependencies are FORBIDDEN.

**Bad Pattern**
```typescript
// order.service.ts
import { UserService } from './user.service';

// user.service.ts
import { OrderService } from './order.service'; // Circular!
```

**Good Pattern**
```typescript
// Extract shared interface
// order.types.ts
export interface IOrderLookup {
  getOrdersByUser(userId: string): Promise<Order[]>;
}

// user.service.ts - depends on interface, not implementation
import type { IOrderLookup } from './order.types';

export class UserService {
  constructor(private orderLookup: IOrderLookup) {}
}
```

**Rationale**
Circular imports cause runtime issues, initialization problems, and indicate poor design.

---

## TS-ARCH-005 — Layer Boundaries

**Severity: Major**

**Rule**
Lower layers MUST NOT import from higher layers. Dependency flows downward only.

**Layer Hierarchy (top to bottom)**
1. Presentation (controllers, routes)
2. Application (use cases, services)
3. Domain (entities, value objects)
4. Infrastructure (database, external APIs)

**Bad Pattern**
```typescript
// domain/order.entity.ts
import { OrderRepository } from '../infrastructure/order.repository'; // Upward violation!
```

**Good Pattern**
```typescript
// domain/order.entity.ts - pure domain, no infrastructure deps
export class Order {
  readonly id: string;
  readonly items: readonly OrderItem[];
}

// infrastructure/order.repository.ts - can import from domain
import { Order } from '../domain/order.entity';

export class OrderRepository {
  async save(order: Order): Promise<void> { }
}
```

**Rationale**
Strict layering prevents coupling and enables testing/replacement of components.

---

## TS-ARCH-006 — Shared Module Location

**Severity: Major**

**Rule**
Shared code MUST live in `@/shared` or `@/core`. No direct imports between sibling features.

**Bad Pattern**
```typescript
// features/orders/order.service.ts
import { validateEmail } from '../users/user.utils'; // Cross-feature import!
```

**Good Pattern**
```typescript
// shared/validation/email.validator.ts
export function validateEmail(email: string): boolean { }

// features/orders/order.service.ts
import { validateEmail } from '@/shared/validation/email.validator';
```

**Rationale**
Shared modules prevent hidden coupling between features.

---

## TS-ARCH-007 — File Naming Convention

**Severity: Major**

**Rule**
Files MUST use kebab-case with purpose suffix: `.service.ts`, `.controller.ts`, `.types.ts`.

**Bad Pattern**
```
OrderService.ts
orderservice.ts
order_service.ts
order.ts (ambiguous purpose)
```

**Good Pattern**
```
order.service.ts
order.controller.ts
order.repository.ts
order.types.ts
order.schema.ts
order.test.ts
```

**Rationale**
Consistent naming enables quick identification of file purpose.

---

## TS-ARCH-008 — Type Naming Convention

**Severity: Major**

**Rule**
Types use PascalCase. Interfaces prefix with `I` only for contracts (not data shapes).

**Bad Pattern**
```typescript
type orderDto = { }; // camelCase
interface IOrderDto { } // I prefix on data shape
type ORDER_STATUS = 'pending'; // SCREAMING_CASE
```

**Good Pattern**
```typescript
type OrderDto = { };
type OrderStatus = 'pending' | 'shipped';

// I prefix only for behavioral contracts
interface IOrderRepository {
  save(order: Order): Promise<void>;
}
```

**Rationale**
Consistent naming improves readability and distinguishes interfaces from types.

---

## TS-ARCH-009 — Variable and Function Naming

**Severity: Major**

**Rule**
Variables and functions use camelCase. Constants use SCREAMING_SNAKE_CASE.

**Bad Pattern**
```typescript
const MaxRetries = 3; // PascalCase constant
function ProcessOrder() { } // PascalCase function
const ORDER_SERVICE = new OrderService(); // SCREAMING for instance
```

**Good Pattern**
```typescript
const MAX_RETRIES = 3;
const DEFAULT_TIMEOUT_MS = 5000;

function processOrder(): void { }
const orderService = new OrderService();
```

**Rationale**
Case conventions communicate identifier purpose at a glance.

---

## TS-ARCH-010 — Index Files for Public API

**Severity: Major**

**Rule**
Use `index.ts` only to define public API of a module. No logic in index files.

**Bad Pattern**
```typescript
// features/orders/index.ts
export * from './order.service';
export * from './order.repository';
export * from './order.types';
export * from './internal-helpers'; // Exposes internals!

// Or worse - logic in index
export function createOrder() { } // Logic doesn't belong here
```

**Good Pattern**
```typescript
// features/orders/index.ts - explicit public API
export { OrderService } from './order.service';
export { OrderController } from './order.controller';
export type { Order, OrderDto, CreateOrderRequest } from './order.types';
// Internal helpers NOT exported
```

**Rationale**
Explicit exports define clear module boundaries and prevent internal leakage.

---

## TS-ARCH-011 — File Size Limits

**Severity: Info**

**Rule**
Files SHOULD NOT exceed 500 lines. Split large files into focused modules.

**Bad Pattern**
```typescript
// order.service.ts - 1500 lines with everything
export class OrderService {
  // All order logic, validation, mapping, etc.
}
```

**Good Pattern**
```typescript
// order.service.ts - orchestration only
// order.validator.ts - validation logic
// order.mapper.ts - mapping logic
// order.calculator.ts - calculation logic
```

**Rationale**
Smaller files are easier to navigate, review, and maintain.

---

## TS-ARCH-012 — Dependency Injection

**Severity: Major**

**Rule**
Dependencies MUST be injected via constructor. No direct instantiation of dependencies.

**Bad Pattern**
```typescript
export class OrderService {
  private userService = new UserService(); // Direct instantiation
  private logger = console; // Global dependency

  async process(): Promise<void> {
    const user = await this.userService.getUser();
  }
}
```

**Good Pattern**
```typescript
export class OrderService {
  constructor(
    private readonly userService: IUserService,
    private readonly logger: ILogger
  ) {}

  async process(): Promise<void> {
    const user = await this.userService.getUser();
  }
}
```

**Rationale**
DI enables testing, loose coupling, and runtime configuration.

---

## TS-ARCH-013 — Configuration Management

**Severity: Major**

**Rule**
Configuration MUST be validated at startup and accessed via typed config module.

**Bad Pattern**
```typescript
// Scattered process.env access
const port = process.env.PORT || 3000;
const dbUrl = process.env.DATABASE_URL; // Might be undefined!
```

**Good Pattern**
```typescript
// config/env.schema.ts
import { z } from 'zod';

const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']),
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.string().url(),
  REDIS_URL: z.string().url().optional()
});

export type Env = z.infer<typeof envSchema>;

// config/index.ts
const result = envSchema.safeParse(process.env);
if (!result.success) {
  console.error('Invalid configuration:', result.error.issues);
  process.exit(1);
}

export const config = Object.freeze(result.data);
```

**Rationale**
Validated configuration fails fast and prevents runtime config errors.

---

## TS-ARCH-014 — No Mutable Global State

**Severity: Critical**

**Rule**
Mutable global state is FORBIDDEN. Use dependency injection or module-scoped constants.

**Bad Pattern**
```typescript
// globals.ts
export let currentUser: User | null = null;
export let requestCount = 0;

// Mutated anywhere
import { currentUser } from './globals';
currentUser = newUser;
```

**Good Pattern**
```typescript
// Immutable module constants
export const CONFIG = Object.freeze({
  maxRetries: 3,
  timeout: 5000
});

// Request-scoped state via AsyncLocalStorage
const requestContext = new AsyncLocalStorage<RequestContext>();
```

**Rationale**
Global mutable state causes race conditions, testing difficulties, and hidden coupling.

---

## TS-ARCH-015 — Explicit Boot Order

**Severity: Major**

**Rule**
Application initialization MUST have explicit order. No side effects on import.

**Bad Pattern**
```typescript
// database.ts
import { createPool } from 'pg';
export const pool = createPool(config); // Runs on import!

// Any file importing this causes connection
```

**Good Pattern**
```typescript
// database.ts
import { Pool, createPool } from 'pg';

let pool: Pool | null = null;

export async function initDatabase(config: DbConfig): Promise<Pool> {
  if (pool) return pool;
  pool = createPool(config);
  await pool.connect(); // Verify connection
  return pool;
}

export function getPool(): Pool {
  if (!pool) throw new Error('Database not initialized');
  return pool;
}

// main.ts - explicit initialization order
await initDatabase(config.database);
await initCache(config.redis);
await startServer(config.port);
```

**Rationale**
Explicit initialization enables testing, error handling, and controlled startup.

---

## Forbidden Patterns

- TS-ARCH-FORBID-001: No default exports
- TS-ARCH-FORBID-002: No circular imports
- TS-ARCH-FORBID-003: No relative path traversals (`../../../`)
- TS-ARCH-FORBID-004: No cross-feature direct imports
- TS-ARCH-FORBID-005: No upward layer violations
- TS-ARCH-FORBID-006: No mutable global state
- TS-ARCH-FORBID-007: No side effects on import
- TS-ARCH-FORBID-008: No logic in index.ts files
- TS-ARCH-FORBID-009: No `export *` re-exports (explicit exports only)
- TS-ARCH-FORBID-010: No direct process.env access outside config module
