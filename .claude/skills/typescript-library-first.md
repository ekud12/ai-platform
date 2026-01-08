---
name: typescript-library-first
description: Check for existing npm packages before writing boilerplate. Always ask user permission before adding new dependencies.
allowed-tools: Read, Write, Edit, WebSearch
---

# TypeScript Library-First Approach (Rules Only)

## Core Principle
Before writing boilerplate in TypeScript, search for existing well-maintained npm packages. **Always ask user permission before adding any library.**

## When to Search for Packages

Check npm when implementing:
- **Error handling patterns** (Result/Either types: neverthrow, fp-ts, etc.)
- Validation (zod, valibot)
- HTTP clients (ky, axios)
- Async utilities (p-limit, p-queue, p-retry)
- Date/Time (date-fns, luxon)
- Testing (vitest, jest)
- State management
- Form handling
- Data transformation
- File parsing
- Cryptography
- Authentication

## Search Process

### Step 1: Use WebSearch
Query format: `"best npm package for [functionality] TypeScript 2025"`

### Step 2: Evaluate Top Results
Check:
- **npm stats**: Weekly downloads, last publish
- **GitHub**: Stars, commits, maintenance
- **TypeScript**: Native types included
- **Bundle size**: Use bundlephobia.com
- **Security**: No vulnerabilities

### Step 3: Ask User Permission
**Required format:**
```
Found: [package-name] v[version]
- Downloads: [count/week]
- Last published: [date]
- GitHub stars: [count]
- Bundle size: [size]
- TypeScript: Native types
- License: [type]
- Docs: [url]

This would replace [X] lines of custom code.

May I add this package? (yes/no)
```

## Preferred npm Packages

### Well-Established Libraries
- `neverthrow`, `fp-ts` - Result/Either pattern (check before writing custom)
- `zod` or `valibot` - Runtime validation
- `ky` - HTTP client
- `date-fns` - Date utilities (NOT moment.js)
- `p-limit`, `p-queue`, `p-retry` - Async utilities
- `vitest` or `jest` - Testing
- `remeda` - Typed utilities (lodash alternative)
- `nanoid` - ID generation
- `js-cookie` - Cookie handling
- `qs` - Query string parsing

### Avoid These (Unmaintained)
- ❌ `moment.js` - Use date-fns or luxon
- ❌ `request` - Use ky or axios
- ❌ `lodash` - Use remeda (smaller, typed)

## Decision Framework

### ✅ Recommend Package When:
- Maintained (published within 6 months)
- Popular (>100K weekly downloads)
- TypeScript native or @types available
- Bundle size reasonable (<50KB for utilities)
- Reduces >50 lines of boilerplate
- **After user approval**

### ✅ Write Custom When:
- No suitable package exists
- Simple functionality (<20 lines)
- User declines package addition
- Package unmaintained
- Bundle size too large for feature
- Security vulnerabilities

## Installation Command
After approval:
```bash
npm install [package-name]
# or
pnpm add [package-name]
# or
yarn add [package-name]
```

## Bundle Size Consideration
Always mention bundle size for frontend code:
```
Bundle impact: +15KB gzipped
```

## Anti-Patterns
- ❌ Adding packages without user permission
- ❌ Using unmaintained packages (moment.js, request)
- ❌ Writing custom Result/Either types (search for libraries first)
- ❌ Writing custom validation (use zod)
- ❌ Writing custom async utilities (use p-limit)
- ❌ Large bundles for simple features
- ❌ Packages without TypeScript types
