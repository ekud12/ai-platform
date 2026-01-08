# TypeScript Security Rules

## Purpose
Defines security standards for frontend and Node.js TypeScript code.

## Authority
Governs all `.ts` and `.tsx` files.

---

## TS-SEC-001 — No InnerHTML / DangerouslySetInnerHTML
**Severity: Critical**

**Rule**
Avoid direct DOM injection to prevent XSS.

**Bad Pattern**
```tsx
<div dangerouslySetInnerHTML={{ __html: userInput }} />
```

**Good Pattern**
```tsx
<div>{userInput}</div>
// If HTML is absolutely required, use a sanitizer:
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(userInput) }} />
```

---

## TS-SEC-002 — No Console Logs in Production
**Severity: Warning**

**Rule**
Remove `console.log` statements. They leak sensitive data and clutter output.

**Bad Pattern**
```typescript
try {
  login();
} catch (e) {
  console.log("Login failed", e); // Leaks potential stack/data
}
```

**Good Pattern**
```typescript
logger.error("Login failed", { error: e.message });
```

---

## TS-SEC-003 — No Eval or Function Constructor
**Severity: Critical**

**Rule**
Do not use `eval()` or `new Function()`.

**Bad Pattern**
```typescript
const result = eval(userInput);
```

**Good Pattern**
```typescript
// Parse data safely
const result = JSON.parse(userInput);
```

---

## TS-SEC-004 — No Secrets in Client Code
**Severity: Critical**

**Rule**
API keys, tokens, and secrets MUST NOT exist in frontend bundles. Use backend proxies.

**Bad Pattern**
```typescript
const STRIPE_KEY = "sk_live_abc123"; // Exposed in bundle!
const response = await fetch(url, {
    headers: { "Authorization": `Bearer ${STRIPE_KEY}` }
});
```

**Good Pattern**
```typescript
// Call your backend, which holds the secret
const response = await fetch("/api/payment", {
    method: "POST",
    body: JSON.stringify(paymentData)
});
```

---

## TS-SEC-005 — Secure Cookie Handling
**Severity: Critical**

**Rule**
Cookies MUST use `Secure`, `HttpOnly`, and `SameSite=Strict` attributes for sensitive data.

**Bad Pattern**
```typescript
document.cookie = `session=${token}`; // Accessible to XSS, sent over HTTP
```

**Good Pattern**
```typescript
// Set from server response header:
// Set-Cookie: session=xyz; Secure; HttpOnly; SameSite=Strict; Path=/

// Client cannot and should not set sensitive cookies
```

---

## TS-SEC-006 — No Sensitive Data in LocalStorage
**Severity: Critical**

**Rule**
Sensitive data (tokens, PII) MUST NOT be stored in localStorage. Use httpOnly cookies.

**Bad Pattern**
```typescript
localStorage.setItem("authToken", token); // XSS can steal this
localStorage.setItem("creditCard", cardNumber);
```

**Good Pattern**
```typescript
// Auth tokens should be in httpOnly cookies (set by server)
// Store only non-sensitive UI preferences in localStorage
localStorage.setItem("theme", "dark");
localStorage.setItem("language", "en");
```

---

## TS-SEC-007 — PostMessage Validation
**Severity: Critical**

**Rule**
`postMessage` handlers MUST validate `origin` before processing messages.

**Bad Pattern**
```typescript
window.addEventListener("message", (event) => {
    processData(event.data); // Any origin can send malicious data!
});
```

**Good Pattern**
```typescript
const TRUSTED_ORIGINS = ["https://app.example.com", "https://widget.example.com"];

window.addEventListener("message", (event) => {
    if (!TRUSTED_ORIGINS.includes(event.origin)) {
        console.warn("Rejected message from untrusted origin:", event.origin);
        return;
    }
    processData(event.data);
});
```

---

## TS-SEC-008 — URL Parameter Injection
**Severity: Critical**

**Rule**
User-controlled values in URLs MUST be encoded. Never interpolate raw input into `href` or `src`.

**Bad Pattern**
```typescript
const url = `https://api.example.com/search?q=${userInput}`; // Injection risk
link.href = userInput; // javascript: URLs possible!
```

**Good Pattern**
```typescript
const url = new URL("https://api.example.com/search");
url.searchParams.set("q", userInput); // Automatically encoded

// Validate URL protocol before assignment
const parsed = new URL(userInput);
if (parsed.protocol === "https:") {
    link.href = parsed.toString();
}
```

---

## TS-SEC-009 — CSP Compliance
**Severity: Major**

**Rule**
Code MUST be CSP-compatible. No inline scripts, no `unsafe-eval`. Use nonces if dynamic scripts required.

**Bad Pattern**
```typescript
// Requires unsafe-inline
element.setAttribute("onclick", "doSomething()");

// Requires unsafe-eval
const fn = new Function("return " + code);
```

**Good Pattern**
```typescript
// Use event listeners
element.addEventListener("click", doSomething);

// Use pre-compiled code, not runtime evaluation
import { handler } from "./handlers";
```

---

## TS-SEC-010 — Dependency Audit
**Severity: Critical**

**Rule**
`npm audit` MUST pass with zero high/critical vulnerabilities before deployment.

**Bad Pattern**
```bash
# Ignoring vulnerabilities
npm audit # Shows 5 critical vulnerabilities
npm run deploy # Deploying anyway
```

**Good Pattern**
```bash
# CI/CD pipeline
npm audit --audit-level=high
# Fails build if high/critical found

# Regular maintenance
npm audit fix
npm update
```