def memoize(f):
  @functools.lru_cache(None)
  def memoized(_, *args, **kwargs):
    return f(*args, **kwargs)

  @functools.wraps(f)
  def wrapper(*args, **kwargs):
    return memoized(bool(FLAGS.jax_enable_x64), *args, **kwargs)

  wrapper.cache_clear = memoized.cache_clear
  wrapper.cache_info = memoized.cache_info
  return wrapper