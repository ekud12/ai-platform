# TypeScript Forbidden Patterns Rules

## Purpose

This rulebook explicitly defines patterns that are banned from TypeScript codebases. These patterns cause problems and must not be used.

## Authority

These rules define absolute prohibitions. No exception mechanism exists for forbidden patterns.

## Scope

Applies to all TypeScript code without exception.

## Constraints

- Forbidden patterns must be eliminated
- Legacy code must be refactored
- No new code may use forbidden patterns

## Rule Format

All rules use the TS-FORBID prefix.

---

## TS-FORBID-001 — No Implicit Any

**Rule**
Implicit any from missing type annotations is forbidden.

**Rationale**
Implicit any silently disables type checking. It creates type-unsafe code without explicit acknowledgment.

**Enforcement**
tsconfig must enable noImplicitAny. Build must fail on implicit any. Explicit types required everywhere.

---

## TS-FORBID-002 — No Non-Null Assertions

**Rule**
Non-null assertions (`!` operator) are forbidden except in tests.

**Scope**
This rule covers the postfix `!` operator that asserts a value is not null/undefined. For type casting assertions (`as Type`), see TS-TYPES-002.

**Related Rules**
- TS-TYPES-002 covers type assertions (`as Type`) which are a different mechanism

**Rationale**
Non-null assertions bypass null checks. They can cause runtime errors that TypeScript should prevent.

**Enforcement**
ESLint @typescript-eslint/no-non-null-assertion must be enabled. Proper null handling must be used. Exceptions for test assertions only.

---

## TS-FORBID-003 — No ts-ignore

**Rule**
@ts-ignore comments are forbidden. Use @ts-expect-error with explanation if suppression is necessary.

**Rationale**
ts-ignore silently suppresses all errors. ts-expect-error fails if the error disappears, ensuring intentionality.

**Enforcement**
ESLint must flag ts-ignore. ts-expect-error must have explanation. Suppressions must be minimized.

---

## TS-FORBID-004 — No Namespace

**Rule**
TypeScript namespaces are forbidden. Use ES modules.

**Rationale**
Namespaces are a legacy pattern. ES modules are the standard for code organization.

**Enforcement**
Build must reject namespace declarations. Imports must use ES module syntax. Migration required for legacy code.

---

## TS-FORBID-005 — No Enums

**Rule**
TypeScript enums are forbidden. Use const objects with as const.

**Rationale**
Enums have unexpected runtime behavior and type issues. Const objects are simpler and more predictable.

**Enforcement**
ESLint must flag enum declarations. Const objects must be used instead. Code review must reject enums.

---

## TS-FORBID-006 — No Boolean Trap

**Rule**
Functions with multiple boolean parameters are forbidden.

**Rationale**
Boolean parameters are unclear at call sites. Object parameters with named properties are self-documenting.

**Enforcement**
Code review must identify boolean traps. Options objects must be used. Boolean parameters must be refactored.

---

## TS-FORBID-007 — No Default Export

**Rule**
Default exports are forbidden. Use named exports only.

**Rationale**
Default exports break refactoring and import consistency. Named exports ensure the same name is used everywhere.

**Enforcement**
ESLint must flag default exports. Named exports must be used. IDE settings must prefer named imports.

---

## TS-FORBID-008 — No Class Properties Without Modifier

**Rule**
Class properties must have explicit access modifiers (public, private, protected).

**Rationale**
Implicit public is unclear. Explicit modifiers document intent and encapsulation.

**Enforcement**
ESLint must require modifiers. Code review must verify explicitness. TypeScript strict mode enforced.

---

## TS-FORBID-009 — No Require

**Rule**
require() is forbidden. Use ES import syntax.

**Rationale**
Require is CommonJS syntax incompatible with tree shaking. ES imports enable static analysis.

**Enforcement**
ESLint must flag require. Dynamic imports must use import(). CommonJS must be avoided.

---

## TS-FORBID-010 — No Object Mutation

**Rule**
Object mutation in shared state is forbidden. Use immutable update patterns.

**Rationale**
Mutation creates bugs in React, Redux, and concurrent code. Immutable updates are predictable and traceable.

**Enforcement**
ESLint must flag mutation operators. Spread operator or immer must be used. Code review must verify immutability.

---

## TS-FORBID-011 — No Prototype Modification

**Rule**
Modifying built-in prototypes (`Array.prototype`, `String.prototype`, etc.) is forbidden.

**Rationale**
Prototype pollution affects all code including third-party libraries. It causes unpredictable behavior and security issues.

**Enforcement**
ESLint no-extend-native must be enabled. Code review must reject prototype modifications. Utility functions must be used instead.

---

## TS-FORBID-012 — No Nested Ternaries

**Rule**
Nested ternary operators are forbidden. Use if/else or switch statements.

**Rationale**
Nested ternaries are difficult to read and maintain. They obscure logic flow and are prone to errors.

**Enforcement**
ESLint no-nested-ternary must be enabled. Complex conditions must use if/else. Code review must reject nested ternaries.
