    def _is_valid(self, *args, **kwargs):
        """Checks whether the supplied file can be read by this frontend.
        """
        warn_h5py(args[0])
        try:
            with h5.File(args[0], "r") as f:
                attrs = list(f["/"].attrs.keys())
                for i in opmd_required_attributes:
                    if i not in attrs:
                        return False

                if StrictVersion(f.attrs["openPMD"].decode()) not in ompd_known_versions:
                    return False

                if f.attrs["iterationEncoding"].decode() == "fileBased":
                    return True

                return False
        except (IOError, OSError, ImportError):
            return False