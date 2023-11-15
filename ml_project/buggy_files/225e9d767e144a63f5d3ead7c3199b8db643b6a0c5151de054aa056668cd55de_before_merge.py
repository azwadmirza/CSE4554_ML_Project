    def _detect_crayos_version(cls):
        release_attrs = read_cle_release_file()
        v = spack.version.Version(release_attrs['RELEASE'])
        return v[0]