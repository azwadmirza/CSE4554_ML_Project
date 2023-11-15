def _find_libcrypto():
    """
    Find the path (or return the short name) of libcrypto.
    """
    if sys.platform.startswith("win"):
        lib = "libeay32"
    elif salt.utils.platform.is_darwin():
        # will look for several different location on the system,
        # Search in the following order. salts pkg, homebrew, macports, finnally
        # system.
        # look in salts pkg install location.
        lib = glob.glob("/opt/salt/lib/libcrypto.dylib")
        # Find library symlinks in Homebrew locations.
        lib = lib or glob.glob("/usr/local/opt/openssl/lib/libcrypto.dylib")
        lib = lib or glob.glob("/usr/local/opt/openssl@*/lib/libcrypto.dylib")
        # look in macports.
        lib = lib or glob.glob("/opt/local/lib/libcrypto.dylib")
        # check if 10.15, regular libcrypto.dylib is just a false pointer.
        if platform.mac_ver()[0].split(".")[:2] == ["10", "15"]:
            lib = lib or glob.glob("/usr/lib/libcrypto.*.dylib")
            lib = list(reversed(sorted(lib)))
        # last but not least all the other macOS versions should work here.
        # including Big Sur.
        lib = lib[0] if lib else "/usr/lib/libcrypto.dylib"
    elif getattr(sys, "frozen", False) and salt.utils.platform.is_smartos():
        lib = glob.glob(os.path.join(os.path.dirname(sys.executable), "libcrypto.so*"))
        lib = lib[0] if lib else None
    else:
        lib = ctypes.util.find_library("crypto")
        if not lib:
            if salt.utils.platform.is_sunos():
                # Solaris-like distribution that use pkgsrc have libraries
                # in a non standard location.
                # (SmartOS, OmniOS, OpenIndiana, ...)
                # This could be /opt/tools/lib (Global Zone) or
                # /opt/local/lib (non-Global Zone), thus the two checks
                # below
                lib = glob.glob("/opt/local/lib/libcrypto.so*")
                lib = lib or glob.glob("/opt/tools/lib/libcrypto.so*")
                lib = lib[0] if lib else None
            elif salt.utils.platform.is_aix():
                if os.path.isdir("/opt/salt/lib"):
                    # preference for Salt installed fileset
                    lib = glob.glob("/opt/salt/lib/libcrypto.so*")
                else:
                    lib = glob.glob("/opt/freeware/lib/libcrypto.so*")
                lib = lib[0] if lib else None
    if not lib:
        raise OSError("Cannot locate OpenSSL libcrypto")
    return lib