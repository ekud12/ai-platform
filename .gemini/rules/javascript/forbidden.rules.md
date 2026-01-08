# JavaScript Forbidden Patterns Rules

## Purpose

This rulebook explicitly defines patterns that are banned from JavaScript codebases. These patterns are known to cause problems.

## Authority

These rules define absolute prohibitions for JavaScript code.

## Scope

Applies to all JavaScript code without exception.

## Constraints

- Forbidden patterns must be eliminated
- Legacy code must be refactored
- No new code may use forbidden patterns

## Rule Format

All rules use the JS-FORBID prefix.

---

## JS-FORBID-001 — No var

**Rule**
The var keyword is forbidden. Use const or let.

**Rationale**
var has function scope and hoisting that cause bugs. Block-scoped const/let are safer and clearer.

**Related Rules**
- JS-MOD-004 defines const vs let preference (const by default)

**Enforcement**
ESLint no-var must error. Existing var must be migrated. No new var allowed.

---

## JS-FORBID-002 — No eval

**Rule**
eval and Function constructor are forbidden.

**Rationale**
eval executes arbitrary code, enabling injection attacks. It bypasses static analysis and optimization.

**Enforcement**
ESLint must error on eval. No dynamic code execution. Security scans must detect eval.

---

## JS-FORBID-003 — No with

**Rule**
The with statement is forbidden.

**Rationale**
with creates ambiguous scope. It is deprecated, error-prone, and prevents optimization.

**Enforcement**
ESLint must error on with. Strict mode forbids with. Legacy code must be refactored.

---

## JS-FORBID-004 — No arguments Object

**Rule**
The arguments object is forbidden. Use rest parameters.

**Rationale**
arguments is not a real array. Rest parameters provide proper array functionality.

**Enforcement**
ESLint must flag arguments usage. Rest parameters must be used. Legacy code must be migrated.

---

## JS-FORBID-005 — No == Operator

**Rule**
Loose equality (== and !=) is forbidden. Use strict equality (=== and !==).

**Rationale**
Loose equality has complex coercion rules that cause bugs. Strict equality is predictable.

**Enforcement**
ESLint must error on ==. All comparisons must use ===. Explicit coercion if needed.

---

## JS-FORBID-006 — No Implicit Globals

**Rule**
Implicit global variable creation is forbidden.

**Rationale**
Undeclared variables become globals, polluting global scope. This causes hard-to-find bugs.

**Enforcement**
Strict mode must be enabled. ESLint no-undef must be enabled. All variables must be declared.

---

## JS-FORBID-007 — No Callbacks for Async

**Rule**
Callback-based async patterns are forbidden for new code. Use Promises/async-await.

**Rationale**
Callbacks create nesting and make error handling difficult. Promises are the modern standard.

**Enforcement**
New async code must use Promises. Legacy callbacks must be wrapped. Code review must reject callbacks.

---

## JS-FORBID-008 — No document.write

**Rule**
document.write is forbidden.

**Rationale**
document.write blocks parsing and can overwrite the entire document. It causes performance issues.

**Enforcement**
ESLint must flag document.write. DOM manipulation must use modern APIs. Legacy usage must be removed.

---

## JS-FORBID-009 — No Synchronous XHR

**Rule**
Synchronous XMLHttpRequest is forbidden.

**Rationale**
Synchronous requests block the main thread, freezing the UI. They are deprecated in modern browsers.

**Enforcement**
ESLint must flag sync XHR. Fetch or async XHR must be used. Legacy code must be migrated.

---

## JS-FORBID-010 — No Inline Event Handlers

**Rule**
Inline HTML event handlers (onclick, onload, etc.) are forbidden.

**Rationale**
Inline handlers mix behavior with markup. They complicate CSP and cannot be easily managed.

**Enforcement**
HTML must not contain event attributes. addEventListener must be used. Template systems must not emit inline handlers.

---

## JS-FORBID-011 — No Alert/Confirm/Prompt

**Rule**
Browser dialogs (`alert`, `confirm`, `prompt`) are forbidden. Use UI components.

**Rationale**
Browser dialogs block the main thread and cannot be styled. They provide poor UX and break accessibility.

**Enforcement**
ESLint no-alert must be enabled. Modal components must be used instead. Code review must reject browser dialogs.

---

## JS-FORBID-012 — No Deep Callback Nesting

**Rule**
Callback nesting beyond 2 levels is forbidden. Refactor to promises, async/await, or named functions.

**Rationale**
Deep nesting creates "pyramid of doom" that is hard to read and maintain. It indicates need for refactoring.

**Enforcement**
ESLint max-nested-callbacks must be configured. Deep nesting must be refactored. Code review must reject callback pyramids.
