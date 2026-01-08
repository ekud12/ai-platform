using AIPlatform.SimpleCache.Infrastructure.Interfaces;

namespace AIPlatform.SimpleCache.Infrastructure.Services;

/// <summary>
/// Implementation of <see cref="ICacheService"/> using <see cref="IMemoryCache"/>.
/// </summary>
/// <remarks>
/// Initializes a new instance of the <see cref="MemoryCacheService"/> class.
/// </remarks>
/// <param name="memoryCache">The memory cache.</param>
public sealed class MemoryCacheService(IMemoryCache memoryCache) : ICacheService
{
    private readonly IMemoryCache _memoryCache = memoryCache;

    /// <inheritdoc />
    public ValueTask<T?> GetAsync<T>(string key, CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(key);

        return new ValueTask<T?>(_memoryCache.Get<T>(key));
    }

    /// <inheritdoc />
    public ValueTask SetAsync<T>(string key, T value, TimeSpan? expiration = null, CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(key);

        var options = new MemoryCacheEntryOptions();
        if (expiration.HasValue)
        {
            options.SetAbsoluteExpiration(expiration.Value);
        }

        _memoryCache.Set(key, value, options);
        return ValueTask.CompletedTask;
    }

    /// <inheritdoc />
    public ValueTask RemoveAsync(string key, CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(key);

        _memoryCache.Remove(key);
        return ValueTask.CompletedTask;
    }
}
