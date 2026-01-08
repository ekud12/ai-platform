# TypeScript Performance Rules

## Purpose
Standards for Frontend Performance.

## Authority
Governs all React/Frontend code.

---

## TS-PERF-001 — Bundle Size Budget
**Severity: Critical**

**Rule**
Large features MUST be code-split.

**Bad Pattern**
```typescript
import { HeavyChart } from './HeavyChart'; // Bundled in main.js
```

**Good Pattern**
```typescript
const HeavyChart = lazy(() => import('./HeavyChart')); // Separate chunk
```

---

## TS-PERF-002 — Tree Shaking
**Severity: Major**

**Rule**
Avoid "Barrel Files" (`index.ts`) that re-export everything if they break tree-shaking.

**Bad Pattern**
```typescript
export * from './components'; // Imports EVERYTHING
```

**Good Pattern**
```typescript
export { Button } from './Button'; // Named export
```

---

## TS-PERF-003 — Lazy Loading
**Severity: Major**

**Rule**
Routes MUST be Lazy Loaded.

**Bad Pattern**
```typescript
<Route path="/admin" component={AdminPanel} />
```

**Good Pattern**
```typescript
<Route path="/admin" component={lazy(() => import('./AdminPanel'))} />
```

---

## TS-PERF-004 — Memoization
**Severity: Warning**

**Rule**
Memoize expensive computations (`useMemo`).

**Bad Pattern**
```typescript
const sorted = items.sort(); // Runs on every render!
```

**Good Pattern**
```typescript
const sorted = useMemo(() => items.sort(), [items]);
```

---

## TS-PERF-005 — Virtual Lists
**Severity: Major**

**Rule**
Lists > 100 items MUST be virtualized.

**Bad Pattern**
```typescript
items.map(i => <Item data={i} />) // 1000s of DOM nodes
```

**Good Pattern**
```typescript
<VirtualList items={items} renderItem={...} /> // Only renders visible
```

---

## TS-PERF-006 — Debounce and Throttle
**Severity: Warning**

**Rule**
Search/Scroll handlers MUST be debounced/throttled.

**Bad Pattern**
```typescript
<input onChange={doSearch} /> // API call on every keystroke
```

**Good Pattern**
```typescript
<input onChange={debounce(doSearch, 300)} />
```

---

## TS-PERF-007 — Avoid Memory Leaks
**Severity: Critical**

**Rule**
`useEffect` MUST return cleanup function.

**Bad Pattern**
```typescript
useEffect(() => {
    window.addEventListener('resize', handle);
}); // Leaks listener
```

**Good Pattern**
```typescript
useEffect(() => {
    window.addEventListener('resize', handle);
    return () => window.removeEventListener('resize', handle);
}, []);
```

---

## TS-PERF-008 — Minimize Dependencies
**Severity: Warning**

**Rule**
Do not import huge libs for small tasks (e.g., Lodash).

**Bad Pattern**
```typescript
import _ from 'lodash';
_.map(arr, ...);
```

**Good Pattern**
```typescript
arr.map(...); // Native JS is faster
```

---

## TS-PERF-009 — Image Optimization
**Severity: Major**

**Rule**
Images MUST be optimized (WebP/AVIF) and sized correctly.

**Bad Pattern**
```typescript
<img src="huge-raw-photo.png" />
```

**Good Pattern**
```typescript
<img src="photo.webp" width={800} height={600} loading="lazy" />
```

---

## TS-PERF-010 — Avoid Render Blocking
**Severity: Critical**

**Rule**
Third-party scripts MUST be `async` or `defer`.

**Bad Pattern**
```html
<script src="analytics.js"></script> <!-- Blocks parsing -->
```

**Good Pattern**
```html
<script src="analytics.js" defer></script>
```

---

## TS-PERF-011 — Web Workers for Heavy Computation
**Severity: Major**

**Rule**
CPU-intensive operations (>50ms) MUST be offloaded to Web Workers.

**Bad Pattern**
```typescript
// On main thread - blocks UI
function processLargeDataset(data: number[]): number[] {
    return data.map(x => expensiveCalculation(x)); // UI freezes
}
```

**Good Pattern**
```typescript
// worker.ts
self.onmessage = (e) => {
    const result = e.data.map(expensiveCalculation);
    self.postMessage(result);
};

// main.ts
const worker = new Worker("worker.js");
worker.postMessage(data);
worker.onmessage = (e) => setResult(e.data);
```

---

## TS-PERF-012 — Service Worker Caching
**Severity: Major**

**Rule**
Static assets MUST be cached via Service Worker for offline support and performance.

**Bad Pattern**
```typescript
// No service worker - every page load fetches from network
```

**Good Pattern**
```typescript
// service-worker.ts
self.addEventListener("install", (event) => {
    event.waitUntil(
        caches.open("v1").then((cache) =>
            cache.addAll(["/", "/app.js", "/styles.css"])
        )
    );
});

self.addEventListener("fetch", (event) => {
    event.respondWith(
        caches.match(event.request).then((r) => r || fetch(event.request))
    );
});
```

---

## TS-PERF-013 — CSS-in-JS Extraction
**Severity: Major**

**Rule**
CSS-in-JS MUST extract static styles at build time. Runtime style generation forbidden in hot paths.

**Bad Pattern**
```typescript
// Generates CSS on every render
const Button = styled.button`
    background: ${props => props.primary ? "blue" : "gray"};
`;
```

**Good Pattern**
```typescript
// Use static extraction or CSS modules
import styles from "./Button.module.css";

// Or use variants with pre-generated CSS
const Button = styled.button.variants({
    primary: { background: "blue" },
    secondary: { background: "gray" }
});
```

---

## TS-PERF-014 — Compiler-Optimized Reactivity
**Severity: Info**

**Rule**
Prefer compiler-optimized reactivity (React Compiler, Solid, signals) over manual memoization.

**Bad Pattern**
```typescript
// Manual memoization everywhere
const Component = () => {
    const value = useMemo(() => compute(a, b), [a, b]);
    const handler = useCallback(() => doThing(value), [value]);
    return <Child value={value} onClick={handler} />;
};
```

**Good Pattern**
```typescript
// With React Compiler or signal-based framework
const Component = () => {
    const value = compute(a, b); // Compiler handles memoization
    const handler = () => doThing(value);
    return <Child value={value} onClick={handler} />;
};
```