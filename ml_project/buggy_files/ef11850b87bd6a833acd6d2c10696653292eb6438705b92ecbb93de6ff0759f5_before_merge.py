def LIBC():
    """The platform dependent libc implementation."""
    if ON_DARWIN:
        libc = ctypes.CDLL(ctypes.util.find_library("c"))
    elif ON_CYGWIN:
        libc = ctypes.CDLL('cygwin1.dll')
    elif ON_MSYS:
        libc = ctypes.CDLL('msys-2.0.dll')
    elif ON_BSD:
        try:
            libc = ctypes.CDLL('libc.so')
        except AttributeError:
            libc = None
        except OSError:
            # OS X; can't use ctypes.util.find_library because that creates
            # a new process on Linux, which is undesirable.
            try:
                libc = ctypes.CDLL('libc.dylib')
            except OSError:
                libc = None
    elif ON_POSIX:
        try:
            libc = ctypes.CDLL('libc.so')
        except AttributeError:
            libc = None
        except OSError:
            # Debian and derivatives do the wrong thing because /usr/lib/libc.so
            # is a GNU ld script rather than an ELF object. To get around this, we
            # have to be more specific.
            # We don't want to use ctypes.util.find_library because that creates a
            # new process on Linux. We also don't want to try too hard because at
            # this point we're already pretty sure this isn't Linux.
            try:
                libc = ctypes.CDLL('libc.so.6')
            except OSError:
                libc = None
        if not hasattr(libc, 'sysinfo'):
            # Not Linux.
            libc = None
    elif ON_WINDOWS:
        if hasattr(ctypes, 'windll') and hasattr(ctypes.windll, 'kernel32'):
            libc = ctypes.windll.kernel32
        else:
            try:
                # Windows CE uses the cdecl calling convention.
                libc = ctypes.CDLL('coredll.lib')
            except (AttributeError, OSError):
                libc = None
    elif ON_BEOS:
        libc = ctypes.CDLL('libroot.so')
    else:
        libc = None
    return libc