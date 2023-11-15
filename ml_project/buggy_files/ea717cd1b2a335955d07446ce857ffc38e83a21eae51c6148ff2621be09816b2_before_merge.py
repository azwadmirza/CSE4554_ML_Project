        def cleanup():
            if modules:
                del modules[handle.value]
            driver.cuModuleUnload(handle)