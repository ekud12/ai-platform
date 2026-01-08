---
name: architecture-checklist
description: Complete architecture interrogation framework for validating designs before implementation. 12-section assessment plus strategic risk questions.
allowed-tools: Read, Grep, Glob
---

# Architecture Interrogation Framework (Rules Only)

## 12-Section Architecture Interrogation

### Section 1: Scope & Intent
- What real-world need does this feature address?
- Who or what will invoke it, and when?
- What defines success in actual usage - not just unit tests?
- What's explicitly excluded? Are there hidden responsibilities?

### Section 2: Inputs & Outputs
- What shapes are valid or invalid at the boundary?
- Is validation performed at ingestion? With what schema/tools?
- How are outputs used - rendered, persisted, ignored?
- If shapes change, who breaks and where?

### Section 3: Failure Modes
- What can go wrong - internally and externally?
  - Network, permission, quota, misconfig, corrupted state
- How are errors surfaced - log, retry, fail loud, or silent drop?
- Are partial failures handled as first-class outcomes?

### Section 4: Logging & Observability
- What identifiers are logged for traceability? (user, request, correlation)
- Are both success and failure cases logged with structure?
- Can someone debug this flow using telemetry alone?
- What should trigger alerts, and where is the signal?

### Section 5: Performance & Scaling
- What's the expected throughput, and what's the ceiling?
- Is this logic part of a loop, batch, or scheduled job?
- Where are latency risks - network, disk, serialization, cold start?
- What pre-allocation or pooling is required to avoid GC or retries?

### Section 6: Idempotency & Transactionality
- Can this logic be safely retried? What if it is?
- What safeguards exist for partial state mutation?
- Is the operation atomic, or should isolation be enforced?

### Section 7: System Architecture Fit
- What component or layer should own this logic?
- Does it follow existing architectural boundaries and patterns?
- Are dependencies isolated behind interfaces?
- Could this introduce coupling, cycles, or ambiguity?

### Section 8: Security & Access
- What auth model is enforced - token, session, mutual trust?
- Is every operation scoped and permission-checked?
- Are secrets loaded securely and validated early?
- Any privilege escalation, spoofing, or injection vectors?

### Section 9: Deployment Variants
- What changes across environments (dev, staging, prod)?
- Are sandboxed dependencies configured properly?
- Do logs, telemetry, or settings vary by tier?
- Any legal or regulatory constraints by region or tenant?

### Section 10: Testability & Simulation
- Can the logic be isolated for unit testing?
- Are mocks or fakes available for dependencies?
- How do we simulate failures in connected systems?
- Can we load test, fuzz input, or trigger edge conditions safely?

### Section 11: Dependency Surface
- What external systems does this code rely on?
- Are all third-party SDKs version-locked and encapsulated?
- Is startup-time validation in place for required config?
- What happens when a downstream changes contract or behavior?

### Section 12: Documentation & Maintenance
- Could a new developer understand this module without help?
- Are all contracts (inputs/outputs/errors) typed and discoverable?
- Is there documentation for scale, auth, failures, and usage boundaries?
- Have all runtime assumptions been written down?

## Strategic Risk & Readiness Interrogation

### Execution Risk Questions
- What **critical edge cases** surface under concurrency, retries, latency, or degraded conditions?
- What **failure types** emerge *only* in production? (retries causing duplicates, state corruption, race conditions)
- What **implicit trust assumptions** exist around identity, access, or caller behavior?
- If the system returns **partial success**, does the caller know what actually happened?

### Safety, Scope & Security
- Could the system be **misused or overused** by a legitimate caller? (retry 100 times?)
- What happens if a **client misbehaves**, lies, or times out mid-request?
- If this spans **tenants, regions, or identities**, how are separation, access, and constraints enforced?
- Is **authorization** fully contextual? Or can a privileged path be reused with the wrong payload?

### Change Tolerance & Drift
- What **silent changes** to upstream/third-party services could **break behavior**? How do we detect and adapt?
- If **configuration, time, or environment** changes between regions, how does this code react?
- Could the system **fail subtly** instead of loudly? Would we know?

### Degradation, Scale, and Cost
- What's the **scaling model** - linear, spiky, or bottlenecked?
- What's the **run cost** at 10x, 100x usage? Bound by quotas, memory, or I/O?
- Does this degrade **gracefully** under pressure - or catastrophically?

### Observability & Debuggability
- If a user reports "it broke," can we **trace the incident** from logs alone?
- Are **all key decision points logged** with identifiers, timestamps, and reasons?
- Can we **differentiate user error, infra error, and system bug** in telemetry?
- Is there a **reliable retry or recovery** mechanism when things fail?

### Recovery & Repair
- If this system **crashes, resets, or restarts**, can state be recovered or replayed?
- If a bug silently corrupts state, **how far does it propagate before we detect it?**
- Can this system be **re-initialized safely** or **re-synced** without data loss or collisions?

### Architecture Awareness
- Does this feature **violate layering**, cause tight coupling, or introduce circular dependencies?
- If reused in **async flows**, **long-lived processes**, or **multi-actor contexts**, does behavior remain safe?
- What happens if it's **called from a context we didn't plan for** - CLI, scheduler, webhook, etc.?

### Time, Ordering, and Uncertainty
- Are we assuming **perfect time sync**? What about clock skew, leap seconds, or timezone variance?
- Are operations assumed to be **instantaneous or sequential**? Can they arrive **out-of-order or delayed**?

### Postmortem Forecasting
- What **single point of failure** here could trigger a major incident?
- What **human error paths** exist (misconfig, misuse, missing setup)?
- If this fails publicly, what's our **blame radius** - one user, one region, or everything?

### Design Regret Preview
- What decisions **seem harmless now**, but will cause long-term regret? (Hardcoded logic, weak abstractions, ambiguous states, logging gaps)
- What features are **under-tested, under-specified, or silently assumed**?

## Red Flags (Instant Fail)
- "It should work" without testing
- Missing error handling strategy
- No logging in critical paths
- Unbounded operations (no limits, pagination, timeouts)
- Hard-coded configuration values
- Missing cancellation support in async operations
- Circular dependencies
- Single point of failure without mitigation
- No retry or circuit breaker for external calls
- Secrets in code or config files
- Missing input validation at boundaries
- No observability instrumentation

## Assessment Directive
Assume the implementer's job is on the line. If this ships and fails, they present the root cause to leadership.

Deliver knowledge no one else has:
- Dead paths that look successful
- False success cases that hide failures
- Broken retry logic
- Silent failures that corrupt state
- Bad assumptions that won't trigger until version 1.3 or load spike #7

Show what the system **pretends is safe** - and prove it's not.

This is insurance against humiliation. Deliver insight like it's a postmortem you prevented. Because it is.

## Output Requirements
- No code generation
- Strategic design insights only
- Identify all critical risks and edge cases
- Provide clear recommendations for mitigations
- Flag architectural violations or coupling issues
- Highlight observability and testing gaps
- Forecast operational and scale challenges
- Be direct and specific - no hedging
