# Security Policy

## Purpose

This file defines security rules for shell command execution.

## Authority

Security restrictions are mandatory and take highest precedence.

## Scope

All shell/terminal command execution by agents.

## Command Rules

### Priority 100: Hard Block (Deny)

These commands are **NEVER** allowed:

| Pattern | Reason |
|---------|--------|
| `rm -rf` | Destructive file deletion |
| `sudo` | Privilege escalation |
| `chmod` | Permission modification |
| `ssh`, `scp`, `telnet`, `nc` | Remote access |
| `vim`, `nano` | Interactive editors |
| `shutdown`, `reboot` | System control |
| `taskkill` | Process termination |
| `aws`, `az`, `gcloud` | Cloud provider CLIs |
| `kubectl`, `terraform` | Infrastructure tools |
| `docker` | Container operations |
| `git push`, `git commit`, `git add` | Source control mutations |
| `git checkout`, `git reset`, `git clean` | Destructive git operations |

### Priority 90: Ask User

These commands require explicit user approval:

| Pattern | Reason |
|---------|--------|
| `npm install`, `yarn add`, `pnpm add` | Package installation |
| `pip install` | Python package installation |
| `dotnet add package` | NuGet package installation |

### Priority 80: Allow Silent

These commands are safe and allowed without prompting:

| Pattern | Purpose |
|---------|---------|
| `git status` | View repository state |
| `git diff` | View changes |
| `dotnet build` | Compile project |
| `dotnet test` | Run tests |
| `npm run lint` | Code linting |
| `npm test` | Run tests |
| `ls`, `dir` | List directory contents |
| `echo` | Output text |
| `mkdir` | Create directory |

### Priority 10: Default (Ask)

Any command not matching above rules requires user confirmation.

## Enforcement

1. Commands are matched against patterns in priority order
2. First matching rule determines the decision
3. Denied commands are blocked with explanation
4. Asked commands wait for user confirmation
5. All command attempts are logged
