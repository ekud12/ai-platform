# TypeScript Observability Rules

## Purpose

Standards for structured logging, distributed tracing, and metrics in TypeScript/Node.js applications.

## Authority

Governs all observability instrumentation in TypeScript applications. Production observability is mandatory.

## Scope

Applies to logging, tracing, metrics, health checks, and error handling.

---

## TS-OBS-001 — No Console in Production

**Severity: Critical**

**Rule**
`console.log`, `console.error`, `console.warn` are FORBIDDEN in production code. Use structured logging.

**Bad Pattern**
```typescript
function processOrder(order: Order): void {
  console.log('Processing order:', order.id);
  console.error('Order failed:', error.message);
}
```

**Good Pattern**
```typescript
import { logger } from '@/shared/logger';

function processOrder(order: Order): void {
  logger.info('Processing order', { orderId: order.id, customerId: order.customerId });
  logger.error('Order processing failed', { orderId: order.id, error: error.message });
}
```

**Rationale**
Structured logging enables filtering, aggregation, and analysis in production systems.

---

## TS-OBS-002 — Structured Logging Format

**Severity: Critical**

**Rule**
All logs MUST use structured JSON format with named properties, not string concatenation.

**Bad Pattern**
```typescript
logger.info(`User ${userId} created order ${orderId} for $${amount}`);
logger.error('Failed to process: ' + error.message);
```

**Good Pattern**
```typescript
logger.info('Order created', {
  userId,
  orderId,
  amount,
  currency: 'USD'
});

logger.error('Order processing failed', {
  orderId,
  error: error.message,
  stack: error.stack
});
```

**Rationale**
Structured logs are machine-parseable and enable powerful querying.

---

## TS-OBS-003 — Correlation ID in All Logs

**Severity: Critical**

**Rule**
Every log entry MUST include correlation ID, request ID, or trace ID.

**Bad Pattern**
```typescript
logger.info('Processing request', { path: '/orders' });
// No correlation - can't trace across services
```

**Good Pattern**
```typescript
import { AsyncLocalStorage } from 'node:async_hooks';

const requestContext = new AsyncLocalStorage<RequestContext>();

logger.info('Processing request', {
  correlationId: requestContext.getStore()?.correlationId,
  requestId: requestContext.getStore()?.requestId,
  path: '/orders'
});
```

**Rationale**
Correlation IDs enable distributed tracing across services and requests.

---

## TS-OBS-004 — AsyncLocalStorage for Context

**Severity: Major**

**Rule**
Request context MUST use `AsyncLocalStorage` for automatic propagation across async boundaries.

**Bad Pattern**
```typescript
// Manually passing context everywhere
async function processOrder(order: Order, correlationId: string): Promise<void> {
  await validateOrder(order, correlationId);
  await chargePayment(order, correlationId);
  await sendNotification(order, correlationId);
}
```

**Good Pattern**
```typescript
import { AsyncLocalStorage } from 'node:async_hooks';

type RequestContext = {
  correlationId: string;
  userId?: string;
  traceId: string;
};

export const requestContext = new AsyncLocalStorage<RequestContext>();

// Middleware sets context once
app.use((req, res, next) => {
  const ctx: RequestContext = {
    correlationId: req.headers['x-correlation-id'] as string ?? crypto.randomUUID(),
    userId: req.user?.id,
    traceId: crypto.randomUUID()
  };
  requestContext.run(ctx, next);
});

// All functions automatically have access
async function processOrder(order: Order): Promise<void> {
  const ctx = requestContext.getStore();
  logger.info('Processing order', { ...ctx, orderId: order.id });
}
```

**Rationale**
AsyncLocalStorage provides clean context propagation without parameter drilling.

---

## TS-OBS-005 — Log at All Exit Points

**Severity: Major**

**Rule**
Every function MUST log at entry (debug) and exit (info for success, error for failure).

**Bad Pattern**
```typescript
async function createOrder(request: CreateOrderRequest): Promise<Order> {
  const order = await orderRepository.create(request);
  return order; // No logging
}
```

**Good Pattern**
```typescript
async function createOrder(request: CreateOrderRequest): Promise<Order> {
  logger.debug('Creating order', { customerId: request.customerId });

  try {
    const order = await orderRepository.create(request);
    logger.info('Order created successfully', {
      orderId: order.id,
      customerId: request.customerId,
      total: order.total
    });
    return order;
  } catch (error) {
    logger.error('Failed to create order', {
      customerId: request.customerId,
      error: error instanceof Error ? error.message : String(error)
    });
    throw error;
  }
}
```

**Rationale**
Entry/exit logging enables complete request tracing and performance analysis.

---

## TS-OBS-006 — OpenTelemetry Integration

**Severity: Major**

**Rule**
Distributed systems MUST use OpenTelemetry for tracing with proper span creation.

**Bad Pattern**
```typescript
// No tracing
async function processPayment(orderId: string): Promise<PaymentResult> {
  return await paymentClient.charge(orderId);
}
```

**Good Pattern**
```typescript
import { trace, SpanStatusCode } from '@opentelemetry/api';

const tracer = trace.getTracer('order-service');

async function processPayment(orderId: string): Promise<PaymentResult> {
  return tracer.startActiveSpan('processPayment', async (span) => {
    try {
      span.setAttribute('orderId', orderId);
      const result = await paymentClient.charge(orderId);
      span.setAttribute('paymentId', result.paymentId);
      span.setStatus({ code: SpanStatusCode.OK });
      return result;
    } catch (error) {
      span.setStatus({ code: SpanStatusCode.ERROR, message: error.message });
      span.recordException(error);
      throw error;
    } finally {
      span.end();
    }
  });
}
```

**Rationale**
OpenTelemetry provides vendor-neutral distributed tracing and observability.

---

## TS-OBS-007 — HTTP Client Tracing

**Severity: Major**

**Rule**
All outgoing HTTP requests MUST log duration, status, and propagate trace context.

**Bad Pattern**
```typescript
const response = await fetch('https://api.payment.com/charge');
// No logging, no tracing
```

**Good Pattern**
```typescript
async function httpRequest(url: string, options: RequestInit): Promise<Response> {
  const startTime = performance.now();
  const ctx = requestContext.getStore();

  const headers = new Headers(options.headers);
  headers.set('X-Correlation-Id', ctx?.correlationId ?? '');
  headers.set('traceparent', getTraceparent());

  try {
    const response = await fetch(url, { ...options, headers });
    const duration = performance.now() - startTime;

    logger.info('HTTP request completed', {
      url,
      method: options.method ?? 'GET',
      status: response.status,
      durationMs: Math.round(duration),
      correlationId: ctx?.correlationId
    });

    return response;
  } catch (error) {
    const duration = performance.now() - startTime;
    logger.error('HTTP request failed', {
      url,
      method: options.method ?? 'GET',
      durationMs: Math.round(duration),
      error: error.message,
      correlationId: ctx?.correlationId
    });
    throw error;
  }
}
```

**Rationale**
HTTP logging enables latency analysis and debugging of integration issues.

---

## TS-OBS-008 — Health Check Endpoints

**Severity: Critical**

**Rule**
All services MUST expose `/health/live` and `/health/ready` endpoints.

**Bad Pattern**
```typescript
app.get('/health', (req, res) => {
  res.json({ status: 'ok' }); // No dependency checks
});
```

**Good Pattern**
```typescript
type HealthStatus = 'healthy' | 'degraded' | 'unhealthy';

interface HealthCheck {
  name: string;
  status: HealthStatus;
  duration?: number;
  error?: string;
}

app.get('/health/live', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

app.get('/health/ready', async (req, res) => {
  const checks: HealthCheck[] = await Promise.all([
    checkDatabase(),
    checkRedis(),
    checkExternalApi()
  ]);

  const overallStatus = checks.every(c => c.status === 'healthy')
    ? 'healthy'
    : checks.some(c => c.status === 'unhealthy')
      ? 'unhealthy'
      : 'degraded';

  const statusCode = overallStatus === 'healthy' ? 200 : overallStatus === 'degraded' ? 200 : 503;

  res.status(statusCode).json({
    status: overallStatus,
    timestamp: new Date().toISOString(),
    checks
  });
});
```

**Rationale**
Separate liveness/readiness checks enable proper Kubernetes orchestration.

---

## TS-OBS-009 — Error Logging with Context

**Severity: Critical**

**Rule**
All errors MUST be logged with full context including stack trace, cause chain, and identifiers.

**Bad Pattern**
```typescript
catch (error) {
  logger.error('Something went wrong');
  throw error;
}
```

**Good Pattern**
```typescript
catch (error) {
  logger.error('Order processing failed', {
    orderId,
    customerId,
    operation: 'processOrder',
    error: {
      name: error instanceof Error ? error.name : 'UnknownError',
      message: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : undefined,
      cause: error instanceof Error && error.cause
        ? { message: (error.cause as Error).message }
        : undefined
    },
    correlationId: requestContext.getStore()?.correlationId
  });
  throw error;
}
```

**Rationale**
Rich error context enables effective debugging and postmortem analysis.

---

## TS-OBS-010 — Metrics Collection

**Severity: Major**

**Rule**
Key operations MUST emit metrics: counters for events, histograms for durations.

**Bad Pattern**
```typescript
// No metrics
async function processOrder(order: Order): Promise<void> {
  await chargePayment(order);
}
```

**Good Pattern**
```typescript
import { Counter, Histogram, Registry } from 'prom-client';

const ordersProcessed = new Counter({
  name: 'orders_processed_total',
  help: 'Total orders processed',
  labelNames: ['status']
});

const orderProcessingDuration = new Histogram({
  name: 'order_processing_duration_seconds',
  help: 'Order processing duration',
  buckets: [0.1, 0.5, 1, 2, 5, 10]
});

async function processOrder(order: Order): Promise<void> {
  const end = orderProcessingDuration.startTimer();
  try {
    await chargePayment(order);
    ordersProcessed.inc({ status: 'success' });
  } catch (error) {
    ordersProcessed.inc({ status: 'failure' });
    throw error;
  } finally {
    end();
  }
}
```

**Rationale**
Metrics enable alerting, capacity planning, and performance analysis.

---

## TS-OBS-011 — Startup Validation Logging

**Severity: Major**

**Rule**
Application startup MUST log configuration validation, dependencies, and metadata.

**Bad Pattern**
```typescript
app.listen(3000);
// No startup logging
```

**Good Pattern**
```typescript
async function bootstrap(): Promise<void> {
  logger.info('Application starting', {
    version: process.env.npm_package_version,
    nodeVersion: process.version,
    environment: process.env.NODE_ENV,
    commitSha: process.env.COMMIT_SHA
  });

  // Validate configuration
  const configResult = configSchema.safeParse(process.env);
  if (!configResult.success) {
    logger.error('Configuration validation failed', {
      errors: configResult.error.issues
    });
    process.exit(1);
  }
  logger.info('Configuration validated successfully');

  // Check dependencies
  await checkDatabaseConnection();
  logger.info('Database connection established');

  await checkRedisConnection();
  logger.info('Redis connection established');

  app.listen(config.port, () => {
    logger.info('Application started', {
      port: config.port,
      startupDurationMs: performance.now()
    });
  });
}
```

**Rationale**
Startup logging enables quick diagnosis of deployment issues.

---

## TS-OBS-012 — PII Redaction

**Severity: Critical**

**Rule**
Logs MUST NOT contain PII, passwords, tokens, or other sensitive data.

**Bad Pattern**
```typescript
logger.info('User login', {
  email: user.email,
  password: request.password, // NEVER
  authToken: token // NEVER
});
```

**Good Pattern**
```typescript
logger.info('User login', {
  userId: user.id,
  emailDomain: user.email.split('@')[1], // Only domain, not full email
  hasAuthToken: Boolean(token)
});

// Or use redaction
const redactedLogger = logger.child({
  redact: ['password', 'token', 'authorization', 'cookie', 'email']
});
```

**Rationale**
Logging PII creates compliance and security risks.

---

## Forbidden Patterns

- TS-OBS-FORBID-001: No `console.log/error/warn` in production code
- TS-OBS-FORBID-002: No string concatenation in log messages
- TS-OBS-FORBID-003: No logs without correlation/request ID
- TS-OBS-FORBID-004: No sensitive data (passwords, tokens, PII) in logs
- TS-OBS-FORBID-005: No missing error logging in catch blocks
- TS-OBS-FORBID-006: No missing health check endpoints
- TS-OBS-FORBID-007: No HTTP requests without duration logging
- TS-OBS-FORBID-008: No startup without configuration validation logging
- TS-OBS-FORBID-009: No silent error swallowing
- TS-OBS-FORBID-010: No unstructured log formats in production
