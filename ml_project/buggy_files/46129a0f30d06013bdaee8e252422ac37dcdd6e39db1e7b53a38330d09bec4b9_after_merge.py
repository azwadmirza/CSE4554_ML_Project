    def _get_or_create_context_uncached(self, devnum):
        """See also ``get_or_create_context(devnum)``.
        This version does not read the cache.
        """
        with self._lock:
            # Try to get the active context in the CUDA stack or
            # activate GPU-0 with the primary context
            with driver.get_active_context() as ac:
                if not ac:
                    return self._activate_context_for(0)
                else:
                    # Get primary context for the active device
                    ctx = self.gpus[ac.devnum].get_primary_context()
                    # Is active context the primary context?
                    if ctx.handle.value != ac.context_handle.value:
                        msg = ('Numba cannot operate on non-primary'
                               ' CUDA context {:x}')
                        raise RuntimeError(msg.format(ac.context_handle.value))
                    # Ensure the context is ready
                    ctx.prepare_for_use()
                return ctx