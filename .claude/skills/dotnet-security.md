---
name: dotnet-security
description: Security patterns including OWASP compliance, input validation, secret management, cryptography, and post-quantum algorithms.
allowed-tools: Read, Write, Edit
---

# .NET Security Patterns (Rules Only)

## Input Validation
- SEC-INPUT-001: Validate at all trust boundaries
- SEC-INPUT-002: Use FluentValidation for complex rules
- SEC-INPUT-003: Apply Data Annotations for simple validation
- SEC-INPUT-004: Reject invalid input before processing
- SEC-INPUT-005: Never trust client data

## OWASP Top 10 Compliance
- SEC-OWASP-001: Injection: Use parameterized queries exclusively
- SEC-OWASP-002: Broken Authentication: Implement WebAuthN/passkeys
- SEC-OWASP-003: Sensitive Data Exposure: Encrypt at rest and in transit
- SEC-OWASP-004: XML External Entities: Disable XXE in XML parsers
- SEC-OWASP-005: Broken Access Control: Validate permissions on every request
- SEC-OWASP-006: Security Misconfiguration: Secure defaults, no debug in production
- SEC-OWASP-007: XSS: Sanitize all output, use Content Security Policy
- SEC-OWASP-008: Insecure Deserialization: Validate types before deserializing
- SEC-OWASP-009: Using Components with Known Vulnerabilities: Keep dependencies updated
- SEC-OWASP-010: Insufficient Logging: Log all security events

## Secret Management
- SEC-SECRET-001: Use SECRET_ prefix for secret identifiers
- SEC-SECRET-002: Never hardcode credentials
- SEC-SECRET-003: Load from secure vault (Azure Key Vault, AWS Secrets Manager)
- SEC-SECRET-004: No secrets in source control
- SEC-SECRET-005: Use managed identities where possible
- SEC-SECRET-006: Rotate secrets regularly

## Cryptography
- SEC-CRYPTO-001: Use vetted .NET APIs only (Aes.Create(), RSA.Create())
- SEC-CRYPTO-002: Never implement custom cryptography
- SEC-CRYPTO-003: Use Rfc2898DeriveBytes for password hashing
- SEC-CRYPTO-004: Apply RandomNumberGenerator.GetBytes for secure random
- SEC-CRYPTO-005: Use constant-time comparison for secrets
- SEC-CRYPTO-006: Implement post-quantum algorithms for forward security

## Post-Quantum Cryptography (.NET 10)
- SEC-PQC-001: Use ML-DSA for digital signatures
- SEC-PQC-002: Apply HashML-DSA where appropriate
- SEC-PQC-003: Implement for long-term data protection
- SEC-PQC-004: Use Windows CNG support on Windows
- SEC-PQC-005: Plan migration path for existing systems

## Authentication
- SEC-AUTH-001: Implement WebAuthN and passkeys (.NET 10)
- SEC-AUTH-002: Use cookie authentication for web apps
- SEC-AUTH-003: Apply JWT for APIs with proper validation
- SEC-AUTH-004: Never roll custom auth schemes
- SEC-AUTH-005: Enforce MFA where possible

## Authorization
- SEC-AUTHZ-001: Use claims-based authorization
- SEC-AUTHZ-002: Apply policy-based authorization patterns
- SEC-AUTHZ-003: Validate on every request, not just entry
- SEC-AUTHZ-004: Check at data access layer too
- SEC-AUTHZ-005: No authorization logic in views/clients

## TLS/HTTPS
- SEC-TLS-001: Enforce HTTPS redirection mandatory
- SEC-TLS-002: Use TLS 1.3 where supported (.NET 10)
- SEC-TLS-003: Disable older TLS versions
- SEC-TLS-004: Validate certificates properly
- SEC-TLS-005: Use HSTS headers

## Content Security Policy
- SEC-CSP-001: Implement CSP headers for web apps
- SEC-CSP-002: No inline scripts without nonce
- SEC-CSP-003: Whitelist allowed sources
- SEC-CSP-004: Report violations to monitoring

## SQL Injection Prevention
- SEC-SQL-001: Use parameterized queries exclusively
- SEC-SQL-002: Apply EF Core for data access
- SEC-SQL-003: Never concatenate SQL strings
- SEC-SQL-004: Use stored procedures with parameters only

## XSS Prevention
- SEC-XSS-001: Encode all output
- SEC-XSS-002: Use Razor automatic encoding
- SEC-XSS-003: Sanitize rich text inputs
- SEC-XSS-004: Implement CSP
- SEC-XSS-005: No innerHTML without sanitization

## CSRF Protection
- SEC-CSRF-001: Use antiforgery tokens for state changes
- SEC-CSRF-002: ValidateAntiForgeryToken on POST/PUT/DELETE
- SEC-CSRF-003: SameSite cookies for session management

## Dependency Security
- SEC-DEP-001: Scan dependencies for vulnerabilities
- SEC-DEP-002: Use dotnet list package --vulnerable
- SEC-DEP-003: Update vulnerable packages immediately
- SEC-DEP-004: Pin versions for reproducible builds

## Logging Security Events
- SEC-LOG-001: Log all authentication attempts
- SEC-LOG-002: Log authorization failures
- SEC-LOG-003: Log sensitive data access
- SEC-LOG-004: Never log secrets or passwords
- SEC-LOG-005: Include context for incident response

## Forbidden Patterns
- SEC-FORBID-001: No MD5 or SHA1 for security purposes
- SEC-FORBID-002: No hardcoded secrets
- SEC-FORBID-003: No AllowAnonymous without justification
- SEC-FORBID-004: No SQL string concatenation
- SEC-FORBID-005: No custom cryptography
- SEC-FORBID-006: No disabled certificate validation
- SEC-FORBID-007: No secrets in logs
- SEC-FORBID-008: No unvalidated redirects
- SEC-FORBID-009: No dynamic SQL without parameterization
