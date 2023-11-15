    def wrapper(*args, **kwargs):
      if jax.core.debug_state.check_leaks:
        return f(*args, **kwargs)
      else:
        return cached(bool(FLAGS.jax_enable_x64), *args, **kwargs)