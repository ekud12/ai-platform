# TypeScript Runtime Rules

## Purpose

This rulebook defines standards for runtime safety in TypeScript. Type erasure means runtime validation is essential.

## Authority

These rules govern runtime data handling and validation in TypeScript applications.

## Scope

Applies to all external data, environment variables, and runtime type checking.

## Constraints

- Types are erased at runtime
- External data must be validated
- Environment must be validated at startup

## Rule Format

All rules use the TS-RUNTIME prefix.

---

## TS-RUNTIME-001 — Schema Validation

**Rule**
All external data must be validated against a schema using zod, io-ts, or equivalent.

**Rationale**
TypeScript types do not exist at runtime. External data could be anything; validation provides runtime safety.

**Enforcement**
API responses must be parsed through schemas. User input must be validated. Schema must match TypeScript types.

---

## TS-RUNTIME-002 — Environment Validation

**Rule**
Environment variables must be validated at application startup using typed schemas.

**Rationale**
Missing or malformed environment variables cause runtime failures. Early validation provides clear error messages.

**Enforcement**
Environment schema must be defined. Startup must validate all required variables. Missing variables must fail fast.

---

## TS-RUNTIME-003 — Parse Don't Validate

**Rule**
Validation must return typed objects, not booleans. Use parsing functions that transform and type.

**Rationale**
Boolean validation loses type information. Parsing produces typed results that carry validation guarantees.

**Enforcement**
Validation functions must return parsed types. Boolean validation must be refactored. Type guards must narrow types.

---

## TS-RUNTIME-004 — Fail Fast

**Rule**
Invalid data must cause immediate, clear failures. Silent coercion is forbidden.

**Rationale**
Silent failures propagate invalid data through the system. Early failure with clear messages enables quick fixes.

**Enforcement**
Validation failures must throw or return errors. Coercion must be explicit and documented. Error messages must be actionable.

---

## TS-RUNTIME-005 — Type Guards

**Rule**
Runtime type narrowing must use type guard functions, not type assertions.

**Rationale**
Type guards perform actual runtime checks. Assertions assume correctness without verification.

**Enforcement**
Type narrowing must use is functions or in operator. User-defined type guards must have implementations. Assertions require justification.

---

## TS-RUNTIME-006 — Safe JSON Parsing

**Rule**
JSON.parse must be wrapped in try-catch or use safe parsing utilities.

**Rationale**
JSON.parse throws on invalid input. Uncaught parse errors crash applications.

**Enforcement**
Direct JSON.parse must have error handling. Safe parsing utilities must be used. Parse results must be validated.

---

## TS-RUNTIME-007 — Null Object Pattern

**Rule**
Functions returning potentially missing values must use Option pattern or explicit null returns.

**Rationale**
Undefined from object access is ambiguous. Explicit patterns document absence and prevent bugs.

**Enforcement**
Lookup functions must return null or Option. Undefined must not be used for absence. Code review must verify patterns.

---

## TS-RUNTIME-008 — Exhaustive Switches

**Rule**
Switch statements on discriminated unions must be exhaustive with never default case.

**Rationale**
Exhaustive switches catch missing cases at compile time. The never check ensures all variants are handled.

**Enforcement**
Switches on unions must have exhaustiveness check. Default cases must assert never. New variants cause compile errors.

---

## TS-RUNTIME-009 — Config Modules

**Rule**
Configuration must be loaded through typed modules with validation, not scattered process.env access.

**Rationale**
Centralized config enables validation, typing, and documentation. Scattered access makes configuration hard to understand.

**Enforcement**
Config modules must export typed objects. Direct process.env access is forbidden outside config. Config must be validated at load.

---

## TS-RUNTIME-010 — Error Types

**Rule**
Custom errors must extend Error class and include structured metadata.

**Rationale**
Structured errors enable programmatic handling. instanceof checks work correctly with proper extension.

**Enforcement**
Custom errors must extend Error. Error properties must be typed. Error handling must use structured data.

---

## TS-RUNTIME-011 — Safe Property Access

**Rule**
Use `Object.hasOwn()` instead of `in` operator or `hasOwnProperty` for property checks.

**Rationale**
`in` checks prototype chain. `hasOwnProperty` can be overridden. `Object.hasOwn()` is safe and explicit.

**Enforcement**
ESLint must flag `in` operator for object checks. `hasOwnProperty` calls must be replaced. Code review must verify safe access.

---

## TS-RUNTIME-012 — BigInt for Large Numbers

**Rule**
Use `BigInt` for integers exceeding `Number.MAX_SAFE_INTEGER` (2^53 - 1).

**Rationale**
JavaScript numbers lose precision beyond safe integer range. Financial and ID calculations can produce wrong results.

**Enforcement**
Large integer operations must use BigInt. Database IDs over 53 bits must use string or BigInt. Code review must verify precision.
