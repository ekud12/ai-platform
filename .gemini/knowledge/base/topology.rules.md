# Global Topology & Casing Rules

## Purpose
Defines naming and structural standards for project roots and cross-technology boundaries.

## Authority
Governs the top-level directory structure and the interface between backend/frontend/infrastructure folders.

---

## GLOB-TOP-001 — Root Folder Casing
**Severity: Major**

**Rule**
Top-level project folders (e.g., `/src`, `/docs`, `/scripts`, `/deploy`) MUST use **kebab-case** for cross-platform shell compatibility.

**Good Pattern**
```
/src
/docs
/infra-as-code
/scripts
```

---

## GLOB-TOP-002 — Technology Boundaries
**Severity: Major**

**Rule**
Internal folders within a language-specific source directory MUST follow that language's native casing convention, regardless of the root casing.

**Good Pattern**
```
/src/Backend/Orders/... (PascalCase for .NET)
/src/frontend/order-ui/... (kebab-case for TypeScript)
```

**Rationale**
Ensures shell-friendly roots while maintaining idiomatic codebases within each stack.
