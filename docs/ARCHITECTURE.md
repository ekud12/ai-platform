# Project Architecture Map

> Auto-updated by Wiggum after each implementation cycle.
> Last updated: 2026-01-08

## Solution Structure

```
project/
├── src/
│   └── Test/
│       ├── Program.cs
│       ├── GreetingService.cs
│       ├── GreetingServiceTests.cs
│       └── Test.csproj
└── (to be mapped)
```

## Key Components

| Component | Purpose | Location |
|-----------|---------|----------|
| Program | Application Entry Point & API Config | project/src/Test/Program.cs |
| GreetingService | Core Domain Logic | project/src/Test/GreetingService.cs |

## Dependencies

- Microsoft.AspNetCore.OpenApi (8.0.0)
- Swashbuckle.AspNetCore (6.5.0)

## Data Flow

- Request -> Program (MapGet) -> GetGreetingHandler -> GreetingService -> Response
