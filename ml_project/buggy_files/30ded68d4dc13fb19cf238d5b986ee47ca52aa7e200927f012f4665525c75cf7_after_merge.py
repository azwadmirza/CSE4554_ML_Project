    def wrapper(async_fn):

        @functools.wraps(async_fn)
        async def _inner(*args, **kwargs):
            key = tuple([args, tuple([tuple([k, kwargs[k]]) for k in kwargs])])
            if key in lru_cache:
                return lru_cache.get(key)

            concurrent_cache[key] = concurrent_cache.get(key) or asyncio.create_task(async_fn(*args, **kwargs))

            try:
                result = await concurrent_cache[key]
                lru_cache.set(key, result)
                return result
            finally:
                concurrent_cache.pop(key, None)
        return _inner