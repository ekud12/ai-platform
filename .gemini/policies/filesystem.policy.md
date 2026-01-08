# Filesystem Policy

## Purpose

This file defines allowed filesystem access for agents.

## Authority

Filesystem restrictions are mandatory.

## Scope

All file operations by all agents.

## Constraints

- Only whitelisted paths accessible
- Write requires explicit permission
- Sensitive paths blocked

## Access Rules

### Read Access

**Allowed**:
- Project source directories
- Configuration files (non-secret)
- Documentation directories (`.gemmem/`)
- Agent definition files

**Blocked**:
- System directories
- User home directories (except project)
- Credential files
- Environment files

### Write Access

**Allowed (with approval)**:
- Project source files
- Generated output directories
- Temporary workspace

**Blocked**:
- Configuration files
- System files
- Binary directories
- Git internals

### Path Patterns

```
# Allowed read
/project/**/*.cs
/project/**/*.ts
/project/**/*.md

# Blocked always
/etc/**
~/.ssh/**
**/.env
**/secrets/**
**/credentials/**
```

## Enforcement

- Path validation before access
- Symlink resolution and re-check
- Access logged for audit
- Violations block and alert
