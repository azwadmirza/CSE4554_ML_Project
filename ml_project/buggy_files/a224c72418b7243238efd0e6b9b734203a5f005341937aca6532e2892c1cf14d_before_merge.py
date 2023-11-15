def _configure_syspath():
    sys.path.insert(1, _lib_location())
    sys.path.insert(1, _ext_lib_location())