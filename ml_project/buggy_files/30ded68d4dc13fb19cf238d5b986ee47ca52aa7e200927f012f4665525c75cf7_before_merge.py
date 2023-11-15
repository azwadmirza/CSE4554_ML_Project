    async def wrapper(*args, **kwargs):
        key = tuple([args, tuple([tuple([k, kwargs[k]]) for k in kwargs])])
        cache[key] = cache.get(key) or asyncio.create_task(async_fn(*args, **kwargs))
        try:
            return await cache[key]
        finally:
            cache.pop(key, None)