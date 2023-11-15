def memoize(f):
  @functools.lru_cache(None)
  def memoized(_, *args, **kwargs):
    return f(*args, **kwargs)

  @functools.wraps(f)
  def wrapper(*args, **kwargs):
    return memoized(bool(config.x64_enabled), *args, **kwargs)

  wrapper.cache_clear = memoized.cache_clear
  wrapper.cache_info = memoized.cache_info
  return wrapper