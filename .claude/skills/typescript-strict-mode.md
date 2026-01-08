---
name: typescript-strict-mode
description: TypeScript strict type system rules with zero tolerance for any, mandatory readonly collections, branded types, and exhaustive type checking. Core type safety patterns.
allowed-tools: Read, Write, Edit
---

# TypeScript Strict Type System Rules (Rules Only)

## Type System Directives (Mandatory)

### Forbidden Types
- TS-TYPE-001: Ban `any`, `object`, `{}`, `Function` - all forbidden in any context
- TS-TYPE-002: No open generic `T` without constraints
- TS-TYPE-003: No implicit `any` from missing type annotations
- TS-TYPE-004: No `!` non-null assertions - use safe narrowing or type guards
- TS-TYPE-005: No `as` casting except for branded types or safe narrowing

### Immutability Requirements
- TS-TYPE-006: All arrays must be `readonly` or `readonly T[]`
- TS-TYPE-007: All tuples must be `readonly [T, U, ...]`
- TS-TYPE-008: All constants must use `as const` assertion
- TS-TYPE-009: Deep immutability via `ReadonlyDeep<T>` for shared structures
- TS-TYPE-010: No implicit readonly - all immutability must be explicit

### Type vs Interface
- TS-TYPE-011: Use `type` by default unless structural extension required
- TS-TYPE-012: Use `interface` only when structural inheritance needed
- TS-TYPE-013: No empty interfaces - use `type` with explicit shape

### Explicit Typing
- TS-TYPE-014: Explicit return types mandatory on all exported functions
- TS-TYPE-015: Explicit return types mandatory on all public methods
- TS-TYPE-016: No implicit `undefined` returns - explicit `void` or return type required
- TS-TYPE-017: Use `satisfies` for compile-time contract verification without widening

### Branded Types
- TS-TYPE-018: Brand all domain identifiers: `type UserId = string & { __brand: "UserId" }`
- TS-TYPE-019: Brand all tokens, keys, and system types
- TS-TYPE-020: No raw primitive types for domain concepts (no plain `string` for IDs)

### Template Literal Types
- TS-TYPE-021: Use template literal types for all identifier formats
- TS-TYPE-022: Type-safe string patterns: `type EventName = \`user:\${string}\``
- TS-TYPE-023: Enforce compile-time string validation via template literals

### Discriminated Unions
- TS-TYPE-024: All discriminated unions must have exhaustiveness checks
- TS-TYPE-025: Use `never` type for exhaustiveness validation
- TS-TYPE-026: All switch statements on unions must have `default: never` case
- TS-TYPE-027: Implement `assertUnreachable(x: never)` helper for runtime exhaustiveness

### Generic Constraints
- TS-TYPE-028: All generic type parameters must have constraints
- TS-TYPE-029: No open `<T>` - use `<T extends object>` or specific constraint
- TS-TYPE-030: Conditional types must be factored into utilities, no inline infer chains

### Mapped Types
- TS-TYPE-031: Use `as` for key remapping in mapped types
- TS-TYPE-032: Normalize shapes via mapped type transformations
- TS-TYPE-033: No implicit key preservation without type safety

### Override and Inheritance
- TS-TYPE-034: Mandatory `override` keyword for subclass method overrides
- TS-TYPE-035: No subclassing built-ins without sealing

### Enums
- TS-TYPE-036: No enums unless fully wrapped with namespace
- TS-TYPE-037: Prefer const objects with `as const` over enums
- TS-TYPE-038: If using const enums, must set `preserveConstEnums: true`

### Symbols
- TS-TYPE-039: Use `Symbol()` or `unique symbol` for private capabilities
- TS-TYPE-040: Brand types with symbols for nominal typing

## Runtime Schema & Validation (Enforced)

### Schema Libraries
- TS-VALID-001: Wrap all external data with zod, valibot, or io-ts schemas
- TS-VALID-002: Use `.safeParse()` not `.parse()` - handle errors explicitly
- TS-VALID-003: Derive types from schemas: `type User = z.infer<typeof UserSchema>`
- TS-VALID-004: Never define types by hand when schema exists
- TS-VALID-005: Separate validation logic from model logic

### Validation Boundaries
- TS-VALID-006: All input/output boundaries must use runtime contract validation
- TS-VALID-007: Validate `env.ts` at runtime startup
- TS-VALID-008: No loose shapes: `z.any`, `z.unknown` without guards forbidden
- TS-VALID-009: Runtime inputs must match compile-time types (schema first, type second)
- TS-VALID-010: Extract errors from `.safeParse()` with structured error handling

## Error Handling & Result Types

### Result Pattern
- TS-ERROR-001: Return `Result<T, E>` or discriminated unions for expected failures
- TS-ERROR-002: All errors must be branded with `kind` property
- TS-ERROR-003: Never throw raw `Error` - use domain wrappers or error factories
- TS-ERROR-004: Preserve `cause` on all error throws
- TS-ERROR-005: All error paths must be logged with trace context

## Documentation Requirements

### JSDoc
- TS-DOC-001: JSDoc required on all exported functions, types, and interfaces
- TS-DOC-002: All exported functions must include `@example` tag
- TS-DOC-003: All exported types must include usage examples in comments
- TS-DOC-004: Document type constraints and branded type meanings

## Forbidden Violations

### Absolute Bans
- TS-BAN-001: No `any`, `object`, `Function`, `{}`
- TS-BAN-002: No default exports (named exports only)
- TS-BAN-003: No unwrapped `process.env` access
- TS-BAN-004: No unwrapped `JSON.parse` without schema validation
- TS-BAN-005: No mutable exports
- TS-BAN-006: No implicit returns without explicit type
- TS-BAN-007: No literal type widening
- TS-BAN-008: No dynamic property access without type guarantee
- TS-BAN-009: No `Object.keys/entries` without typed wrappers (`typedKeys`, `typedEntries`)

### Advanced Discipline
- TS-ADV-001: Use `Reflect.*` instead of legacy `Object.*` methods
- TS-ADV-002: No bare `@decorator` logic without lifecycle contracts or metadata
- TS-ADV-003: Decorators must emit metadata via `reflect-metadata` and validate shape
- TS-ADV-004: No `arguments` object - use rest parameters `(...args)` only
- TS-ADV-005: No `==`, `!=`, or `with` - no implicit coercion operations
- TS-ADV-006: No `for..in` over arrays
- TS-ADV-007: All switch blocks must have `default` with `never` exhaustiveness check
- TS-ADV-008: No mutation during iteration

## Activation Criteria
Use these patterns when:
- Implementing type-safe TypeScript code
- Validating external data at boundaries
- Creating domain models and types
- Enforcing compile-time and runtime type safety
