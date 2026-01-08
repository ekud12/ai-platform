# TypeScript Types Rules

## Purpose
Standards for Type Safety in TypeScript.

## Authority
Governs all `.ts` files. Strict typing is mandatory.

---

## TS-TYPES-001 — No Any
**Severity: Critical**

**Rule**
`any` is STRICTLY FORBIDDEN. Use `unknown` if necessary.

**Bad Pattern**
```typescript
function parse(input: any) { ... }
```

**Good Pattern**
```typescript
function parse(input: unknown) { 
    if (typeof input === 'string') { ... }
}
```

---

## TS-TYPES-002 — No Type Assertions
**Severity: Major**

**Rule**
Avoid `as Type` assertions. They hide bugs. Use type guards instead.

**Scope**
This rule covers type casting assertions (`as Type` or `<Type>`). For non-null assertions (`!` operator), see TS-FORBID-002.

**Related Rules**
- TS-FORBID-002 covers non-null assertions (`!`) which are a different mechanism

**Bad Pattern**
```typescript
const user = response as User; // If response is wrong, this crashes later
```

**Good Pattern**
```typescript
if (isUser(response)) {
    const user = response; // Narrowed safely
}
```

---

## TS-TYPES-003 — Readonly by Default
**Severity: Info**

**Rule**
Prefer `readonly` properties to prevent mutation bugs.

**Bad Pattern**
```typescript
interface User { id: string; }
```

**Good Pattern**
```typescript
interface User { readonly id: string; }
```

---

## TS-TYPES-004 — Branded Types
**Severity: Info**

**Rule**
Use "Branded Types" for IDs to prevent mixing them.

**Bad Pattern**
```typescript
type UserId = string;
type OrderId = string;
// Can accidentally pass OrderId to function expecting UserId
```

**Good Pattern**
```typescript
type UserId = string & { __brand: 'UserId' };
type OrderId = string & { __brand: 'OrderId' };
```

---

## TS-TYPES-005 — Discriminated Unions
**Severity: Major**

**Rule**
Use Discriminated Unions for state management.

**Bad Pattern**
```typescript
interface State { isLoading: boolean; error?: string; data?: any; }
```

**Good Pattern**
```typescript
type State = 
  | { status: 'loading' }
  | { status: 'error'; error: string }
  | { status: 'success'; data: any };
```

---

## TS-TYPES-006 — Strict Null Checks
**Severity: Critical**

**Rule**
`strictNullChecks` MUST be enabled. Handle `null`/`undefined`.

**Bad Pattern**
```typescript
user.profile.name // Crash if profile is undefined
```

**Good Pattern**
```typescript
user.profile?.name ?? 'Guest'
```

---

## TS-TYPES-007 — Interface Over Type Alias
**Severity: Info**

**Rule**
Use `interface` for Objects, `type` for Unions.

**Bad Pattern**
```typescript
type User = { name: string };
```

**Good Pattern**
```typescript
interface User { name: string; }
```

---

## TS-TYPES-008 — Generic Constraints
**Severity: Warning**

**Rule**
Generics SHOULD have constraints (`T extends ...`).

**Bad Pattern**
```typescript
function getLength<T>(arg: T) { return arg.length; } // Error
```

**Good Pattern**
```typescript
function getLength<T extends { length: number }>(arg: T) { return arg.length; }
```

---

## TS-TYPES-009 — Utility Types
**Severity: Info**

**Rule**
Use built-in Utilities (`Pick`, `Omit`, `Partial`).

**Bad Pattern**
```typescript
interface PartialUser { name?: string; age?: number; } // Duplicate definition
```

**Good Pattern**
```typescript
type PartialUser = Partial<User>;
```

---

## TS-TYPES-010 — Return Type Annotations
**Severity: Major**

**Rule**
Functions MUST have explicit return types.

**Bad Pattern**
```typescript
export function calculate() { return 42; }
```

**Good Pattern**
```typescript
export function calculate(): number { return 42; }
```

---

## TS-TYPES-011 — Template Literal Types
**Severity: Info**

**Rule**
Use template literal types for string patterns (routes, IDs, events).

**Bad Pattern**
```typescript
type EventName = string; // Any string allowed
function emit(event: EventName) { ... }
emit("typo_event"); // No error
```

**Good Pattern**
```typescript
type EventName = `on${Capitalize<string>}`; // Must start with "on"
// Or explicit union
type EventName = "onClick" | "onHover" | "onSubmit";

function emit(event: EventName) { ... }
emit("onclick"); // Error: should be "onClick"
```

---

## TS-TYPES-012 — Const Type Parameters
**Severity: Info**

**Rule**
Use `const` type parameters for literal inference in generic functions.

**Bad Pattern**
```typescript
function createRoute<T extends string>(path: T) { return { path }; }
const route = createRoute("/users"); // type: { path: string }
```

**Good Pattern**
```typescript
function createRoute<const T extends string>(path: T) { return { path }; }
const route = createRoute("/users"); // type: { path: "/users" }
```

---

## TS-TYPES-013 — Satisfies Operator
**Severity: Major**

**Rule**
Use `satisfies` to validate types without widening. Prefer over `as const` when validating shape.

**Bad Pattern**
```typescript
const config: Config = { port: 3000, host: "localhost" };
// Type is Config - loses literal types

const config2 = { port: 3000, host: "localhost" } as const;
// Doesn't validate against Config interface
```

**Good Pattern**
```typescript
const config = {
    port: 3000,
    host: "localhost"
} satisfies Config;
// Validates shape AND preserves literal types
```

---

## TS-TYPES-014 — No Object/Function Types
**Severity: Critical**

**Rule**
Never use `Object`, `Function`, `{}` as types. Use specific shapes or `unknown`.

**Bad Pattern**
```typescript
function process(data: Object) { ... }
function handle(callback: Function) { ... }
function accept(value: {}) { ... }
```

**Good Pattern**
```typescript
function process(data: Record<string, unknown>) { ... }
function handle(callback: () => void) { ... }
function accept(value: unknown) { ... }
```

---

## TS-TYPES-015 — Zod Schema for Runtime Validation
**Severity: Info**

**Rule**
External data (API responses, form inputs) SHOULD use Zod schemas for runtime validation.

**Rationale**
TypeScript types disappear at runtime. Zod provides runtime validation with type inference, catching invalid data at system boundaries.

**Note**
This is a recommendation, not a requirement. Teams may choose alternative validation approaches.

**Pattern Without Zod**
```typescript
interface User {
    id: number;
    name: string;
    email: string;
}

// No runtime validation - trusts external data
const user: User = await response.json();
```

**Recommended Pattern**
```typescript
import { z } from "zod";

const UserSchema = z.object({
    id: z.number(),
    name: z.string().min(1),
    email: z.string().email()
});

type User = z.infer<typeof UserSchema>;

// Runtime validation at system boundary
const user = UserSchema.parse(await response.json());
```

---

## TS-TYPES-016 — Infer Types from Schemas
**Severity: Info**

**Rule**
When using Zod, types SHOULD be inferred from schemas rather than manually duplicated.

**Rationale**
Inferring types from schemas ensures runtime validation and compile-time types stay in sync. Manual duplication leads to drift.

**Note**
This is a recommendation for projects already using Zod. It is not a requirement to adopt Zod.

**Pattern With Duplication**
```typescript
// Manual interface - can drift from schema
interface CreateUserInput {
    name: string;
    email: string;
    age?: number;
}

const CreateUserSchema = z.object({
    name: z.string(),
    email: z.string().email(),
    age: z.number().optional()
});
// Schema and interface can become inconsistent
```

**Recommended Pattern**
```typescript
const CreateUserSchema = z.object({
    name: z.string().min(1),
    email: z.string().email(),
    age: z.number().min(0).optional()
});

// Single source of truth
type CreateUserInput = z.infer<typeof CreateUserSchema>;

// Use in functions
function createUser(input: CreateUserInput): void {
    const validated = CreateUserSchema.parse(input);
    // ...
}
```