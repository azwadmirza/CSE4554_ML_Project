  def get_jax_enable_x64():
    """Returns the value of the flag after GoogleInit.

    We must wait until flags have been parsed (in particular for top-level
    functions decorated with jax.jit), so we delay inspecting the value
    of the jax_enable_x64 flag until JIT time.
    """
    return config.x64_enabled