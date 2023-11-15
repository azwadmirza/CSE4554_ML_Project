    def _update_package_cache(self):
        if not self.package_caching or \
                not config.cache_packages_path or \
                not config.write_package_cache or \
                not self.success:
            return

        # see PackageCache.add_variants_async
        if not system.is_production_rez_install:
            return

        pkgcache = PackageCache(config.cache_packages_path)
        pkgcache.add_variants_async(self.resolved_packages)