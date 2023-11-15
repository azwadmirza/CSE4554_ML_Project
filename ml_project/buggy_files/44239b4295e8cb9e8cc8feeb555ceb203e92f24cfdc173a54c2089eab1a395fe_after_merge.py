def catch_error(exc):
    """Return true if exception exc should be caught"""
    for exception_class in (rpath.SkipFileException, rpath.RPathException,
                            librsync.librsyncError, C.UnknownFileTypeError,
                            zlib.error):
        if isinstance(exc, exception_class):
            return 1
    if (isinstance(exc, EnvironmentError)
            # the invalid mode shows up in backups of /proc for some reason
            and ('invalid mode: rb' in str(exc)
                 or 'Not a gzipped file' in str(exc)
                 or exc.errno in _robust_errno_list)):
        return 1
    return 0