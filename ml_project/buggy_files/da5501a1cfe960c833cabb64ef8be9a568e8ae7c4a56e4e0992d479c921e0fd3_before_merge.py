def _module_finalizer(context, handle):
    trashing = context.trashing
    modules = context.modules

    def core():
        def cleanup():
            if modules:
                del modules[handle.value]
            driver.cuModuleUnload(handle)

        trashing.add_trash(cleanup)

    return core