# .NET Docker Rules

## Purpose

Standards for containerizing .NET applications.

## Authority

Governs all Dockerfile and docker-compose configurations.

## Scope

Applies to container builds, orchestration, and local development environments.

## Constraints

- Images must be minimal and secure
- Builds must be reproducible
- Local development must mirror production

## Rule Format

All rules use the CS-DOCKER prefix.

---

## CS-DOCKER-001 — Multi-Stage Builds
**Severity: Critical**

**Rule**
Dockerfiles MUST use multi-stage builds to minimize image size.

**Rationale**
Multi-stage builds exclude SDK and build artifacts from the final image, reducing size and attack surface.

**Bad Pattern**
```dockerfile
FROM mcr.microsoft.com/dotnet/sdk:10.0
WORKDIR /app
COPY . .
RUN dotnet publish -c Release -o /app/publish
ENTRYPOINT ["dotnet", "MyApp.dll"]
# Image includes full SDK (~900MB)
```

**Good Pattern**
```dockerfile
# Build stage
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src
COPY ["MyApp.csproj", "."]
RUN dotnet restore
COPY . .
RUN dotnet publish -c Release -o /app/publish --no-restore

# Runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS runtime
WORKDIR /app
COPY --from=build /app/publish .
EXPOSE 8080
ENTRYPOINT ["dotnet", "MyApp.dll"]
# Final image is ~200MB
```

---

## CS-DOCKER-002 — Health Check in Dockerfile
**Severity: Major**

**Rule**
Dockerfiles MUST include HEALTHCHECK instruction for orchestrator health monitoring.

**Bad Pattern**
```dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:10.0
COPY --from=build /app/publish .
ENTRYPOINT ["dotnet", "MyApp.dll"]
# No health check - orchestrator can't detect unhealthy containers
```

**Good Pattern**
```dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:10.0
COPY --from=build /app/publish .

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

EXPOSE 8080
ENTRYPOINT ["dotnet", "MyApp.dll"]
```

---

## CS-DOCKER-003 — Docker Compose Service Naming
**Severity: Major**

**Rule**
Docker Compose services MUST use lowercase kebab-case names.

**Rationale**
Consistent naming enables predictable DNS resolution within Docker networks.

**Bad Pattern**
```yaml
services:
  MyApp_API:
  userService:
  ContentAPI:
```

**Good Pattern**
```yaml
services:
  my-app-api:
  user-service:
  content-api:
```

---

## CS-DOCKER-004 — Local Development Emulators
**Severity: Major**

**Rule**
Docker Compose MUST include emulators for cloud services in development.

**Rationale**
Developers should not need cloud subscriptions to run the application locally.

**Bad Pattern**
```yaml
# Requires real Azure subscription for local dev
services:
  api:
    environment:
      - AZURE_STORAGE_CONNECTION=DefaultEndpointsProtocol=https;AccountName=...
```

**Good Pattern**
```yaml
services:
  # Azure Storage emulator
  storage:
    image: mcr.microsoft.com/azure-storage/azurite
    ports:
      - "10000:10000"  # Blob
      - "10001:10001"  # Queue
      - "10002:10002"  # Table

  # Azure Service Bus emulator
  servicebus:
    image: mcr.microsoft.com/azure-messaging/servicebus-emulator
    ports:
      - "5672:5672"

  # Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  # SQL Server
  db:
    image: mcr.microsoft.com/mssql/server:2022-latest
    environment:
      - ACCEPT_EULA=Y
      - MSSQL_SA_PASSWORD=${DB_PASSWORD}
```

---

## CS-DOCKER-005 — Environment-Specific Overrides
**Severity: Major**

**Rule**
Development-specific settings MUST be in `docker-compose.override.yml`, not the base file.

**Rationale**
Base compose file should be environment-agnostic. Overrides customize for local development.

**Good Pattern**
```yaml
# docker-compose.yml - base config (production-like)
services:
  api:
    image: myregistry/my-api:${TAG:-latest}
    environment:
      - ASPNETCORE_ENVIRONMENT=Production

# docker-compose.override.yml - dev overrides (auto-loaded)
services:
  api:
    build:
      context: .
      dockerfile: src/MyApi/Dockerfile
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
      - ASPNETCORE_URLS=http://+:8080
    ports:
      - "8080:8080"
    volumes:
      - ./src:/app/src:ro  # Hot reload
```
