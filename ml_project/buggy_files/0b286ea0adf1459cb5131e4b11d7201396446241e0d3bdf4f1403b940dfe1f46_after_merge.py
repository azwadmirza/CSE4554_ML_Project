def _get_lib_name(lib, add_extension_suffix):
    """
    Helper function to get an architecture and Python version specific library
    filename.

    :type add_extension_suffix: bool
    :param add_extension_suffix: Numpy distutils adds a suffix to
        the filename we specify to build internally (as specified by Python
        builtin `sysconfig.get_config_var("EXT_SUFFIX")`. So when loading the
        file we have to add this suffix, but not during building.
    """
    # our custom defined part of the extension filename
    libname = "lib%s_%s_%s_py%s" % (
        lib, platform.system(), platform.architecture()[0],
        ''.join([str(i) for i in platform.python_version_tuple()[:2]]))
    libname = cleanse_pymodule_filename(libname)
    # numpy distutils adds extension suffix by itself during build (#771, #755)
    if add_extension_suffix:
        # append any extension suffix defined by Python for current platform,
        # but strip ".so"
        ext_suffix = sysconfig.get_config_var("EXT_SUFFIX")
        if ext_suffix:
            if ext_suffix.endswith(".so"):
                ext_suffix = ext_suffix[:-3]
            libname = libname + ext_suffix
    return libname