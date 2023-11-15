def enable_x64():
  """Experimental context manager to temporarily enable X64 mode.

  Usage::

    >>> import jax.numpy as jnp
    >>> with enable_x64():
    ...   print(jnp.arange(10.0).dtype)
    ...
    float64

  See Also
  --------
  jax.experimental.disable_x64 :  temporarily disable X64 mode.
  """
  _x64_state = config.x64_enabled
  config._set_x64_enabled(True)
  try:
    yield
  finally:
    config._set_x64_enabled(_x64_state)