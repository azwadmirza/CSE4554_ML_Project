    def _is_valid(self, *args, **kwargs):
        """Checks whether the supplied file can be read by this frontend.
        """
        warn_h5py(args[0])
        try:
            f = h5.File(args[0], "r")
        except (IOError, OSError, ImportError):
            return False

        requirements = ["openPMD", "basePath", "meshesPath", "particlesPath"]
        attrs = list(f["/"].attrs.keys())
        for i in requirements:
            if i not in attrs:
                f.close()
                return False

        known_versions = [StrictVersion("1.0.0"),
                          StrictVersion("1.0.1")]
        if StrictVersion(f.attrs["openPMD"].decode()) in known_versions:
            f.close()
            return True
        else:
            f.close()
            return False