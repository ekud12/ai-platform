# Observability Protocol

## Directives
You are a monitored entity. You MUST leave a trail.

### 1. Logging (OBS-LOG)
**Rule:** Every significant action MUST produce a structured log line.
**Format:** JSON (always).
**Forbidden:** NEVER log PII (Names, Passwords, Keys).

**Bad Pattern (String):**
`"User logged in successfully."`

**Good Pattern (Structured):**
```json
{
  "level": "INFO",
  "event": "user_login",
  "user_id": "u-12345", 
  "status": "success",
  "correlation_id": "req-abc-999"
}
```

### 2. Metrics (OBS-MET)
**Rule:** If it moves, measure it.
**Key Metrics to Track:**
*   **Duration:** How long did it take? (`ms`)
*   **Count:** How many items processed?
*   **Error Rate:** Did it fail?

**Chain of Thought:**
"I am about to run a DB query. I should start a timer. Done. Duration: 45ms. I will log this."

### 3. Tracing (OBS-TRACE)
**Rule:** You MUST propagate `correlation_id` across all steps.
**Scenario:**
1.  User request comes in (`id: 123`).
2.  Planner creates task (`parent_id: 123`).
3.  Coder writes code (`trace_id: 123`).
*   **Why?** So we can debug the full story later.

### 4. Alerts (OBS-ALERT)
**Rule:** Differentiate `WARN` vs `ERROR`.
*   **WARN:** "I handled it, but it was weird." (e.g., Retry).
*   **ERROR:** "I failed. I stopped." (e.g., DB Down).

---

## Log Schema Reference
```json
{
  "timestamp": "ISO8601",
  "level": "INFO|WARN|ERROR",
  "agent": "coder.dotnet",
  "event": "EventName",
  "data": { ...context... }
}
```
