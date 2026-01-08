---
name: response-format
description: Response formatting guidelines for all agents. Ensures concise, focused communication without unnecessary verbosity.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# Response Format Guidelines

## Core Principles
- Be concise and direct
- Focus on what changed (additions/removals/modifications)
- Avoid unnecessary explanations
- Practical over verbose

## What to Include
✅ **Always show:**
- "What's Included" sections (useful summary)
- Specific changes made (added/removed/modified)
- File paths and line numbers when relevant
- Error messages when fixing issues

❌ **Skip unless fixing violations:**
- Lengthy compliance checklists (📊 Compliance Check)
- Rule-by-rule validation reports
- Exhaustive feature confirmations

## Format Examples

### ✅ Good - Concise with useful info
```
Created multiply.ts

What's Included:
- Result<T, E> type for error handling
- Runtime validation with zod
- Overflow detection
- JSDoc with examples
```

### ❌ Bad - Too verbose
```
Created multiply.ts

What's Included:
- Result<T, E> type for error handling
- Runtime validation with zod
- Overflow detection
- JSDoc with examples

📊 Compliance Check:
- ✅ TS-TYPE-001: No any types
- ✅ TS-VALID-001: Zod validation
- ✅ TS-VALID-002: Uses safeParse
- ✅ TS-ERROR-001: Returns Result<T,E>
[... 10 more lines ...]
```

## When to Show Compliance Checks
Only include compliance validation when:
- Fixing violations in existing code
- Resolving reported issues
- User explicitly asks for validation

## Summary Format
```
✅ Changes:
- Added: [specific addition]
- Modified: [specific change]
- Removed: [specific removal]

What's Included:
- [Key feature 1]
- [Key feature 2]
```

Keep it brief, focused, and actionable.
