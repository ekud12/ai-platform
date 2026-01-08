# Command Policy

## Purpose

This file defines allowed command execution for agents.

## Authority

Command restrictions are mandatory.

## Scope

All shell and tool execution.

## Constraints

- Only whitelisted commands allowed
- Arguments validated
- Output captured and scanned

## Allowed Commands

### Build Tools

```
dotnet build
dotnet test
dotnet publish
npm install
npm run build
npm test
```

### Analysis Tools

```
dotnet format --verify-no-changes
eslint
prettier --check
```

### Version Control (read-only)

```
git status
git log
git diff
git show
```

## Blocked Commands

### Always Blocked

```
rm -rf
sudo
chmod
chown
curl
wget
ssh
scp
```

### Network Commands

```
ping
netcat
telnet
nmap
```

### System Commands

```
shutdown
reboot
kill
pkill
```

## Argument Validation

- No shell metacharacters
- No path traversal
- No environment injection
- Whitelisted flags only

## Execution Controls

- Timeout enforced
- Output size limited
- Exit codes captured
- Errors logged
