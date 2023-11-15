def _load_libcrypto():
    '''
    Load OpenSSL libcrypto
    '''
    if sys.platform.startswith('win'):
        # cdll.LoadLibrary on windows requires an 'str' argument
        return cdll.LoadLibrary(str('libeay32'))  # future lint: disable=blacklisted-function
    elif getattr(sys, 'frozen', False) and salt.utils.platform.is_smartos():
        return cdll.LoadLibrary(glob.glob(os.path.join(
            os.path.dirname(sys.executable),
            'libcrypto.so*'))[0])
    else:
        lib = find_library('crypto')
        if not lib and salt.utils.platform.is_sunos():
            # Solaris-like distribution that use pkgsrc have
            # libraries in a non standard location.
            # (SmartOS, OmniOS, OpenIndiana, ...)
            # This could be /opt/tools/lib (Global Zone)
            # or /opt/local/lib (non-Global Zone), thus the
            # two checks below
            lib = glob.glob('/opt/local/lib/libcrypto.so*') + glob.glob('/opt/tools/lib/libcrypto.so*')
            lib = lib[0] if len(lib) > 0 else None
        if not lib and salt.utils.platform.is_aix():
            if os.path.isdir('/opt/salt/lib'):
                # preference for Salt installed fileset
                lib = glob.glob('/opt/salt/lib/libcrypto.so*')
                lib = lib[0] if len(lib) > 0 else None
            else:
                lib = glob.glob('/opt/freeware/lib/libcrypto.so*')
                lib = lib[0] if len(lib) > 0 else None
        if lib:
            return cdll.LoadLibrary(lib)
        raise OSError('Cannot locate OpenSSL libcrypto')