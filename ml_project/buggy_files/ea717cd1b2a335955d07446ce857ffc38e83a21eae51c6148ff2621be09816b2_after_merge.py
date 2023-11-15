        def cleanup():
            # All modules are owned by their parent Context.
            # A Module is either released by a call to
            # Context.unload_module, which clear the handle (pointer) mapping
            # (checked by the following assertion), or, by Context.reset().
            # Both releases the sole reference to the Module and trigger the
            # finalizer for the Module instance.  The actual call to
            # cuModuleUnload is deferred to the trashing service to avoid
            # further corruption of the CUDA context if a fatal error has
            # occurred in the CUDA driver.
            assert handle.value not in modules
            driver.cuModuleUnload(handle)