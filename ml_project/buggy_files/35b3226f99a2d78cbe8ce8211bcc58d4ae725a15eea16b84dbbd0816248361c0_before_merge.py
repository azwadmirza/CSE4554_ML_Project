  def x64_enabled(self):
    if self._thread_local_state.enable_x64 is None:
      self._thread_local_state.enable_x64 = bool(self.read('jax_enable_x64'))
    return self._thread_local_state.enable_x64