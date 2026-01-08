# Agent Ownership

## Purpose
Defines which Role owns which domain concern.

## Ownership Matrix

### 1. Planning & Architecture
| Concern | Owner Node |
|---------|------------|
| Task Decomposition | **PLANNER** |
| Dependency Ordering | **PLANNER** |
| Risk Assessment | **PLANNER** |

### 2. Implementation (.NET)
| Concern | Owner Node |
|---------|------------|
| C# Syntax Generation | **CODER-NET** |
| C# Async Implementation | **CODER-NET** |
| C# API Creation | **CODER-NET** |

### 3. Implementation (TypeScript)
| Concern | Owner Node |
|---------|------------|
| TS Component Creation | **CODER-TS** |
| TS State Management | **CODER-TS** |
| TS API Consumption | **CODER-TS** |

### 4. Quality Assurance (.NET)
| Concern | Owner Node |
|---------|------------|
| C# Security Audit | **REV-NET** |
| C# Performance Audit | **REV-NET** |
| C# Memory Audit | **REV-NET** |

### 5. Quality Assurance (TypeScript)
| Concern | Owner Node |
|---------|------------|
| TS Security Audit | **REV-TS** |
| TS Performance Audit | **REV-TS** |
| TS Type Safety Audit | **REV-TS** |

### 6. System Integrity
| Concern | Owner Node |
|---------|------------|
| Constitution Enforcement | **META** |
| Cross-Language Consistency | **META** |
| Final Approval | **META** |
| Penetration Testing | **RED-TEAM** |