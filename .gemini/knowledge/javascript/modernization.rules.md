# JavaScript Modernization Rules

## Purpose

This rulebook defines standards for modernizing JavaScript code. The goal is migration to TypeScript and modern JavaScript standards.

## Authority

These rules govern JavaScript codebases with the objective of eventual TypeScript migration.

## Scope

Applies to all JavaScript files with emphasis on migration readiness.

## Constraints

- JavaScript is transitional
- TypeScript is the target
- Modern syntax is required

## Rule Format

All rules use the JS-MOD prefix.

---

## JS-MOD-001 — ESM Modules

**Rule**
All JavaScript files must use ES modules (import/export). CommonJS (require/module.exports) is forbidden for new code.

**Rationale**
ESM is the JavaScript standard. It enables tree shaking, static analysis, and TypeScript migration.

**Enforcement**
ESLint must enforce ESM. Package.json must specify "type": "module". Legacy CommonJS must be migrated.

---

## JS-MOD-002 — TypeScript Ready

**Rule**
JavaScript code must be structured for TypeScript migration. JSDoc type annotations are required.

**Rationale**
JSDoc enables TypeScript to understand JavaScript. It provides incremental typing before full migration.

**Enforcement**
JSDoc types must be present on functions. @ts-check must be enabled where possible. Migration blockers must be documented.

---

## JS-MOD-003 — Strict Mode

**Rule**
All JavaScript files must use strict mode.

**Rationale**
Strict mode catches common errors and prevents unsafe practices. It is required for modules and improves optimization.

**Enforcement**
"use strict" or module mode must be present. Non-strict legacy code must be migrated. Strict violations must be fixed.

---

## JS-MOD-004 — Const Over Let

**Rule**
const must be used by default. let only for variables that are reassigned.

**Rationale**
const prevents accidental reassignment and signals intent. let should be reserved for loop counters and values that genuinely change.

**Related Rules**
- JS-FORBID-001 prohibits var usage (this rule assumes var is already forbidden)

**Enforcement**
ESLint prefer-const must be enabled. let usage must have clear reassignment justification. Code review must verify const preference.

---

## JS-MOD-005 — Arrow Functions

**Rule**
Arrow functions must be used for callbacks and short functions. Function declarations for named functions.

**Rationale**
Arrow functions have lexical this and concise syntax. They prevent this-related bugs in callbacks.

**Enforcement**
Callbacks must use arrow syntax. Function expressions must justify over arrows. Code style must be consistent.

---

## JS-MOD-006 — Template Literals

**Rule**
String concatenation must use template literals for any non-trivial cases.

**Rationale**
Template literals are more readable than concatenation. They enable multiline strings and expression embedding.

**Enforcement**
String concatenation with + must be flagged. Template literals must be preferred. Code review must verify usage.

---

## JS-MOD-007 — Destructuring

**Rule**
Object and array destructuring must be used for extracting multiple values.

**Rationale**
Destructuring is more concise and clearer than repeated property access. It documents the values being used.

**Enforcement**
Multiple property accesses must use destructuring. Function parameters should destructure options. Code review must verify patterns.

---

## JS-MOD-008 — Spread Operator

**Rule**
Spread operator must be used for object copying and array manipulation.

**Rationale**
Spread is clearer than Object.assign or concat. It enables immutable update patterns.

**Enforcement**
Object.assign for copying must be replaced with spread. Array concat must use spread. Code review must verify usage.

---

## JS-MOD-009 — Optional Chaining

**Rule**
Optional chaining (?.) must be used for nullable property access.

**Rationale**
Optional chaining is safer and more concise than && chains. It clearly expresses nullable intent.

**Enforcement**
Nested && checks must use optional chaining. Code review must identify candidates. ESLint must suggest modernization.

---

## JS-MOD-010 — Nullish Coalescing

**Rule**
Nullish coalescing (??) must be used for defaults instead of || when zero/empty string are valid.

**Rationale**
|| treats falsy values as missing. ?? only treats null/undefined as missing, preserving valid empty values.

**Enforcement**
Default value patterns must use ?? appropriately. || usage must consider falsy edge cases. Code review must verify correctness.

---

## JS-MOD-011 — Object Shorthand

**Rule**
Use shorthand property and method syntax in object literals.

**Rationale**
Shorthand is more concise and reduces duplication. It clearly shows when property name matches variable name.

**Enforcement**
ESLint object-shorthand must be enabled. Redundant property definitions must be shortened. Code review must verify usage.

---

## JS-MOD-012 — Class Fields

**Rule**
Use public class fields instead of constructor assignment for simple properties.

**Rationale**
Class fields are more declarative and concise. They clearly show class structure at the top of the definition.

**Enforcement**
Simple property initialization must use class fields. Constructor must only contain complex initialization. Code review must verify patterns.
