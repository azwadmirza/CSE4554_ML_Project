def get_builder(*args, **kwargs):
    '''Intelligently returns an appropriate builder instance'''

    if sys.platform == "win32":
        from .windows import WindowsBuilder
        cls = WindowsBuilder
    elif sys.platform == "darwin":
        from .macos import MacOSBuilder
        cls = MacOSBuilder
    elif sys.platform == "linux":
        from ._external import distro
        dist_id, dist_version, dist_codename = distro.linux_distribution(
            full_distribution_name=False)
        if dist_id == "debian" and (dist_codename == "stretch" or
                                    dist_codename == "sid" or dist_version == "testing"):
            from .debian import DebianStretchBuilder
            cls = DebianStretchBuilder
        elif dist_id == "ubuntu":
            from .debian import UbuntuXenialBuilder
            cls = UbuntuXenialBuilder
        elif dist_id == "arch":
            from .archlinux import ArchLinuxBuilder
            cls = ArchLinuxBuilder
        else:
            from .linux import LinuxStaticBuilder
            cls = LinuxStaticBuilder
    else:
        raise BuilderException("Unsupported sys.platform value"
                               "'{}'".format(sys.platform))
    return cls(*args, **kwargs)