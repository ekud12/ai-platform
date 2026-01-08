# JavaScript Safety Rules

## Purpose

This rulebook defines runtime safety patterns for JavaScript. Without TypeScript's compile-time checks, runtime safety is critical.

## Authority

These rules govern JavaScript code safety and error handling.

## Scope

Applies to all JavaScript runtime operations, error handling, and data validation.

## Constraints

- Runtime checks are mandatory
- Errors must be handled
- Data must be validated

## Rule Format

All rules use the JS-SAFE prefix.

---

## JS-SAFE-001 — Defensive Type Checking

**Rule**
Functions must validate parameter types at boundaries.

**Rationale**
Without compile-time types, runtime validation prevents type errors. Boundary validation catches issues early.

**Enforcement**
Public functions must check types. Type assertions must throw clear errors. Validation must be consistent.

---

## JS-SAFE-002 — Null Checks

**Rule**
Nullable values must be checked before use.

**Rationale**
Null reference errors are common in JavaScript. Explicit checks prevent crashes and clarify logic.

**Enforcement**
Property access on nullable values must be guarded. Optional chaining must be used. Code review must verify null safety.

---

## JS-SAFE-003 — Array Bounds

**Rule**
Array index access must be bounds-checked when index is variable.

**Rationale**
Out-of-bounds access returns undefined, not an error. Explicit checks catch logic errors.

**Enforcement**
Variable indices must be validated. Array methods with callbacks must be preferred. Code review must verify bounds.

---

## JS-SAFE-004 — Error Handling

**Rule**
All potentially throwing operations must have error handling.

**Rationale**
Unhandled exceptions crash applications. Proper error handling enables graceful degradation.

**Enforcement**
Try-catch must surround risky operations. Error boundaries must be defined. Async errors must be caught.

---

## JS-SAFE-005 — Input Validation

**Rule**
All external input must be validated before processing.

**Rationale**
External input is untrusted by definition. Validation prevents injection and logic errors.

**Enforcement**
Form inputs must be validated. API responses must be validated. File inputs must be validated.

---

## JS-SAFE-006 — Safe JSON

**Rule**
JSON.parse must be wrapped in error handling.

**Rationale**
JSON.parse throws on invalid input. Network responses and user input may contain invalid JSON.

**Enforcement**
JSON.parse must have try-catch. Safe parsing utilities must be used. Parse errors must be handled gracefully.

---

## JS-SAFE-007 — Date Handling

**Rule**
Date parsing must validate results. Invalid Date must be detected and handled.

**Rationale**
Invalid date strings produce Invalid Date, not errors. Invalid Date propagates silently through calculations.

**Enforcement**
Date.parse results must be checked. isNaN must verify dates. Date libraries should be used for complex operations.

---

## JS-SAFE-008 — Number Safety

**Rule**
Numeric operations must guard against NaN, Infinity, and precision issues.

**Rationale**
JavaScript numbers have edge cases that produce unexpected results. Validation ensures correct calculations.

**Enforcement**
User input numbers must be validated. Division must check for zero. Financial calculations must use appropriate precision.

---

## JS-SAFE-009 — Prototype Safety

**Rule**
Object property access must not traverse prototype chain unexpectedly.

**Rationale**
Prototype pollution and inherited properties cause security and logic issues. Object.hasOwn must be used.

**Enforcement**
Object.hasOwn must check own properties. Object.create(null) for dictionaries. Code review must verify prototype safety.

---

## JS-SAFE-010 — Event Handler Safety

**Rule**
Event handlers must not throw unhandled exceptions.

**Rationale**
Exceptions in event handlers can break application state. Handlers must catch and log errors.

**Enforcement**
Event handlers must have try-catch. Errors must be logged. UI must not break on handler errors.

---

## JS-SAFE-011 — Regex Safety

**Rule**
User input in RegExp MUST be escaped. Use libraries for complex patterns to avoid ReDoS.

**Rationale**
Unescaped user input enables injection. Complex patterns can cause catastrophic backtracking (ReDoS attacks).

**Enforcement**
User input must be escaped with library functions. Complex regex must be reviewed for ReDoS. Timeouts must be used for user-provided patterns.

---

## JS-SAFE-012 — URL Construction

**Rule**
Use `URL` constructor instead of string concatenation for building URLs.

**Rationale**
String concatenation is error-prone and can create invalid URLs. URL constructor handles encoding and validation automatically.

**Enforcement**
URL building must use URL constructor. Query parameters must use URLSearchParams. Code review must reject string concatenation for URLs.
