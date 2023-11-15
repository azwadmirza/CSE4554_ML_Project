  def _set_x64_enabled(self, state):
    if lib._xla_extension_version >= 4:
      lib.jax_jit.set_enable_x64(bool(state))
    else:
      # TODO(jakevdp): Remove when minimum jaxlib is has extension version 4
      self._thread_local_state.enable_x64 = bool(state)