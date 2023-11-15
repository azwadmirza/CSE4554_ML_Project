def get_system_paths():
    """Return paths of system libraries"""
    paths = []
    # This prioritizes system libraries over
    # the Lutris and Steam runtimes.
    for lib_paths in LINUX_SYSTEM.iter_lib_folders():
        for index, _arch in enumerate(LINUX_SYSTEM.runtime_architectures):
            paths.append(lib_paths[index])
    return paths