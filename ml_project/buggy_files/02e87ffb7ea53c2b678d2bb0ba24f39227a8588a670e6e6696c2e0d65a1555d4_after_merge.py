    def core():
        shutting_down = utils.shutting_down  # early bind

        def module_unload(handle):
            # If we are not shutting down, we must be called due to
            # Context.reset() of Context.unload_module().  Both must have
            # cleared the module reference from the context.
            assert shutting_down() or handle.value not in modules
            driver.cuModuleUnload(handle)

        if dealloc is not None:
            dealloc.add_item(module_unload, handle)
        else:
            # Check the impossible case.
            assert shutting_down(), (
                "dealloc is None but interpreter is not being shutdown!"
            )