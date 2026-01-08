# .NET Solution Management Rules

## Purpose

Standards for organizing .NET solutions, project structure, and naming conventions.

## Authority

Governs all .sln files and project organization.

## Scope

Applies to solution structure, project naming, and build configuration.

## Constraints

- Solutions must be self-documenting through structure
- Projects must have clear ownership and boundaries
- Build settings must be centralized

## Rule Format

All rules use the CS-SLN prefix.

---

## CS-SLN-001 — Domain-Based Project Organization
**Severity: Major**

**Rule**
Large solutions MUST organize projects into domain folders under `src/Domains/{DomainName}/`.

**Bad Pattern**
```
src/
├── MyApp.Api/
├── MyApp.Services/
├── MyApp.Data/
├── MyApp.Auth/
├── MyApp.AuthServices/
└── MyApp.AuthData/
```

**Good Pattern**
```
src/
├── Domains/
│   ├── Auth/
│   │   ├── Auth.Api/
│   │   ├── Auth.Contracts/
│   │   └── Auth.Orchestrator/
│   └── Content/
│       ├── Content.Api/
│       ├── Content.Contracts/
│       └── Content.Orchestrator/
└── Infrastructure/
    ├── Infra.Cache/
    └── Infra.Messaging/
```

---

## CS-SLN-002 — Domain Project Naming Convention
**Severity: Major**

**Rule**
Domain projects MUST follow `{Domain}.{Layer}` naming: Api, Contracts, Client, Orchestrator, Webhooks.

**Bad Pattern**
```
Appointments/
├── AppointmentsController/
├── AppointmentsDtos/
└── AppointmentsLogic/
```

**Good Pattern**
```
Appointments/
├── Appointments.Api/           # REST endpoints
├── Appointments.Contracts/     # DTOs, validators
├── Appointments.Client/        # HTTP clients for external APIs
├── Appointments.Orchestrator/  # Business logic, caching
└── Appointments.Webhooks/      # Webhook handlers (optional)
```

---

## CS-SLN-003 — Infrastructure Library Naming
**Severity: Major**

**Rule**
Shared infrastructure libraries MUST use `Infra.{Category}` naming convention.

**Bad Pattern**
```
Infrastructure/
├── SharedCache/
├── CommonMessaging/
└── UtilityHelpers/
```

**Good Pattern**
```
Infrastructure/
├── Infra.Cache/
├── Infra.Messaging/
├── Infra.Messaging.Nats/      # Implementation-specific
├── Infra.Messaging.ServiceBus/
├── Infra.Observability/
└── Infra.Primitives/
```

---

## CS-SLN-004 — Directory.Build.props Required
**Severity: Critical**

**Rule**
Solutions MUST have a root `Directory.Build.props` enforcing global settings.

**Bad Pattern**
```xml
<!-- Each .csproj repeats settings -->
<PropertyGroup>
  <TargetFramework>net10.0</TargetFramework>
  <Nullable>enable</Nullable>
  <ImplicitUsings>enable</ImplicitUsings>
</PropertyGroup>
```

**Good Pattern**
```xml
<!-- Directory.Build.props at solution root -->
<Project>
  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <LangVersion>latest</LangVersion>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
  </PropertyGroup>
</Project>
```

---

## CS-SLN-005 — Central Package Management
**Severity: Critical**

**Rule**
Solutions MUST use `Directory.Packages.props` for centralized NuGet version management.

**Bad Pattern**
```xml
<!-- In each .csproj -->
<PackageReference Include="Serilog" Version="9.0.0" />
<PackageReference Include="Serilog" Version="8.0.0" /> <!-- Different version! -->
```

**Good Pattern**
```xml
<!-- Directory.Packages.props -->
<Project>
  <PropertyGroup>
    <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>
  </PropertyGroup>
  <ItemGroup>
    <PackageVersion Include="Serilog" Version="9.0.0" />
  </ItemGroup>
</Project>

<!-- In .csproj - no version needed -->
<PackageReference Include="Serilog" />
```

---

## CS-SLN-006 — Global.json SDK Pinning
**Severity: Major**

**Rule**
Solutions MUST have `global.json` pinning the .NET SDK version.

**Bad Pattern**
```
# No global.json - uses whatever SDK is installed
```

**Good Pattern**
```json
{
  "sdk": {
    "version": "10.0.100",
    "rollForward": "latestFeature",
    "allowPrerelease": false
  }
}
```

---

## CS-SLN-007 — Template Projects for Scaffolding
**Severity: Info**

**Rule**
Solutions with repeated patterns SHOULD have template projects under `src/Templates/`.

**Good Pattern**
```
src/Templates/
├── Template.Api/           # Base API with auth, OpenAPI, compression
├── Template.Job/           # NATS job worker scaffold
├── Template.WebWorker/     # Background worker scaffold
└── Template.Extensions/    # Extension method patterns
```

---

## CS-SLN-008 — Contracts Project Isolation
**Severity: Critical**

**Rule**
DTOs and validation rules MUST be in a separate `{Domain}.Contracts` project with NO business logic dependencies.

**Rationale**
Contracts projects can be shared as NuGet packages. They must not pull in business logic or infrastructure.

**Bad Pattern**
```xml
<!-- Contracts.csproj referencing business logic -->
<ProjectReference Include="..\Domain.Services\Domain.Services.csproj" />
```

**Good Pattern**
```xml
<!-- Contracts.csproj - minimal dependencies -->
<PackageReference Include="FluentValidation" />
<PackageReference Include="System.Text.Json" />
<!-- No project references except Infra.Primitives -->
```

---

## CS-SLN-009 — Tooling Projects for Analyzers
**Severity: Info**

**Rule**
Custom Roslyn analyzers and source generators SHOULD be in `src/Tooling/` targeting netstandard2.0.

**Good Pattern**
```
src/Tooling/
├── Tooling.Analyzers/         # Custom architectural rules
├── Tooling.CodeFix/           # Auto-fix providers
└── Tooling.SourceGenerators/  # Custom generators
```

---

## CS-SLN-010 — Scripts and Utilities Folder
**Severity: Info**

**Rule**
Utility scripts MUST be in a `scripts/` folder at solution root, organized by purpose.

**Good Pattern**
```
scripts/
├── database/
│   ├── migrate.py
│   └── seed.sql
├── deployment/
│   ├── deploy.ps1
│   └── rollback.ps1
└── utilities/
    └── CompressPoi/    # .NET utility project
```
