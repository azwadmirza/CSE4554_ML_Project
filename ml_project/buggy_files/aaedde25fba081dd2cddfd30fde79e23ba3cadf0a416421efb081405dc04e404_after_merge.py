  def wrapper(*args, **kwargs):
    return memoized(bool(config.x64_enabled), *args, **kwargs)