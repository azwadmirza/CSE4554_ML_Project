    def _reflink_darwin(src, dst):
        import ctypes

        LIBC = "libc.dylib"
        LIBC_FALLBACK = "/usr/lib/libSystem.dylib"
        try:
            clib = ctypes.CDLL(LIBC)
        except OSError as exc:
            logger.debug(
                "unable to access '{}' (errno '{}'). "
                "Falling back to '{}'.".format(LIBC, exc.errno, LIBC_FALLBACK)
            )
            if exc.errno != errno.ENOENT:
                raise
            # NOTE: trying to bypass System Integrity Protection (SIP)
            clib = ctypes.CDLL(LIBC_FALLBACK)

        if not hasattr(clib, "clonefile"):
            return -1

        clonefile = clib.clonefile
        clonefile.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
        clonefile.restype = ctypes.c_int

        return clonefile(
            ctypes.c_char_p(src.encode("utf-8")),
            ctypes.c_char_p(dst.encode("utf-8")),
            ctypes.c_int(0),
        )