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
  _x64_state = config.FLAGS.jax_enable_x64
  config.update('jax_enable_x64', True)
  try:
    yield
  finally:
    config.update('jax_enable_x64', _x64_state)