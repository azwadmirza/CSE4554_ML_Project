    def cache_distribution(cls, zf, source, target_dir):
        # type: (ZipFile, str, str) -> Distribution
        """Possibly cache a wheel from within a zipfile into `target_dir`.

        Given a zipfile handle and a source path prefix corresponding to a wheel install embedded within
        that zip, maybe extract the wheel install into the target cache and then return a distribution
        from the cache.

        :param zf: An open zip file (a zipped pex).
        :param source: The path prefix of a wheel install embedded in the zip file.
        :param target_dir: The directory to cache the distribution in if not already cached.
        :returns: The cached distribution.
        """
        with atomic_directory(target_dir, source=source, exclusive=True) as target_dir_tmp:
            if target_dir_tmp is None:
                TRACER.log("Using cached {}".format(target_dir))
            else:
                with TRACER.timed("Caching {}:{} in {}".format(zf.filename, source, target_dir)):
                    for name in zf.namelist():
                        if name.startswith(source) and not name.endswith("/"):
                            zf.extract(name, target_dir_tmp)

        dist = DistributionHelper.distribution_from_path(target_dir)
        assert dist is not None, "Failed to cache distribution: {} ".format(source)
        return dist