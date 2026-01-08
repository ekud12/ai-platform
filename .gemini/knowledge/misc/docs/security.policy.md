# Security Policy

## Purpose

This file defines security rules for shell command execution, branch protection, and secret detection.

## Authority

Security restrictions are mandatory and take highest precedence.

## Scope

All shell/terminal command execution by agents, git operations, and file writes.

---

## Configuration Files (Single Source of Truth)

All security configurations are managed in JSON files located in `.gemini/hooks/`:

| File | Purpose | Reference |
|------|---------|-----------|
| `blocked-commands.json` | Command allow/block patterns | [View](#command-rules) |
| `protected-branches.json` | Git branch protection | [View](#branch-protection) |
| `secret-patterns.json` | Secret detection patterns | [View](#secret-detection) |

> **IMPORTANT**: The JSON files are the authoritative source. This document serves as human-readable documentation. If discrepancies exist, the JSON files take precedence.

---

## Command Rules

**Source**: `.gemini/hooks/blocked-commands.json`

### Structure

```json
{
  "blocked_patterns": [
    { "pattern": "regex", "reason": "why blocked", "severity": "critical|high|medium" }
  ],
  "allowed_patterns": [
    { "pattern": "regex", "reason": "why allowed" }
  ],
  "default_action": "ask|block|allow"
}
```

### Priority Order

1. **Blocked patterns** - Checked first, blocks if matched
2. **Allowed patterns** - If matched, command is allowed
3. **Default action** - Applied if no patterns match

### Severity Levels

| Severity | Description | Examples |
|----------|-------------|----------|
| `critical` | Destructive, irreversible, or security breach | `rm -rf`, `sudo`, cloud CLIs |
| `high` | Potentially dangerous, data loss risk | `chmod`, `git push`, registry edits |
| `medium` | Requires caution, manual preferred | `git rebase`, `ssh` |

### Categories (in JSON file)

- **Destructive operations**: `rm -rf`, `rmdir /s`, `del /f`, `Remove-Item -Recurse`
- **Privilege escalation**: `sudo`, `runas`, `Start-Process -Verb RunAs`
- **Permission changes**: `chmod`, `chown`, `icacls`
- **Git mutations**: `git push`, `git commit`, `git reset --hard`, `git clean`
- **Cloud CLIs**: `aws`, `az`, `gcloud`, `kubectl`, `terraform`
- **Remote execution**: `curl | sh`, `Invoke-Expression`
- **System operations**: `mkfs`, `dd`, `format`, `diskpart`, `reg add`

---

## Branch Protection

**Source**: `.gemini/hooks/protected-branches.json`

### Structure

```json
{
  "protected_branches": [
    { "name": "main", "reason": "Production branch - use feature branches and PRs" }
  ],
  "settings": {
    "block_on_protected": true,
    "allow_read_operations": true
  }
}
```

### Default Protected Branches

| Branch | Reason |
|--------|--------|
| `main` | Production branch |
| `master` | Production branch |
| `production` | Production deployment |
| `release` | Release branch |
| `develop` | Integration branch |

### Behavior

- When on a protected branch, tool execution is blocked
- Read-only git operations (`git status`, `git diff`, `git log`) are always allowed
- Agents must create feature branches for any work

---

## Secret Detection

**Source**: `.gemini/hooks/secret-patterns.json`

### Structure

```json
{
  "secret_patterns": [
    {
      "id": "unique-id",
      "pattern": "regex",
      "flags": "i",
      "description": "Human readable",
      "severity": "critical|high|medium",
      "requires_context": ["optional", "keywords"]
    }
  ],
  "exclusions": [
    { "pattern": "regex for file paths to skip" }
  ],
  "settings": {
    "scan_file_writes": true,
    "block_on_detection": true
  }
}
```

### Detected Secret Types

| ID | Description | Severity |
|----|-------------|----------|
| `jwt-token` | JSON Web Token | critical |
| `openai-api-key` | OpenAI API Key | critical |
| `anthropic-api-key` | Anthropic API Key | critical |
| `google-api-key` | Google API Key | critical |
| `github-pat` | GitHub Personal Access Token | critical |
| `aws-access-key` | AWS Access Key ID | critical |
| `azure-connection-string` | Azure Storage Connection String | critical |
| `slack-token` | Slack Token | critical |
| `stripe-api-key` | Stripe Live API Key | critical |
| `private-key-header` | Private Key File | critical |
| `generic-password` | Hardcoded Password | high |
| `generic-api-key` | Generic API Key | high |
| `connection-string` | Database Connection String | critical |

### Exclusions

Files matching these patterns are excluded from secret scanning:
- `*.example`, `*.sample`, `*.template`
- Files in test data directories

---

## Enforcement

The `before-tool.js` hook enforces all security rules:

1. **Panic check** - Looks for `.panic` file (immediate halt)
2. **Branch guard** - Loads from `protected-branches.json`
3. **Command guard** - Loads from `blocked-commands.json`
4. **Secret scanner** - Loads from `secret-patterns.json`

### Adding New Rules

1. Edit the appropriate JSON file
2. Changes take effect immediately (files are loaded per-execution)
3. No code changes required

### Testing Changes

```bash
# Test a command pattern
node .gemini/hooks/before-tool.js <<< '{"tool":"bash","parameters":{"command":"your-command"}}'

# Test a file write with potential secret
node .gemini/hooks/before-tool.js <<< '{"tool":"write_file","parameters":{"content":"sk-test123..."}}'
```

---

## Logging

All security events are logged to:
- `.gemini/logs/blocked-commands.log` - Blocked command attempts
- `.gemini/logs/secret-detections.log` - Secret detection events

Enable/disable logging in the respective JSON file's `settings` section.
