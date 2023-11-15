    def wrapper(*args, **kwargs):
      if jax.core.debug_state.check_leaks:
        return f(*args, **kwargs)
      else:
        return cached(bool(config.x64_enabled), *args, **kwargs)