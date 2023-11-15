    def _detect_crayos_version(cls):
        if os.path.isfile(_cle_release_file):
            release_attrs = read_cle_release_file()
            v = spack.version.Version(release_attrs['RELEASE'])
            return v[0]
        elif os.path.isfile(_clerelease_file):
            v = read_clerelease_file()
            return spack.version.Version(v)[0]
        else:
            raise spack.error.UnsupportedPlatformError(
                'Unable to detect Cray OS version')