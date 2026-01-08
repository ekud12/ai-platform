# Network Policy

## Purpose

This file defines network access restrictions for agents.

## Authority

Network restrictions are mandatory.

## Scope

All network operations by all agents.

## Constraints

- Default deny all network access
- Whitelist required for access
- All traffic logged

## Access Rules

### Default State

All network access is blocked by default.

### Whitelisted Endpoints

Agents may access (with approval):
- Package registries (npm, NuGet)
- Documentation sites
- Approved APIs

### Blocked Always

- Internal network resources
- Social media
- Email services
- Arbitrary URLs

## Traffic Controls

### Outbound

- HTTPS required
- Certificate validation required
- No raw socket access
- Rate limited

### Inbound

- No listening sockets
- No accepting connections
- No server capabilities

## DNS Controls

- Approved domains only
- No IP address access
- DNS queries logged

## Enforcement

- Firewall rules applied
- Proxy inspection if needed
- Violations block and alert
