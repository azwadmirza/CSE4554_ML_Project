def is_manylinux1_compatible():
    # Only Linux, and only x86-64 / i686
    if get_platform() not in {"linux_x86_64", "linux_i686"}:
        return False

    # Check for presence of _manylinux module
    try:
        import _manylinux
        return bool(_manylinux.manylinux1_compatible)
    except (ImportError, AttributeError):
        # Fall through to heuristic check below
        pass

    # Check glibc version. CentOS 5 uses glibc 2.5.
    return pipenv.patched.notpip._internal.utils.glibc.have_compatible_glibc(2, 5)