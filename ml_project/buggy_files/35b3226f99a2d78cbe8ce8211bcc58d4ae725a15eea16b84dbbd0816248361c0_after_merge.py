  def x64_enabled(self):
   if lib._xla_extension_version >= 4:
     if lib.jax_jit.get_enable_x64() is None:
       lib.jax_jit.set_enable_x64(bool(self.read('jax_enable_x64')))
     return lib.jax_jit.get_enable_x64()
   else:
     # TODO(jakevdp): Remove when minimum jaxlib is has extension version 4
     if self._thread_local_state.enable_x64 is None:
       self._thread_local_state.enable_x64 = bool(self.read('jax_enable_x64'))
     return self._thread_local_state.enable_x64