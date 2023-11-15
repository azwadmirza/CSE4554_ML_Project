  def _set_x64_enabled(self, state):
    self._thread_local_state.enable_x64 = bool(state)