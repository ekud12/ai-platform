# Memory Wipe Protocol

## Purpose

This file defines the memory purge procedure for sensitive data.

## Authority

Memory wipe is for data protection scenarios.

## Scope

Clearing sensitive data from system.

## Constraints

- Must be complete
- Must be verifiable
- Must preserve audit trail

## Trigger Conditions

- Session end with sensitive data
- Security incident response
- Compliance requirement
- Human command

## Procedure

### Step 1: Identification

1. Identify sensitive data locations
2. Map memory regions
3. List cached data
4. Document scope

### Step 2: Agent Memory

1. Clear agent working memory (Session Context)
2. Purge cached results
3. Reset agent state
4. Verify clear

### Step 3: System Memory

1. Clear conversation history
2. Purge temporary files
3. Clear caches
4. Overwrite buffers

### Step 4: Persistent Storage

1. Identify sensitive files
2. Secure delete (not just unlink)
3. Clear database caches
4. Verify deletion

## What Is Preserved

- Audit logs (non-sensitive)
- System configuration
- Rule definitions
- Agent definitions
- Architectural Maps (`.gemmem/snapshot.json`)
- Learned Lessons (`.gemmem/history.json`)

## What Is Wiped

- Conversation content
- Processed data
- Cached results
- Temporary files
- Session state
