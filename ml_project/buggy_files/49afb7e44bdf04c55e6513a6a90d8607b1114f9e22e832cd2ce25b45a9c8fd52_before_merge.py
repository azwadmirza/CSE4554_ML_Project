    def core():
        def cleanup():
            if modules:
                del modules[handle.value]
            driver.cuModuleUnload(handle)

        trashing.add_trash(cleanup)