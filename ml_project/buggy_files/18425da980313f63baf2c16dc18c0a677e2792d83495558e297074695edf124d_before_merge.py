def cache(max_size=4096):
  def wrap(f):
    @functools.lru_cache(max_size)
    def cached(_, *args, **kwargs):
      return f(*args, **kwargs)

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
      if jax.core.debug_state.check_leaks:
        return f(*args, **kwargs)
      else:
        return cached(bool(FLAGS.jax_enable_x64), *args, **kwargs)

    wrapper.cache_clear = cached.cache_clear
    wrapper.cache_info = cached.cache_info
    return wrapper
  return wrap