        async def _inner(*args, **kwargs) -> typing.Any:
            loop = asyncio.get_running_loop()
            now = loop.time()
            key = tuple([args, tuple([tuple([k, kwargs[k]]) for k in kwargs])])
            if key in cache and (now - cache[key][1] < duration):
                return cache[key][0]
            to_cache = await fn(*args, **kwargs)
            cache[key] = to_cache, now
            return to_cache