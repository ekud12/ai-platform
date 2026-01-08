using AIPlatform.SimpleCache.Infrastructure.Interfaces;
using AIPlatform.SimpleCache.Infrastructure.Services;
using Microsoft.Extensions.DependencyInjection.Extensions;

namespace AIPlatform.SimpleCache.Infrastructure.Extensions;

/// <summary>
/// Extension methods for setting up cache services in an <see cref="IServiceCollection"/>.
/// </summary>
public static class ServiceCollectionExtensions
{
    /// <summary>
    /// Adds memory cache infrastructure services to the specified <see cref="IServiceCollection"/>.
    /// </summary>
    /// <param name="services">The <see cref="IServiceCollection"/> to add services to.</param>
    /// <returns>The <see cref="IServiceCollection"/> so that additional calls can be chained.</returns>
    /// <exception cref="ArgumentNullException">Thrown when <paramref name="services"/> is null.</exception>
    public static IServiceCollection AddSimpleCache(this IServiceCollection services)
    {
        ArgumentNullException.ThrowIfNull(services);

        // Register TimeProvider if not already present (CS-PLAT-001)
        services.TryAddSingleton(TimeProvider.System);

        // Register standard MemoryCache
        services.AddMemoryCache();

        // Register the cache service
        services.AddSingleton<ICacheService, MemoryCacheService>();

        return services;
    }
}