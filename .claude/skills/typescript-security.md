---
name: typescript-security
description: TypeScript security patterns for XSS prevention, prototype pollution, constant-time comparison, CSP enforcement, and secret isolation.
allowed-tools: Read, Write, Edit
---

# TypeScript Security Patterns (Rules Only)

## Purpose
Enforce security best practices in TypeScript code to prevent common vulnerabilities like XSS, prototype pollution, injection attacks, and secret exposure.

## Input Validation

### Boundary Validation
- TS-SEC-001: All input boundaries must cross schema + sanitizer + access check
- TS-SEC-002: Validate all external data with zod/valibot/io-ts before processing
- TS-SEC-003: Use `.safeParse()` and handle validation failures explicitly
- TS-SEC-004: Sanitize all user input before storage or processing
- TS-SEC-005: Reject invalid input - never attempt to "fix" it
- TS-SEC-006: Validate file uploads (type, size, content)

### Type Safety as Security
- TS-SEC-007: Use branded types for security-sensitive identifiers
- TS-SEC-008: No `any`, `object`, or dynamic typing at security boundaries
- TS-SEC-009: Validate runtime types match compile-time expectations
- TS-SEC-010: Use template literal types for validated string formats

## XSS Prevention

### Content Security Policy
- TS-SEC-011: CSP actively enforced - configure strict Content-Security-Policy headers
- TS-SEC-012: No `innerHTML`, `outerHTML`, or `document.write()`
- TS-SEC-013: Use `textContent` or `createTextNode()` for user data
- TS-SEC-014: Use DOM APIs (createElement, appendChild) instead of string HTML
- TS-SEC-015: Sanitize HTML with DOMPurify if HTML rendering required
- TS-SEC-016: Use CSP nonce or hash for inline scripts

### URL Handling
- TS-SEC-017: Validate and sanitize URLs before navigation or rendering
- TS-SEC-018: Use `URL` constructor to parse and validate URLs
- TS-SEC-019: Whitelist allowed URL schemes (http, https)
- TS-SEC-020: No `javascript:` URLs
- TS-SEC-021: Sanitize `href` and `src` attributes

## Prototype Pollution

### Object Creation
- TS-SEC-022: Use `Object.create(null)` for key-value stores
- TS-SEC-023: No `__proto__`, `constructor`, or `prototype` property access from user input
- TS-SEC-024: Validate object keys against whitelist before assignment
- TS-SEC-025: Use `Map` instead of plain objects for user-controlled keys
- TS-SEC-026: Freeze prototypes of sensitive objects

### Safe Property Access
- TS-SEC-027: Use `Object.hasOwn()` instead of `hasOwnProperty`
- TS-SEC-028: No dynamic property assignment from untrusted sources
- TS-SEC-029: Validate property names before dynamic access
- TS-SEC-030: Use `Reflect.get/set` with proper validation

## Secret Management

### Secret Isolation
- TS-SEC-031: All secrets use `SECRET_*` naming pattern
- TS-SEC-032: No hardcoded secrets in code
- TS-SEC-033: Load secrets from secure environment variables or secret manager
- TS-SEC-034: Never log secrets (use redaction patterns)
- TS-SEC-035: Never include secrets in error messages
- TS-SEC-036: Never return secrets in API responses

### Secret Comparison
- TS-SEC-037: Use constant-time comparison for secrets
- TS-SEC-038: Implement `timingSafeEqual()` for password/token comparison
- TS-SEC-039: No string `===` for security-sensitive comparisons
- TS-SEC-040: Use crypto.timingSafeEqual() from Node.js crypto module

## Authentication & Authorization

### Token Handling
- TS-SEC-041: Store authentication tokens securely (httpOnly cookies or secure storage)
- TS-SEC-042: No tokens in URLs or query parameters
- TS-SEC-043: Implement token expiration and refresh logic
- TS-SEC-044: Validate token signature and claims before trusting
- TS-SEC-045: Use short-lived access tokens with refresh tokens

### Authorization
- TS-SEC-046: Check authorization on every protected operation
- TS-SEC-047: Implement role-based or attribute-based access control
- TS-SEC-048: No client-side authorization checks only (always validate server-side)
- TS-SEC-049: Validate resource ownership before allowing operations
- TS-SEC-050: Default deny - require explicit permission grants

## Injection Prevention

### SQL Injection
- TS-SEC-051: Use parameterized queries or ORMs
- TS-SEC-052: Never concatenate user input into SQL queries
- TS-SEC-053: Validate and sanitize all database inputs
- TS-SEC-054: Use prepared statements for all queries
- TS-SEC-055: Limit database privileges (principle of least privilege)

### Command Injection
- TS-SEC-056: Never pass user input to `child_process.exec()` or `eval()`
- TS-SEC-057: Use `child_process.execFile()` with argument array
- TS-SEC-058: Validate and whitelist all command arguments
- TS-SEC-059: Avoid shell execution - use direct binaries
- TS-SEC-060: No dynamic code execution (`eval`, `Function()`, `new Function()`)

### NoSQL Injection
- TS-SEC-061: Validate all inputs to NoSQL queries
- TS-SEC-062: Use typed ORM/ODM instead of raw queries
- TS-SEC-063: No query operators from user input
- TS-SEC-064: Sanitize MongoDB queries (no `$where`, untrusted operators)

## CSRF Protection

### Cross-Site Request Forgery
- TS-SEC-065: Implement CSRF tokens for state-changing operations
- TS-SEC-066: Validate CSRF token on all POST/PUT/DELETE/PATCH requests
- TS-SEC-067: Use SameSite cookie attribute
- TS-SEC-068: Validate Origin and Referer headers
- TS-SEC-069: No GET requests for state-changing operations

## CORS Configuration

### Cross-Origin Resource Sharing
- TS-SEC-070: Configure explicit CORS origins - no wildcard `*` in production
- TS-SEC-071: Validate Origin header against whitelist
- TS-SEC-072: No credentials with wildcard origins
- TS-SEC-073: Use appropriate CORS preflight caching
- TS-SEC-074: Limit exposed headers in CORS responses

## Cryptography

### Encryption
- TS-SEC-075: Use strong encryption algorithms (AES-256-GCM)
- TS-SEC-076: Generate random IVs for each encryption operation
- TS-SEC-077: Use crypto.randomBytes() for cryptographically secure random values
- TS-SEC-078: No weak algorithms (MD5, SHA1 for security purposes, DES, RC4)
- TS-SEC-079: Use HMAC for message authentication

### Password Hashing
- TS-SEC-080: Use bcrypt, scrypt, or Argon2 for password hashing
- TS-SEC-081: No plain-text password storage
- TS-SEC-082: Use appropriate work factor/cost parameter
- TS-SEC-083: Salt all password hashes
- TS-SEC-084: No weak hashing algorithms for passwords

## Session Management

### Session Security
- TS-SEC-085: Generate cryptographically random session IDs
- TS-SEC-086: Implement session expiration and idle timeout
- TS-SEC-087: Regenerate session ID after authentication
- TS-SEC-088: Invalidate sessions on logout
- TS-SEC-089: Use secure and httpOnly flags for session cookies
- TS-SEC-090: Implement session fixation protection

## File Upload Security

### Upload Validation
- TS-SEC-091: Validate file type and extension
- TS-SEC-092: Validate file size limits
- TS-SEC-093: Scan uploaded files for malware
- TS-SEC-094: Store uploads outside web root
- TS-SEC-095: Generate random filenames for uploads
- TS-SEC-096: Validate file content (magic bytes), not just extension

## Error Handling

### Secure Error Handling
- TS-SEC-097: Never expose stack traces to users in production
- TS-SEC-098: Log detailed errors server-side only
- TS-SEC-099: Return generic error messages to clients
- TS-SEC-100: No sensitive data in error messages
- TS-SEC-101: Implement proper error monitoring and alerting

## Logging Security

### Secure Logging
- TS-SEC-102: Redact PII from logs
- TS-SEC-103: Redact secrets and tokens from logs
- TS-SEC-104: Sanitize log injection attacks (no user input directly in logs)
- TS-SEC-105: Use structured logging to prevent log injection
- TS-SEC-106: Secure log storage and access controls

## Dependency Security

### Dependency Management
- TS-SEC-107: Regularly audit dependencies for vulnerabilities (npm audit)
- TS-SEC-108: Keep dependencies up to date
- TS-SEC-109: Remove unused dependencies (reduce attack surface)
- TS-SEC-110: Verify package integrity (use lock files)
- TS-SEC-111: Review dependencies before adding (supply chain security)
- TS-SEC-112: No dependencies >25 KB that are unused

## Regular Expressions

### ReDoS Prevention
- TS-SEC-113: Avoid catastrophic backtracking patterns
- TS-SEC-114: Test regex with malicious inputs
- TS-SEC-115: Set timeouts for regex execution
- TS-SEC-116: Use atomic groups or possessive quantifiers
- TS-SEC-117: Validate regex patterns before compilation

## HTTP Security Headers

### Security Headers
- TS-SEC-118: Set Strict-Transport-Security header
- TS-SEC-119: Set X-Content-Type-Options: nosniff
- TS-SEC-120: Set X-Frame-Options: DENY or SAMEORIGIN
- TS-SEC-121: Set Referrer-Policy
- TS-SEC-122: Set Permissions-Policy
- TS-SEC-123: Remove or obscure Server header

## Forbidden Patterns

### Security Anti-Patterns
- TS-SEC-124: No `eval()` or `Function()` constructor
- TS-SEC-125: No `innerHTML` with user data
- TS-SEC-126: No secrets in client-side code
- TS-SEC-127: No client-side security logic only
- TS-SEC-128: No sensitive data in URLs
- TS-SEC-129: No disabled security features (escapeValue, sanitization)
- TS-SEC-130: No weak random number generation for security

## Activation Criteria
Use these patterns when:
- Handling user input at any boundary
- Implementing authentication and authorization
- Storing or processing sensitive data
- Preventing common web vulnerabilities
