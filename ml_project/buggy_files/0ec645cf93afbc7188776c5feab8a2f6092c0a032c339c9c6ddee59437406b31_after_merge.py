    def execute(self):
        # I hate inline imports, but I guess it's ok since we're importing from the conda.core
        # The alternative is passing the the classes to ExtractPackageAction __init__
        from .package_cache import PackageCache, PackageCacheEntry
        log.trace("extracting %s => %s", self.source_full_path, self.target_full_path)

        if lexists(self.hold_path):
            rm_rf(self.hold_path)
        if lexists(self.target_full_path):
            try:
                backoff_rename(self.target_full_path, self.hold_path)
            except (IOError, OSError) as e:
                if e.errno == EXDEV:
                    # OSError(18, 'Invalid cross-device link')
                    # https://github.com/docker/docker/issues/25409
                    # ignore, but we won't be able to roll back
                    log.debug("Invalid cross-device link on rename %s => %s",
                              self.target_full_path, self.hold_path)
                    rm_rf(self.target_full_path)
                else:
                    raise
        extract_tarball(self.source_full_path, self.target_full_path)

        target_package_cache = PackageCache(self.target_pkgs_dir)

        recorded_url = target_package_cache.urls_data.get_url(self.source_full_path)
        dist = Dist(recorded_url) if recorded_url else Dist(path_to_url(self.source_full_path))
        package_cache_entry = PackageCacheEntry.make_legacy(self.target_pkgs_dir, dist)
        target_package_cache[package_cache_entry.dist] = package_cache_entry