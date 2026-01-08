# Feature Specification Template

> Use this template to create specifications for Wiggum to process.

## Feature Name

[Give your feature a clear, concise name]

## Overview

[Provide a brief description of what this feature does and why it's needed]

## User Story

As a [type of user],
I want [goal/desire],
So that [benefit/value].

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Technical Requirements

### Domain

- [ ] .NET / C#
- [ ] TypeScript / JavaScript
- [ ] Both

### Components Affected

List the main components, services, or modules that will be created or modified:

1. Component A
2. Component B
3. Component C

### Data Model

Describe any new entities, DTOs, or data structures:

```
Entity: [Name]
- property1: type
- property2: type
```

### API Endpoints (if applicable)

```
[METHOD] /api/[endpoint]
Request: { ... }
Response: { ... }
```

### Business Rules

1. Rule 1
2. Rule 2
3. Rule 3

## Constraints

- Must follow existing code patterns
- Must include unit tests
- Must pass all linting rules
- [Add any specific constraints]

## Out of Scope

- Item 1
- Item 2

## Dependencies

- Dependency 1
- Dependency 2

## Notes

[Any additional notes or considerations]

---

## Example: User Registration Feature

### Feature Name

User Registration

### Overview

Allow new users to register accounts with email and password authentication.

### User Story

As a new visitor,
I want to create an account,
So that I can access personalized features.

### Acceptance Criteria

- [ ] User can register with email and password
- [ ] Email must be unique
- [ ] Password must meet complexity requirements
- [ ] Confirmation email is sent after registration
- [ ] User cannot log in until email is confirmed

### Technical Requirements

#### Domain

- [x] .NET / C#

#### Components Affected

1. `Users.Orchestrator` - Add registration endpoint
2. `Users.Contracts` - Add DTOs
3. `Infra.Auth` - Add password hashing service

#### Data Model

```
Entity: User
- Id: Guid
- Email: string (unique)
- PasswordHash: string
- EmailConfirmed: bool
- CreatedAt: DateTimeOffset
```

#### API Endpoints

```
POST /api/users/register
Request: { email: string, password: string }
Response: { userId: string, message: string }
```

#### Business Rules

1. Email must be valid format
2. Password minimum 8 characters with uppercase, lowercase, number
3. Rate limit: 5 registration attempts per IP per hour

### Constraints

- Use BCrypt for password hashing
- Follow existing API patterns in Users.Orchestrator
- Add validation using FluentValidation

### Out of Scope

- Social login (OAuth)
- Two-factor authentication
- Password reset flow

### Dependencies

- BCrypt.Net-Next NuGet package
- Existing email service in Infra.Messaging
