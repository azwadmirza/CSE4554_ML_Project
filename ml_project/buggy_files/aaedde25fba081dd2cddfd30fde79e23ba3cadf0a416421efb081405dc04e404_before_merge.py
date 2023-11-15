  def wrapper(*args, **kwargs):
    return memoized(bool(FLAGS.jax_enable_x64), *args, **kwargs)